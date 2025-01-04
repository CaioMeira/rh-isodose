#! -*- encoding:utf-8 -*-
import matplotlib 
matplotlib.use('Agg')
import numpy as np
from lib.dicompylercore import dicomparser
import os
import math
import matplotlib.pyplot as plt
import matplotlib.path as path

def rotate(x,y,xo,yo,theta): #rotate x,y around xo,yo by theta (rad)
    xr = math.cos(theta) * (x-xo) - math.sin(theta) * (y-yo) + xo
    yr = math.sin(theta) * (x-xo) + math.cos(theta) * (y-yo) + yo
    return [ xr, yr ]

def forceDicomparserObj(obj):
    if obj is not None:
        if isinstance(obj, dicomparser.DicomParser):
            return obj
        else:
            return dicomparser.DicomParser(obj)
    else:
        return None

def getUnusedKey(obj, key, base_key = 'Rtplan'):
    i = 1
    key = key if key else base_key
    newKey = key
    while newKey in obj:
        newKey = "%s_%d" % (key, i)
        i += 1
    return newKey

class Dose(object):
    def __init__(self, RTDose, RTPlans, Images, Isodoses):
        self.rtdose = forceDicomparserObj(RTDose)
        if RTPlans is None:
            self.rtplans = []
        else:
            self.rtplans = [forceDicomparserObj(RTPlan) for RTPlan in RTPlans]
        self.images = Images

        self.dpi = 100
        self._fig = None

        self._rxdose = 0
        if Isodoses is not None:
            self._rxdose = Isodoses['rxdose']
            self._isodoses = Isodoses['isodoses']
        
        self._base_levels = np.array([0.3, 0.5, 0.7, 0.8, 0.9, 0.95, 1])
        self._levels = None
        # jet colormap
        self._colors = [
            [0,0,131],
            [0,60,170],
            [5,255,255],
            [130,255,128],
            [255,255,0],
            [250,0,0],
            [128,0,0]
        ]

        self._doselut = None
        self._pixlut = None
        self._dosepixlut = None
        self._grid = None
        self._lastAxialDosepixlut = None

    def isclose(self, a, b, rel_tol=1e-09, abs_tol=0.0):
        return abs(a-b) <= max(rel_tol * max(abs(a), abs(b)), abs_tol)

    def _set_img_num(self, imagekey, imagenum):
        self._imagenum = int(imagenum)
        self._image = dicomparser.DicomParser(self.images[imagekey][self._imagenum])
        
        self.imdata = self._image.GetImageData()
        self._z = '%.2f' % self.imdata['position'][2]

        if self._fig == None:
            self._rows = self._image.ds.Rows
            self._columns = self._image.ds.Columns
            self._fig = plt.figure(figsize=(self._columns/self.dpi, self._rows/self.dpi), dpi=self.dpi)
            self._ax = self._fig.gca()

            self._ax.set_axis_off()
            self._ax.set_frame_on(False)
            self._ax.imshow(self._image.ds.pixel_array, alpha=0)

    def _GetDoseGrid(self, imagekey):       
        # # remover zeros do grid
        # masked_data = self.rtdose.GetDoseGrid(self._z)
        # return np.ma.masked_where(masked_data < 0.1, masked_data)

        # pixel_array = self.rtdose.ds.pixel_array * self.rtdose.ds.DoseGridScaling
        masked_data = []
        
        if imagekey != 'axial':
            pixel_array = self.rtdose.ds.pixel_array
           
            masked_data = [[]] * len(self.images[imagekey])
            if imagekey == 'sagittal':
                for i in range(pixel_array.shape[2]-1):
                    k = int(self._lastAxialDosepixlut[0][i])
                    k2 = int(self._lastAxialDosepixlut[0][i+1])
                    #interv = int(self._lastAxialDosepixlut[0][i+1]) - int(self._lastAxialDosepixlut[0][i])

                    if k2>len(self.images[imagekey]):
                        k2= len(self.images[imagekey])-1
                    interv = k2-k
                    aux = (pixel_array[:,:,i])
                    aux2 = (pixel_array[:,:,i+1])
                    masked_data[k] = aux
                    masked_data[k2] = aux2
                    j=1
                    while j<interv:
                        soma=(aux + aux2)/2
                        masked_data[int(self._lastAxialDosepixlut[0][i]+j)]=soma
                        aux=soma
                        j+=1
            else:
          
                for i in range(pixel_array.shape[1]-1):
                    #interv = int(self._lastAxialDosepixlut[0][i+1]) - int(self._lastAxialDosepixlut[0][i])
                    k = int(self._lastAxialDosepixlut[1][i])
                    k2 = int(self._lastAxialDosepixlut[1][i+1])
                    if k2>len(self.images[imagekey]):
                        k2= len(self.images[imagekey])-1
                    interv = k2-k
                    aux = (pixel_array[:,i,:])
                    aux2 = (pixel_array[:,i+1,:])
                    masked_data[k] = aux
                    masked_data[k2] = aux2
                    j=1
                    while j<interv:
                        soma=(aux + aux2)/2
                        masked_data[int(self._lastAxialDosepixlut[1][i]+j)]=soma
                        aux=soma
                        j+=1
                

            #for i in range(pixel_array.shape[2]):
            #    k = int(self._lastAxialDosepixlut[0][i])
            #    masked_data[k] = (pixel_array[:,:,i])
            
        # masked_data = np.ma.masked_where(masked_data < 0.1, masked_data)
        masked_data = np.array(masked_data)
        return masked_data
    
    def _GetDosePatientToPixelLUT(self,imagekey):
        # return self.rtdose.GetPatientToPixelLUT()

        spacing_dose = self.rtdose.ds.PixelSpacing
        di_dose = spacing_dose[0] #self.rtdose.ds.PixelSpacing[0]
        dj_dose = spacing_dose[1] #self.rtdose.ds.PixelSpacing[1]
        orientation_dose = self.rtdose.ds.ImageOrientationPatient
        position_dose = self.rtdose.ds.ImagePositionPatient

        m = np.matrix(
            [[orientation_dose[0]*di_dose, orientation_dose[3]*dj_dose, 0, position_dose[0]],
            [orientation_dose[1]*di_dose, orientation_dose[4]*dj_dose, 0, position_dose[1]],
            [orientation_dose[2]*di_dose, orientation_dose[5]*dj_dose, 0, position_dose[2]],
            [0, 0, 0, 1]])

        x = []
        y = []

        if self._lastAxialDosepixlut is None:
            for i in range(0, self.rtdose.ds.Columns):
                imat = m * np.matrix([[i], [0], [0], [1]])
                x.append(float(imat[0]))
            for j in range(0, self.rtdose.ds.Rows):
                jmat = m * np.matrix([[0], [j], [0], [1]])
                y.append(float(jmat[1]))
            return (np.array(x), np.array(y)) #doselut no viewer
        else:
            if imagekey == 'sagittal':
                k = int(self._lastAxialDosepixlut[0][0])
            else:
                k = int(self._lastAxialDosepixlut[1][0])
                
            for i in range( 0, len(self._grid[k]) ): 
                imat = m * np.matrix([[i], [0], [0], [1]])
                x.append(float(imat[0]))
                
            for j in range( 0, len(self._grid[k][1]) ): 
                jmat = m * np.matrix([[0], [j], [0], [1]])
                y.append(float(jmat[1]))
            return (np.array(x), np.array(y)) #GetPatientToPixelLUT

    def _getDoseGridPixelData(self, imagekey):
        # """Convert dosegrid data into pixel data using the dose to pixel LUT."""
        # x = []
        # y = []
        # # Determine if the patient is prone or supine
        # prone = -1 if 'p' in self.imdata['patientposition'].lower() else 1
        # feetfirst = -1 if 'ff' in self.imdata['patientposition'].lower() else 1
        # # Get the pixel spacing
        # spacing = self.imdata['pixelspacing']

        # # Transpose the dose grid LUT onto the image grid LUT
        # x = (np.array(self._doselut[0]) - self._pixlut[0][0]) * prone * feetfirst / spacing[0]
        # y = (np.array(self._doselut[1]) - self._pixlut[1][0]) * prone / spacing[1]
        # return (x, y)

        prone = -1 if 'p' in self._image.ds.PatientPosition.lower() else 1
        feetfirst = -1 if 'ff' in self._image.ds.PatientPosition.lower() else 1
        spacing = self._image.ds.PixelSpacing


        x = None
        y = None
        if imagekey == 'axial':
            x = (np.array(self._doselut[0]) - self._pixlut[0][0]) * prone * feetfirst / spacing[0]
            y = (np.array(self._doselut[1]) - self._pixlut[1][0]) * prone / spacing[1]
        else:
            if imagekey == 'sagittal':
                y_tmp = (np.array(self._doselut[0]) - self._pixlut[0][0]) * prone * feetfirst / spacing[0]
                x = (np.array(self._doselut[1]) - self._pixlut[1][0]) * prone / spacing[1]
       
                y = [ (i - y_tmp[0])  for i in y_tmp][::-1]
                y = y - (y[0] - self._image.ds.Rows)/2
            
                for i in range(0,len(y)):
                    if y[i] > self._image.ds.Rows:
                        y[i] = self._image.ds.Rows-1
                    elif y[i] <0:
                        y[i] = 0
                            
            else: 
                y_tmp = (np.array(self._doselut[0]) - self._pixlut[0][0]) * prone * feetfirst / spacing[0]
                x_tmp = (np.array(self._doselut[1]) - self._pixlut[1][0]) * prone / spacing[1]
                y = [ (i - y_tmp[0])  for i in y_tmp][::-1]
                x = [(i - x_tmp[0]) for i in x_tmp]
                
                y = y - (y[0] - self._image.ds.Rows)/2
                x = x - (x[-1] - self._image.ds.Columns)/2
                
                for i in range(0,len(y)):
                    if y[i] > self._image.ds.Rows:
                        y[i] = self._image.ds.Rows-1
                    elif y[i] <0:
                        y[i] = 0
                
        return (x, y)

    def _GetImagePatientToPixelLUT(self):
        # return self._image.GetPatientToPixelLUT()

        di = self._image.ds.PixelSpacing[0]
        dj = self._image.ds.PixelSpacing[1]
        orientation = self._image.ds.ImageOrientationPatient
        position = self._image.ds.ImagePositionPatient

        m = np.matrix(
            [[orientation[0]*di, orientation[3]*dj, 0, position[0]],
            [orientation[1]*di, orientation[4]*dj, 0, position[1]],
            [orientation[2]*di, orientation[5]*dj, 0, position[2]],
            [0, 0, 0, 1]])

        xi = []
        yi = []
        for i in range(0, self._image.ds.Columns):
            imat = m * np.matrix([[i], [0], [0], [1]])
            xi.append(float(imat[0]))
        for j in range(0, self._image.ds.Rows):
            jmat = m * np.matrix([[0], [j], [0], [1]])
            yi.append(float(jmat[1]))

        return (np.array(xi), np.array(yi))

    def _fix_segs(self, contour):
        ret = []
        segs = contour.allsegs
        kinds = contour.allkinds
        for i in range(len(segs)):
            ret.append([])
            for j in range(len(segs[i])):
                for k, coord in enumerate(segs[i][j]):
                    kind = kinds[i][j][k] if kinds is not None else None
                    if kind == path.Path.CLOSEPOLY:
                        ret[i].append('-')
                    elif k % 2 == 0:
                        ret[i].append(coord)
                # if kinds is None:
                #     ret[i].append('-')
                ret[i][-1] = '--'
        return np.array(ret)

    def _drawContour(self, imagekey):
        self._pixlut = self._GetImagePatientToPixelLUT()
        self._dosepixlut = self._getDoseGridPixelData(imagekey)

        grid = self._grid
        if imagekey == 'axial':
            grid = self.rtdose.GetDoseGrid(self._z)
        else:
            grid = np.array(grid[self._image.ds.InstanceNumber - 1])

        if grid.size == 0:
        # if len(grid) == 0:
            # print('grid size == 0')
            return {}
            
        max_grid = np.amax(grid)
        # if np.ma.is_masked(max_grid): # não tem curva
        if max_grid < 0.1:
            # print(imagekey, 'grid masked == 0')
            return {}

        # precisa de no min 2 levels pra plotar o contorno
        if max_grid < self._levels[1]:
            # print('max < levels', max_grid, self._levels[1])
            return {}

        # https://matplotlib.org/1.2.1/api/path_api.html#matplotlib.path.Path [allkinds]
        if imagekey == 'axial':
            X, Y = np.meshgrid(self._dosepixlut[0], self._dosepixlut[1])
        else:
            X, Y = np.meshgrid(self._dosepixlut[0], self._dosepixlut[1])

        try:
            contourf = self._ax.contourf(X, Y, grid, alpha=1, levels=self._levels)
            return self._fix_segs(contourf)
        except Exception as e:
            print(imagekey, X.shape, Y.shape, grid.shape)
            raise e

    def contour(self):
        scaling = self.rtdose.ds.DoseGridScaling * 100
        # scaling = 1
        self._levels = []
        for i, iso in self._isodoses.items():
            self._levels.append(iso['dose'] / scaling)
        max_v = self._levels[0]
        max_d = np.amax(self.rtdose.ds.pixel_array)
        max_d = max_v if max_d < max_v else max_d 
        self._levels.reverse()
        self._levels.append(max_d + 10 if self.isclose(max_v, max_d) else max_d)
           
        # usar threads? (from multiprocessing.pool import ThreadPool)
        # http://192.168.0.95:1515/notebooks/dicompyler/Baixando%20Imagens%20do%20PACS.ipynb
        # https://docs.python.org/3/library/multiprocessing.html
        all_contours = {
            'axial': {},
            'coronal': {},
            'sagittal': {}
        }
        keys = all_contours.keys()
        for key in keys:
            self._grid = self._GetDoseGrid(key)
            self._doselut = self._GetDosePatientToPixelLUT(key)

            for imagenum in self.images[key].keys():
                self._set_img_num(key, imagenum)
                ret = self._drawContour(key)
                if len(ret) > 0:
                    all_contours[key][imagenum] = ret
            
            if key == 'axial' and self._dosepixlut is not None:
                self._lastAxialDosepixlut = self._dosepixlut

        return {
            'contours': all_contours
        }
    
    def default_isodoses(self):
        scaling = self.rtdose.ds.DoseGridScaling * 100
        rxdose = np.amax(self.rtdose.ds.pixel_array) * scaling
        isodoses = []

        for i, level in enumerate(self._base_levels):
            isodoses.append({
                'id': level*100,
                'level': level,
                'dose': round(rxdose*level, 2),
                'color': self._colors[i]
            })
        return {
            'rxdose': rxdose,
            'isodoses': isodoses
        }

    def _getRefImg(self, z):
        lastDiff = float("inf")
        lastUid = None
        for uid, image in self.images.items():
            diff = abs(image.ds.ImagePositionPatient[2] - z)
            if diff < lastDiff:
                lastDiff = diff
                lastUid = uid
        return self.images[lastUid]

    def line_intersection(self, line1, line2):
        xdiff = (line1[0][0] - line1[1][0], line2[0][0] - line2[1][0])
        ydiff = (line1[0][1] - line1[1][1], line2[0][1] - line2[1][1])

        def det(a, b):
            return a[0] * b[1] - a[1] * b[0]

        div = det(xdiff, ydiff)
        if div == 0:
            raise Exception('lines do not intersect')

        d = (det(*line1), det(*line2))
        x = det(d, xdiff) / div
        y = det(d, ydiff) / div
        return x, y

    def closest(self, lst, K):
        return lst[min(range(len(lst)), key = lambda i: abs(lst[i]-K))] 
    
    def beam_lines(self):
        ret = {}
        for obj in self.rtplans:
            rtplan = obj.ds
            uid = rtplan.SOPInstanceUID
            ret[uid] = self._beam_lines(rtplan)
        return ret

    def _beam_lines(self, rtplan):
        # http://192.168.10.195:1515/notebooks/dicompyler/beamlines_demais_cortes.ipynb
        self.lastZ = None
        self.lastImg = None
        img_ref = {}
        slice_limits = []
        iso_points = []
        interseccent = []
        intersec1 = []
        ponto_plot1 = []
        intersec2 = []
        ponto_plot2 = []
        pontofiltro1 = []
        pontofiltro2 = []
        pontofiltro3 = []
        pontofiltro4 = []
        entrada_saida1=[]
        entrada_saida2=[]
        for i in range(0, len(rtplan.BeamSequence)):
            if rtplan.BeamSequence[i].TreatmentDeliveryType != "TREATMENT":
                continue
            
            ent_sai1 = []
            ent_sai2 = []

            (bx, by, bz) = rtplan.BeamSequence[i].ControlPointSequence[0].IsocenterPosition

            if self.lastZ is not None and self.isclose(self.lastZ, bz):
                image = self.lastImg
            else:
                image = self._getRefImg(bz)
                self.lastImg = image
                self.lastZ = bz

            _div = image.ds.Rows / 512
            
            (di, dj) = image.ds.PixelSpacing
            orientation = image.ds.ImageOrientationPatient
            position = image.ds.ImagePositionPatient

            bx = bx*_div
            by = by*_div

            di = di*_div
            dj = dj*_div

            orientation = [o * _div for o in orientation]
            position = [p * _div for p in position]

            Ix = ((bx - position[0]) / orientation[0] * di)*_div
            Iy = ((by - position[1]) / orientation[4] * dj)*_div
            Iz = float(bz)

            #print( bx,by,bz, '-', di,dj, '-', Ix,Iy, '-', orientation, '-', position )

            imgUid = image.ds.SOPInstanceUID
            if imgUid not in img_ref:
                img_ref[imgUid] = [Ix, Iy, Iz]

            if "SourceToSurfaceDistance" in rtplan.BeamSequence[i].ControlPointSequence[0]:
                ssd = rtplan.BeamSequence[i].ControlPointSequence[0].SourceToSurfaceDistance
            else:
                ssd = 100

            sad = rtplan.BeamSequence[i].SourceAxisDistance
            ssdp = (ssd - position[0]) / orientation[0] * di
            sadp = (sad - position[0]) / orientation[0] * di
            SDIF = sad - ssd
            SSD = ssdp

            gantry = rtplan.BeamSequence[i].ControlPointSequence[0].GantryAngle
            gantry_deg = gantry
            gantry_rad = math.radians(gantry)

            # x1,y1, x2,y2 abertura do jaw
            x1 = -(rtplan.BeamSequence[i].ControlPointSequence[0].BeamLimitingDevicePositionSequence[0].LeafJawPositions[0])*_div
            y1 = -(rtplan.BeamSequence[i].ControlPointSequence[0].BeamLimitingDevicePositionSequence[1].LeafJawPositions[0])*_div
             
            x2 = (rtplan.BeamSequence[i].ControlPointSequence[0].BeamLimitingDevicePositionSequence[0].LeafJawPositions[1])*_div
            y2 = (rtplan.BeamSequence[i].ControlPointSequence[0].BeamLimitingDevicePositionSequence[1].LeafJawPositions[1])*_div
            
            # passar a abertura pro tamanho da abertura da imagem
            cx1 = (x1 - position[0]) / orientation[0] * di
            cy1 = (y1 - position[1]) / orientation[4] * dj
            
            cx2 = (x2 - position[0]) / orientation[0] * di
            cy2 = (y2 - position[1]) / orientation[4] * dj

            # Tamanho do campo "em pixel"
            #c = 2 * (cx1 + cx2) * (cy1 + cy2) / (cx1 + cx2 + cy1 + cy2)
            
            #if ssdp >= sadp:
            #    c = c * ssdp / sadp

            # ABERTURA DOS CAMPOS COM RELAÇÃO AO ISOCENTRO    
            # - Se não tiver dando certo com cx1,cx2... fazer com c e descomentar em cima
            iso_point = img_ref[imgUid]
            iso_points.append(iso_point)
            DeviceAngle = rtplan.BeamSequence[i].ControlPointSequence[0].BeamLimitingDeviceAngle
            DeviceRotation = rtplan.BeamSequence[i].ControlPointSequence[0].BeamLimitingDeviceRotationDirection

            ##CASO TENHA GIRO NO COLIMADOR E INTERFIRA NO LIMITE TEM QUE CONSIDERAR ISSO EM CADA LIMITE##
            # if DeviceAngle == 0:
            #     cobertura1 = abs(iso_point[2] - cy2 / 10)
            #     cobertura2 = abs(iso_point[2] + cy1 / 10)
            # elif DeviceAngle == 180 and DeviceRotation == 'cw':
            #     cobertura1 = abs(iso_point[2] + cy2 / 10)
            #     cobertura2 = abs(iso_point[2] - cy1 / 10)
            # elif DeviceAngle == 90:
            #     cobertura1 = abs(iso_point[2] + cx1 / 10)
            #     cobertura2 = abs(iso_point[2] - cx2 / 10)
            # elif DeviceAngle == 270:
            #     cobertura1 = abs(iso_point[2] + cx2 / 10)
            #     cobertura2 = abs(iso_point[2] - cx1 / 10)
            # else:
            #     if DeviceRotation == 'cw':
            #         if DeviceAngle >= 0 and DeviceAngle < 90:
            #             cobertura1 = abs(iso_point[2] + math.sqrt((cx1/10)**2 + (cy2/10)**2))
            #             cobertura2 = abs(iso_point[2] - math.sqrt((cx2/10)**2 + (cy1/10)**2))
            #         elif DeviceAngle >= 90 and DeviceAngle < 180:
            #             cobertura1 = abs(iso_point[2] + math.sqrt((cx1/10)**2 + (cy1/10)**2))
            #             cobertura2 = abs(iso_point[2] - math.sqrt((cx2/10)**2 + (cy2/10)**2))
            #         elif DeviceAngle >= 180 and DeviceAngle < 270:
            #             cobertura1 = abs(iso_point[2] + math.sqrt((cx1/10)**2 + (cy2/10)**2))
            #             cobertura2 = abs(iso_point[2] - math.sqrt((cx2/10)**2 + (cy1/10)**2))
            #         else:
            #             cobertura1 = abs(iso_point[2] + math.sqrt((cx1/10)**2 + (cy1/10)**2))
            #             cobertura2 = abs(iso_point[2] - math.sqrt((cx2/10)**2 + (cy2/10)**2))
            #     else:
            #         if DeviceAngle >= 0 and DeviceAngle < 90:
            #             cobertura1=abs(iso_point[2] + math.sqrt((cx1/10)**2 + (cy2/10)**2))
            #             cobertura2=abs(iso_point[2] - math.sqrt((cx2/10)**2 + (cy1/10)**2))
            #         elif DeviceAngle >=90 and DeviceAngle < 180:
            #             cobertura1=abs(iso_point[2] + math.sqrt((cx2/10)**2 + (cy1/10)**2))
            #             cobertura2=abs(iso_point[2] - math.sqrt((cx1/10)**2 + (cy2/10)**2))
            #         elif DeviceAngle >=180 and DeviceAngle < 270:
            #             cobertura1=abs(iso_point[2] + math.sqrt((cx1/10)**2 + (cy1/10)**2))
            #             cobertura2=abs(iso_point[2] - math.sqrt((cx2/10)**2 + (cy2/10)**2))
            #         else:
            #             cobertura1=abs(iso_point[2] + math.sqrt((cx2/10)**2 + (cy2/10)**2))
            #             cobertura2=abs(iso_point[2] - math.sqrt((cx1/10)**2 + (cy1/10)**2))

            # slicecima = round(cobertura1)
            # slicebaixo = round(cobertura2)

            m = 3
            if (gantry >= 360-m or gantry <= 0+m) or (gantry >= 180-m and gantry <= 180+m):
                d1x = iso_point[0] - x1
                d1y = iso_point[1]
                d2x = iso_point[0] + x2
                d2y = iso_point[1]
            elif (gantry >= 90-m and gantry <= 90+m) or (gantry >= 270-m and gantry <= 270+m):
                d1x = iso_point[0]
                d1y = iso_point[1] + y1
                d2x = iso_point[0]
                d2y = iso_point[1] - y2
            else: 
                d1x = iso_point[0] - x1
                d1y = iso_point[1] + y1
                d2x = iso_point[0] + x2
                d2y = iso_point[1] - y2

            # PONTO EM QUE SE ESTENDE O CAMPO EM RELAÇÃO COM A ROTAÇÃO DO GANTRY 
            # - CAMPO.. SÃO LINHAS RETAS, CA.. SÃO OS CAMPOS COM DIVERGENCIA
            x = np.sin(gantry_rad) * SSD * _div
            y = np.cos(gantry_rad) * SSD * _div
            ponto = (iso_point[0] + x, iso_point[1] - y)
            
            campo1 = (d1x + x, d1y - y)
            campo2 = (d2x + x, d2y - y)
            
            # campo onde há intersecção - "reta perpendicular ao campo"
            x2 = np.sin(gantry_rad) * SDIF * _div
            y2 = np.cos(gantry_rad) * SDIF * _div
            
            ca1x = d1x + x2
            ca1y = d1y - y2
            ca2x = d2x + x2
            ca2y = d2y - y2

            # A RELAÇÃO ENTRE O EIXO VAI VARIAR SE VAI SOMAR OU SUBTRAIS X E Y
            if (gantry_deg >= 0 and gantry_deg < 90):
                ponto_plot2.append((d2x, d1y))
                ponto_plot1.append((d1x, d2y))
                
                camp11 = (ca1x, ca2y)
                camp22 = (ca2x, ca1y)

                slicecima = round(iso_point[2] - math.sqrt((cx2/10)**2 + (cy1/10)**2))
                slicebaixo = round(iso_point[2] + math.sqrt((cx1/10)**2 + (cy2/10)**2))

                # slicecima = round(iso_point[2] - math.sqrt((x2/10)**2 + (y1/10)**2))
                # slicebaixo = round(iso_point[2] + math.sqrt((x1/10)**2 + (y2/10)**2))
                
            elif (gantry_deg >= 90 and gantry_deg < 180):
                ponto_plot2.append((d1x, d1y))
                ponto_plot1.append((d2x, d2y))
                
                camp11 = (ca1x, ca1y)
                camp22 = (ca2x, ca2y)

                slicecima = round(iso_point[2] - math.sqrt((cx1/10)**2 + (cy1/10)**2))
                slicebaixo = round(iso_point[2] + math.sqrt((cx2/10)**2 + (cy2/10)**2))

                # slicecima = round(iso_point[2] - math.sqrt((x1/10)**2 + (y1/10)**2))
                # slicebaixo = round(iso_point[2] + math.sqrt((x2/10)**2 + (y2/10)**2))
                
            elif (gantry_deg >= 180 and gantry_deg < 270):
                ponto_plot2.append((d1x, d2y))
                ponto_plot1.append((d2x, d1y))
                
                camp11 = (ca1x, ca2y)
                camp22 = (ca2x, ca1y)

                slicecima = round(iso_point[2] - math.sqrt((cx1/10)**2 + (cy2/10)**2))
                slicebaixo = round(iso_point[2] + math.sqrt((cx2/10)**2 + (cy1/10)**2))

                # slicecima = round(iso_point[2] - math.sqrt((x1/10)**2 + (y2/10)**2))
                # slicebaixo = round(iso_point[2] + math.sqrt((x2/10)**2 + (y1/10)**2))

            elif (gantry_deg >= 270 and gantry_deg <= 360):
                ponto_plot2.append((d1x, d1y))
                ponto_plot1.append((d2x, d2y))
                
                camp11 = (ca2x, ca2y)
                camp22 = (ca1x, ca1y)

                slicecima = round(iso_point[2] - math.sqrt((cx2/10)**2 + (cy2/10)**2))
                slicebaixo = round(iso_point[2] + math.sqrt((cx1/10)**2 + (cy1/10)**2))

                # slicecima = round(iso_point[2] - math.sqrt((x2/10)**2 + (y2/10)**2))
                # slicebaixo = round(iso_point[2] + math.sqrt((x1/10)**2 + (y1/10)**2))

            if slicecima > slicebaixo:
                slice_limits.append((slicebaixo, slicecima))
            else:
                slice_limits.append((slicecima, slicebaixo))

            # print(i, gantry_deg, ponto_plot1)
            
            # intersecções de onde SSD-SAD "corta" as linhas para as linhas verticais
            # precisará do intersec1, intersec2 e interseccent para o "fim" das linhas
            A = [(campo1[0]), (campo1[1])]              
            B = [(ponto_plot1[-1][0]), (ponto_plot1[-1][1])]
            C = [(camp22[0]), (camp22[1])]
            D = [(camp11[0]), (camp11[1])]
            intersec1.append(self.line_intersection((A, B), (C, D)))
            
            A = [(campo2[0]), (campo2[1])]
            B = [(ponto_plot2[-1][0]), (ponto_plot2[-1][1])]
            C = [(camp22[0]), (camp22[1])]
            D = [(camp11[0]), (camp11[1])]
            intersec2.append(self.line_intersection((A, B), (C, D)))
            
            Ac = [(iso_point[0]), (iso_point[1])]
            Bc = [(ponto[0]), (ponto[1])]
            Cc = [(camp22[0]), (camp22[1])]
            Dc = [(camp11[0]), (camp11[1])]
            interseccent.append(self.line_intersection((Ac, Bc), (Cc, Dc)))

            meio = ((intersec1[-1][0] + ponto_plot1[-1][0])/2, (intersec1[-1][1] + ponto_plot1[-1][1])/2)
            ent_sai1.append(((meio[0] + ponto_plot1[-1][0])/2, (meio[1] + ponto_plot1[-1][1])/2))
            ent_sai1.append(meio)
            ent_sai1.append(((intersec1[-1][0] + meio[0])/2, (intersec1[-1][1] + meio[1])/2))


            meio = ((intersec2[-1][0] + ponto_plot2[-1][0])/2, (intersec2[-1][1] + ponto_plot2[-1][1])/2)
            ent_sai2.append(((meio[0] + ponto_plot2[-1][0])/2, (meio[1] + ponto_plot2[-1][1])/2))
            ent_sai2.append(meio)
            ent_sai2.append(((intersec2[-1][0] + meio[0])/2, (intersec2[-1][1] + meio[1])/2))

            #Plotar filtros - CONSIDERANDO A ROTAÇÃO DO GANTRY O CAMPO LEFT (270), RIGHT(90), OUT(180) E IN (0)
            if (rtplan.BeamSequence[i].NumberOfWedges == 1):   
                ax = 5
                ay = 5
                WedgeOrientation = rtplan.BeamSequence[i].WedgeSequence[0].WedgeOrientation
                if gantry <= 90:
                    if (WedgeOrientation == 90):
                        A = [(campo2[0]), (campo2[1])]
                        B = [(ponto_plot2[-1][0]), (ponto_plot2[-1][1])]
                        C = [(camp22[0]+ax), (camp22[1])-ay]
                        D = [(camp11[0]+ax), (camp11[1])-ay]
                        inter = self.line_intersection((A, B), (C, D))
                        pontofiltro1.append((inter[0], inter[1]))
                        pontofiltro2.append(intersec2[-1])
                        pontofiltro3.append(intersec1[-1])
                        pontofiltro4.append(None)
                        
                    elif (WedgeOrientation == 270):
                        A = [(campo1[0]), (campo1[1])]
                        B = [(ponto_plot1[-1][0]), (ponto_plot1[-1][1])]
                        C = [(camp22[0]+ax), (camp22[1])-ay]
                        D = [(camp11[0]+ax), (camp11[1])-ay]
                        inter = self.line_intersection((A, B), (C, D))
                        pontofiltro1.append((inter[0], inter[1]))
                        pontofiltro2.append(intersec1[-1])
                        pontofiltro3.append(intersec2[-1])
                        pontofiltro4.append(None)
                        
                    elif (WedgeOrientation == 180):  
                        A = [(campo1[0]), (campo1[1])]
                        B = [(ponto_plot1[-1][0]), (ponto_plot1[-1][1])]
                        C = [(camp22[0]+ax), (camp22[1])-ay]
                        D = [(camp11[0]+ax), (camp11[1])-ay]
                        inter = self.line_intersection((A, B), (C, D))
                        pontofiltro1.append((inter[0], inter[1]))
                    
                        A = [(campo2[0]), (campo2[1])]
                        B = [(ponto_plot2[-1][0]), (ponto_plot2[-1][1])]
                        C = [(camp22[0]+ax), (camp22[1])-ay]
                        D = [(camp11[0]+ax), (camp11[1])-ay]
                        inter = self.line_intersection((A, B), (C, D))
                        pontofiltro2.append((inter[0], inter[1]))
                        pontofiltro3.append(intersec1[-1])
                        pontofiltro4.append(intersec2[-1])
                        
                    else: 
                        pontofiltro1.append(intersec1[-1])
                        pontofiltro2.append(intersec2[-1])
                        pontofiltro3.append(None)
                        pontofiltro4.append(None)
                elif gantry > 90 and gantry <= 180: #GANTRY PARA CASO DE TER QUE SOMAR OU SUBTRAIS VALOR VAI MUDAR QUANTO EIXOS
                    if (WedgeOrientation == 90):
                        A = [(campo2[0]), (campo2[1])]
                        B = [(ponto_plot2[-1][0]), (ponto_plot2[-1][1])]
                        C = [(camp22[0]+ax), (camp22[1])+ay]
                        D = [(camp11[0]+ax), (camp11[1])+ay]
                        inter = self.line_intersection((A, B), (C, D))
                        pontofiltro1.append((inter[0], inter[1]))
                        pontofiltro2.append(intersec1[-1])
                        pontofiltro3.append(intersec2[-1])
                        pontofiltro4.append(None)
                        
                    elif (WedgeOrientation == 270):
                        A = [(campo1[0]), (campo1[1])]
                        B = [(ponto_plot1[-1][0]), (ponto_plot1[-1][1])]
                        C = [(camp22[0]+ax), (camp22[1])+ay]
                        D = [(camp11[0]+ax), (camp11[1])+ay]
                        inter = self.line_intersection((A, B), (C, D))
                        pontofiltro1.append((inter[0], inter[1]))
                        pontofiltro2.append(intersec2[-1])
                        pontofiltro3.append(intersec1[-1])
                        pontofiltro4.append(None)

                    elif (WedgeOrientation == 180):   
                        A = [(campo1[0]), (campo1[1])]
                        B = [(ponto_plot1[-1][0]), (ponto_plot1[-1][1])]
                        C = [(camp22[0]+ax), (camp22[1])+ay]
                        D = [(camp11[0]+ax), (camp11[1])+ay]
                        inter = self.line_intersection((A, B), (C, D))
                        pontofiltro1.append((inter[0], inter[1]))
                        
                        A = [(campo2[0]), (campo2[1])]
                        B = [(ponto_plot2[-1][0]), (ponto_plot2[-1][1])]
                        C = [(camp22[0]+ax), (camp22[1])+ay]
                        D = [(camp11[0]+ax), (camp11[1])+ay]
                        inter=(self.line_intersection((A, B), (C, D)))
                        pontofiltro2.append((inter[0], inter[1]))
                        pontofiltro3.append(intersec2[-1])
                        pontofiltro4.append(intersec1[-1])
                        
                    else: 
                        pontofiltro1.append(intersec1[-1])
                        pontofiltro2.append(intersec2[-1])
                        pontofiltro3.append(None)
                        pontofiltro4.append(None)
                elif gantry > 180 and gantry <= 270:
                    if (WedgeOrientation == 90):
                        A = [(campo2[0]), (campo2[1])]
                        B = [(ponto_plot2[-1][0]), (ponto_plot2[-1][1])]
                        C = [(camp22[0]-ax), (camp22[1])+ay]
                        D = [(camp11[0]-ax), (camp11[1])+ay]
                        inter = self.line_intersection((A, B), (C, D))
                        pontofiltro1.append((inter[0], inter[1]))
                        pontofiltro2.append(intersec1[-1])
                        pontofiltro3.append(intersec2[-1])
                        pontofiltro4.append(None)
                        
                    elif (WedgeOrientation == 270):
                        A = [(campo1[0]), (campo1[1])]
                        B = [(ponto_plot1[-1][0]), (ponto_plot1[-1][1])]
                        C = [(camp22[0]-ax), (camp22[1])+ay]
                        D = [(camp11[0]-ax), (camp11[1])+ay]
                        inter = self.line_intersection((A, B), (C, D))
                        pontofiltro1.append((inter[0], inter[1]))
                        pontofiltro2.append(intersec2[-1])
                        pontofiltro3.append(intersec1[-1])
                        pontofiltro4.append(None)

                    elif (WedgeOrientation == 180):  
                        A = [(campo1[0]), (campo1[1])]
                        B = [(ponto_plot1[-1][0]), (ponto_plot1[-1][1])]
                        C = [(camp22[0]-ax), (camp22[1])+ay]
                        D = [(camp11[0]-ax), (camp11[1])+ay]
                        inter = self.line_intersection((A, B), (C, D))
                        pontofiltro1.append((inter[0], inter[1]))
                        
                        A = [(campo2[0]), (campo2[1])]
                        B = [(ponto_plot2[-1][0]), (ponto_plot2[-1][1])]
                        C = [(camp22[0]-ax), (camp22[1])+ay]
                        D = [(camp11[0]-ax), (camp11[1])+ay]
                        inter = self.line_intersection((A, B), (C, D))
                        pontofiltro2.append((inter[0], inter[1]))
                        pontofiltro3.append(intersec1[-1])
                        pontofiltro4.append(intersec2[-1])
                        
                    else: 
                        pontofiltro1.append(intersec1[-1])
                        pontofiltro2.append(intersec2[-1])
                        pontofiltro3.append(None)
                        pontofiltro4.append(None)
                elif gantry >= 270: 
                    if (WedgeOrientation == 90):
                        A = [(campo1[0]), (campo1[1])]
                        B = [(ponto_plot1[-1][0]), (ponto_plot1[-1][1])]
                        C = [(camp22[0]-ax), (camp22[1])-ay]
                        D = [(camp11[0]-ax), (camp11[1])-ay]
                        inter = self.line_intersection((A, B), (C, D))
                        pontofiltro1.append((inter[0], inter[1]))
                        pontofiltro2.append(intersec2[-1])
                        pontofiltro3.append(intersec1[-1])
                        pontofiltro4.append(None)
                        
                    elif (WedgeOrientation == 270):
                        A = [(campo2[-1][0]), (campo2[-1][1])]
                        B = [(ponto_plot2[-1][0]), (ponto_plot2[-1][1])]
                        C = [(camp22[0]-ax), (camp22[1])-ay]
                        D = [(camp11[0]-ax), (camp11[1])-ay]
                        inter = self.line_intersection((A, B), (C, D))
                        pontofiltro1.append((inter[0], inter[1]))
                        pontofiltro2.append(intersec1[-1])
                        pontofiltro3.append(intersec2[-1])
                        pontofiltro4.append(None)
                        
                    elif (WedgeOrientation == 180):  
                        A = [(campo1[0]), (campo1[1])]
                        B = [(ponto_plot1[-1][0]), (ponto_plot1[-1][1])]
                        C = [(camp22[0]-ax), (camp22[1])-ay]
                        D = [(camp11[0]-ax), (camp11[1])-ay]
                        inter = self.line_intersection((A, B), (C, D))
                        pontofiltro1.append((inter[0], inter[1]))
                        
                        A = [(campo2[-1][0]), (campo2[-1][1])]
                        B = [(ponto_plot2[-1][0]), (ponto_plot2[-1][1])]
                        C = [(camp22[0]-ax), (camp22[1])-ay]
                        D = [(camp11[0]-ax), (camp11[1])-ay]
                        inter = self.line_intersection((A, B), (C, D))
                        pontofiltro2.append((inter[0], inter[1]))
                        pontofiltro3.append(intersec1[-1])
                        pontofiltro4.append(intersec2[-1])
                        
                    else: 
                        pontofiltro1.append(intersec1[-1])
                        pontofiltro2.append(intersec2[-1])
                        pontofiltro3.append(None)
                        pontofiltro4.append(None)
            else:
                pontofiltro1.append(None)
                pontofiltro2.append(None)
                pontofiltro3.append(None)
                pontofiltro4.append(None)

            entrada_saida1.append(ent_sai1)
            entrada_saida2.append(ent_sai2)
            
        return {
            'img_ref': img_ref,
            'slice_limits': slice_limits,
            'beam_line_iso_ini': np.array(iso_points), 
            'beam_line_iso_fim': np.array(interseccent),
            'beam_line1_ini': np.array(intersec1),
            'beam_line1_fim': np.array(ponto_plot1),
            'beam_line2_ini': np.array(intersec2),
            'beam_line2_fim': np.array(ponto_plot2),
            'filtro1': np.array(pontofiltro1),
            'filtro2': np.array(pontofiltro2),
            'filtro3': np.array(pontofiltro3),
            'filtro4': np.array(pontofiltro4),
            'entrada_saida1': np.array(entrada_saida1),
            'entrada_saida2': np.array(entrada_saida2)
        }

    