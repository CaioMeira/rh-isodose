#! -*- encoding:utf-8 -*-
import numpy as np
import math
import copy
from scipy.spatial.distance import cdist

def rotatez(x,y,z,theta): #rotate x,y around xo,yo by theta (rad)
    xr=math.cos(theta)*(x)-math.sin(theta)*(y)  
    yr=math.sin(theta)*(x)+math.cos(theta)*(y)  
    zr=z
    return [xr,yr,zr]

def rotatex(x,y,z,theta): #rotate x,y around xo,yo by theta (rad)
    xr=x
    yr=math.cos(theta)*(y) - math.sin(theta)*(z)  
    zr=math.sin(theta)*(y)+math.cos(theta)*(z)  
    return [xr,yr,zr]

def rotatey(x,y,z,theta): #rotate x,y around xo,yo by theta (rad)
    xr=math.cos(theta)*(x) + math.sin(theta)*(z)  
    yr=y
    zr= - math.sin(theta)*(x)+math.cos(theta)*(z)  
    return [xr,yr,zr]

def translacao(x,y,z,t): #rotate x,y around xo,yo by theta (rad)
    xt= x + t[0]
    yt= y + t[1]
    zt= z + t[2]
    return [xt,yt,zt]

def calculateDistance(a, b):  
    dist = math.sqrt((b[0] - a[0])**2 + (b[1] - a[1])**2)  
    return dist

# https://wiki.python.org/moin/HowTo/Sorting
# https://www.geeksforgeeks.org/python-program-for-dijkstras-shortest-path-algorithm-greedy-algo-7/
def cmp_to_key(mycmp):
    'Convert a cmp= function into a key= function'
    class K(object):
        def __init__(self, obj, *args):
            self.obj = obj
        def __lt__(self, other):
            return mycmp(self.obj, other.obj) < 0
        def __gt__(self, other):
            return mycmp(self.obj, other.obj) > 0
        def __eq__(self, other):
            return mycmp(self.obj, other.obj) == 0
        def __le__(self, other):
            return mycmp(self.obj, other.obj) <= 0
        def __ge__(self, other):
            return mycmp(self.obj, other.obj) >= 0
        def __ne__(self, other):
            return mycmp(self.obj, other.obj) != 0
    return K

class Estrutura(object):
    def __init__(self, RTStructure, RTDose, Images):
        self.images = Images
        self.set_rtstruct(RTStructure) 
        self.rtdose = RTDose

    def set_rtstruct(self, struct):
        self.rtstruct = struct
        self._structures = self.rtstruct.GetStructures()
        for key, struct in self._structures.items():
            del struct['empty']
    
    def contour(self):
        ret = {}

        img = list(self.images.values())[0]
        im_row = img.ds.Rows
        im_col = img.ds.Columns
        img = None

        for key, struct in self._structures.items():
            id = struct['id']

            axial = {}
            sagittal = {}
            sagittal_ord = {}
            # coronal = {}
            # coronal_ord = {}

            # est_3d_ax = np.zeros((len(self.images), im_row, im_col))
            # est_3d_sag= []
            # est_3d_cor= [] 

            contour_seq = list(filter(lambda contours: contours.ReferencedROINumber == id, self.rtstruct.ds.ROIContourSequence))[0]

            if contour_seq is None or 'ContourSequence' not in contour_seq:
                print('contour_seq == None or "ContourSequence" not in contour_seq')
                continue
            
            for contourSeq in contour_seq.ContourSequence:
                contour = contourSeq.ContourData
                coord = []

                for i in range(0, len(contour), 3):
                    coord.append((contour[i], contour[i + 1], contour[i + 2]))

                if (contourSeq.ContourGeometricType == "CLOSED_PLANAR"):
                    img_ID = contourSeq.ContourImageSequence[0].ReferencedSOPInstanceUID 
                else: 
                    img_ID = self.rtstruct.ds.ReferencedFrameOfReferenceSequence[0].FrameOfReferenceUID
                    continue
                
                img = self.images[img_ID]
                # img_arr = img.ds.pixel_array
                # img_shape = img_arr.shape
                instanceNumber = int(img.ds.InstanceNumber)

                #physical distance between the center of each pixel
                x_spacing, y_spacing = float(img.ds.PixelSpacing[0]), float(img.ds.PixelSpacing[1])
                # z_spacing = float(self.rtdose.ds.GridFrameOffsetVector[1] - self.rtdose.ds.GridFrameOffsetVector[0])
                z_spacing = img.ds.SliceThickness
                #this is the center of the upper left voxel
                origin_x, origin_y, origin_z = img.ds.ImagePositionPatient
                # y, x is how it's mapped

                pixel_coords = [(np.ceil((x - origin_x) / x_spacing), np.ceil((y - origin_y) / y_spacing)) for x, y, _ in coord] 
                # pixel_coords = [(np.ceil((x - origin_x) / x_spacing), np.ceil((y - origin_y) / y_spacing), np.ceil((z - origin_z)/ z_spacing)) for x, y, z in coord] 

                if img_ID not in axial:
                    axial[img_ID] = []
                axial[img_ID].append(pixel_coords)

                for im_num in range(0, len(pixel_coords)):
                    key2 = int(pixel_coords[im_num][0])
                    if key2 not in sagittal:
                        sagittal[key2] = []
                        sagittal_ord[key2] = [] 

                    val = [pixel_coords[im_num][1], instanceNumber]
                    if val not in sagittal[key2]:
                        sagittal[key2].append(val)

            for item in sagittal.items():
                # ref = item[1][0]
                # sagittal_ord[item[0]] = sorted(item[1], key=lambda x: calculateDistance(ref, x))
                sagittal_ord[item[0]] = sorted(item[1], key=cmp_to_key(calculateDistance))

            #     for el in range(len(pixel_coords)):
            #         est_3d_ax[instanceNumber][int(pixel_coords[el][1])][int(pixel_coords[el][0])] = 1 
            
            # for k in range(est_3d_ax.shape[2]):
            #     est_3d_sag.append((est_3d_ax[:,:,k]))
                
            # for k in range(est_3d_ax.shape[1]):
            #     est_3d_cor.append((est_3d_ax[:,k,:]))

            ret[id] = {
                'id': struct['id'],
                'name': struct['name'],
                'type': struct['type'],
                'color': struct['color'],
                'axial_data': axial,
                #'sagittal_data': sagittal_ord,
                # 'coronal_data': est_3d_cor

                # 'axial_data': est_3d_ax,
                # 'sagittal_data': est_3d_sag,
                # 'coronal_data': est_3d_cor
            }
        return ret

    def structures(self):
        return self._structures