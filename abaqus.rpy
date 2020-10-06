# -*- coding: mbcs -*-
#
# Abaqus/CAE Release 2018 replay file
# Internal Version: 2017_11_07-11.21.41 127140
# Run by sebastian.chirinos on Fri Oct  2 16:29:48 2020
#

# from driverUtils import executeOnCaeGraphicsStartup
# executeOnCaeGraphicsStartup()
#: Executing "onCaeGraphicsStartup()" in the site directory ...
from abaqus import *
from abaqusConstants import *
session.Viewport(name='Viewport: 1', origin=(0.0, 0.0), width=79.6100006103516, 
    height=120.269996643066)
session.viewports['Viewport: 1'].makeCurrent()
session.viewports['Viewport: 1'].maximize()
from caeModules import *
from driverUtils import executeOnCaeStartup
executeOnCaeStartup()
openMdb('assembly.cae')
#: The model database "C:\Users\sebastian.chirinos\MEEN 491H\Cross-Optimization\assembly.cae" has been opened.
session.viewports['Viewport: 1'].setValues(displayedObject=None)
session.viewports['Viewport: 1'].partDisplay.geometryOptions.setValues(
    referenceRepresentation=ON)
p = mdb.models['Model-1'].parts['Cross-1_Z1']
session.viewports['Viewport: 1'].setValues(displayedObject=p)
p1 = mdb.models['Model-1'].parts['Cross-2_Z2']
session.viewports['Viewport: 1'].setValues(displayedObject=p1)
p1 = mdb.models['Model-1'].parts['Cross-3_Z3']
session.viewports['Viewport: 1'].setValues(displayedObject=p1)
p1 = mdb.models['Model-1'].parts['Cross-4_Z4']
session.viewports['Viewport: 1'].setValues(displayedObject=p1)
p1 = mdb.models['Model-1'].parts['Cross-5_Z5']
session.viewports['Viewport: 1'].setValues(displayedObject=p1)
session.viewports['Viewport: 1'].view.setValues(nearPlane=52.107, 
    farPlane=61.0301, width=28.7852, height=15.2332, viewOffsetX=-1.06546, 
    viewOffsetY=-0.508728)
p1 = mdb.models['Model-1'].parts['Cross-7_Z7']
session.viewports['Viewport: 1'].setValues(displayedObject=p1)
