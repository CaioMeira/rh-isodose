#! -*- encoding:utf-8 -*-
import cherrypy
from cherrypy import tools
from cherrypy.lib.static import serve_file
import cherrypy_cors

import collections
from pprint import pprint
import time
from datetime import datetime
import tempfile
import os
import numpy as np
import os.path
import stat
import re
import subprocess

import urllib.request
import matplotlib.pyplot as plt
import pydicom
from lib.dicompylercore import dicomparser, dvh, dvhcalc
import multiprocessing
from cherrypy.process.plugins import BackgroundTask

import shutil
from Model.viewer.dose import Dose
from Model.viewer.contorno import Estrutura
import cherrypy
import json
import matplotlib
from dotenv import load_dotenv

matplotlib.use('Agg')
cherrypy_cors.install()

load_dotenv()

def get_env_value(key):
    val = os.getenv(key)
    if(val == 'true' or val == 'True'):
        val = True
    elif(val == 'false' or val == 'False'):
        val = False
    return val

class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return json.JSONEncoder.default(self, obj)

class NumpyFloatEncoder(json.JSONEncoder):
    def round_floats(self, o):
        if isinstance(o, float):
            return round(o, 1)
        if isinstance(o, dict):
            return {k: self.round_floats(v) for k, v in o.items()}
        if isinstance(o, (list, tuple)):
            return [self.round_floats(x) for x in o]
        return o

    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return self.round_floats(obj.tolist())
        return json.JSONEncoder.default(self, obj)
    
def is_dicom_file(filepath):
    try:
        # Tenta ler o arquivo como um arquivo DICOM
        pydicom.dcmread(filepath, stop_before_pixels=True)
        return True
    except:
        # Se ocorrer um erro, o arquivo não é um DICOM
        return False

class API:
    @cherrypy.expose
    def index(self):
        return serve_file(os.path.join(os.getcwd(), 'data/static/index.html'))
    
    @cherrypy.expose
    def contour(self, data=None):
        # pegando o path que vem via post ou get,
        if data:
            d = json.loads(data)
            rtstructs = []
            rtdoses = []
            images = {}
            for key, value in d.items():
                # Lê o Arquivo e Extrai o Dicom
                dicom = dicomparser.DicomParser(value)
                info = dicom.GetSeriesInfo()

                if info["modality"] == "RTSTRUCT":
                    rtstructs.append(dicom)
                elif info["modality"] == "CT":
                    images[dicom.ds.SOPInstanceUID] = dicom
                elif info["modality"] == "RTDOSE":
                    rtdoses.append(dicom)
            
            if len(rtstructs) == 0 or len(images) == 0:
                raise Exception("No RTStruct or CT images found")

            rtdose = rtdoses[0] if len(rtdoses) > 0 else None
            calc = Estrutura(rtstructs[0], rtdose, images)
            ret = calc.contour()
            return json.dumps(ret, cls=NumpyEncoder)
        else:
            return "Envie as Informações Via POST ou GET"

    @cherrypy.expose
    def isodose(self, data=None):
        # pegando o path que vem via post ou get,
        if data:
            d = json.loads(data)
            rtdoses = []
            for key, value in d['files'].items():
                # Lê o Arquivo e Extrai o Dicom
                dicom = dicomparser.DicomParser(value)
                info = dicom.GetSeriesInfo()

                # and 'GridFrameOffsetVector' in dicom.ds:
                if info["modality"] == "RTDOSE":
                    rtdoses.append(dicom)

            print(rtdoses)
            rtdose = rtdoses[0] if len(rtdoses) > 0 else None
            isodoses = d['isodoses'] if 'isodoses' in d else None

            calc = Dose(rtdose, None, None, isodoses)
            ret = calc.default_isodoses()
            return json.dumps(ret, cls=NumpyEncoder)
        else:
            return "Envie as Informações Via POST ou GET"

   
if __name__ == '__main__':
    cherrypy_cors.install()

    conf = {
        '/': {
            'tools.sessions.on': True,
            'tools.staticdir.root': os.path.abspath(os.getcwd()),

            # Adding the following lines enable CORS
            'cors.expose.on': True,
        },
    }

    cherrypy.config.update({'server.socket_host': '0.0.0.0',
                            'server.socket_port': 9999,
                            })
    cherrypy.quickstart(API(), '/', conf)