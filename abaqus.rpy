# -*- coding: mbcs -*-
#
# Abaqus/CAE Release 2018 replay file
# Internal Version: 2017_11_07-11.21.41 127140
# Run by pwalgren58 on Tue Oct 20 14:36:05 2020
#

# from driverUtils import executeOnCaeGraphicsStartup
# executeOnCaeGraphicsStartup()
#: Executing "onCaeGraphicsStartup()" in the site directory ...
from abaqus import *
from abaqusConstants import *
session.Viewport(name='Viewport: 1', origin=(0.0, 0.0), width=31.0, 
    height=131.083343505859)
session.viewports['Viewport: 1'].makeCurrent()
session.viewports['Viewport: 1'].maximize()
from caeModules import *
from driverUtils import executeOnCaeStartup
executeOnCaeStartup()
session.viewports['Viewport: 1'].partDisplay.geometryOptions.setValues(
    referenceRepresentation=ON)
execfile('C:/temp/Walgren/Cross-Optimization/AssemblyModifyEdit.py', 
    __main__.__dict__)
#: A new model database has been created.
#: The model "Model-1" has been created.
session.viewports['Viewport: 1'].setValues(displayedObject=None)
#: The model database "C:\temp\Walgren\Cross-Optimization\assembly.cae" has been opened.
session.viewports['Viewport: 1'].setValues(displayedObject=None)
#* ImportError: No module named multiarray
#* File "C:/temp/Walgren/Cross-Optimization/AssemblyModifyEdit.py", line 1225, 
#* in <module>
#*     runAssembly()
#* File "C:/temp/Walgren/Cross-Optimization/AssemblyModifyEdit.py", line 1103, 
#* in runAssembly
#*     partsInfo = pickle.load( open( 'partsInfo.p', "rb" ))
#* File "C:\SIMULIA\CAE\2018\win_b64\tools\SMApy\python2.7\lib\pickle.py", line 
#* 1378, in load
#*     return Unpickler(file).load()
#* File "C:\SIMULIA\CAE\2018\win_b64\tools\SMApy\python2.7\lib\pickle.py", line 
#* 858, in load
#*     dispatch[key](self)
#* File "C:\SIMULIA\CAE\2018\win_b64\tools\SMApy\python2.7\lib\pickle.py", line 
#* 1090, in load_global
#*     klass = self.find_class(module, name)
#* File "C:\SIMULIA\CAE\2018\win_b64\tools\SMApy\python2.7\lib\pickle.py", line 
#* 1124, in find_class
#*     __import__(module)
execfile('C:/temp/Walgren/Cross-Optimization/AssemblyModifyEdit.py', 
    __main__.__dict__)
#: A new model database has been created.
#: The model "Model-1" has been created.
session.viewports['Viewport: 1'].setValues(displayedObject=None)
#: The model database "C:\temp\Walgren\Cross-Optimization\assembly.cae" has been opened.
session.viewports['Viewport: 1'].setValues(displayedObject=None)
#: 0
#: 1
#: 2
#: 3
#: 4
#: 5
#: 6
#: 7
#: 8
#: 9
#: 10
#: 11
#: 12
#: Made it to instance 0
#* Required substructure file Cross-1_Z1.sim does not exist.
#* File "C:/temp/Walgren/Cross-Optimization/AssemblyModifyEdit.py", line 1225, 
#* in <module>
#*     runAssembly()
#* File "C:/temp/Walgren/Cross-Optimization/AssemblyModifyEdit.py", line 1084, 
#* in runAssembly
#*     allSubInfo=partsInfo,nSubs=64,nVars=3,nAtt=4,pathName=path)
#* File "C:/temp/Walgren/Cross-Optimization/AssemblyModifyEdit.py", line 153, 
#* in importSubstructure
#*     mdb.models[modelName].PartFromSubstructure(name=partName, 
#* substructureFile=substructureFileName,odbFile=odbName)
execfile('C:/temp/Walgren/Cross-Optimization/AssemblyModifyEdit.py', 
    __main__.__dict__)
#: A new model database has been created.
#: The model "Model-1" has been created.
session.viewports['Viewport: 1'].setValues(displayedObject=None)
#: 0
#: 1
#: 2
#: 3
#: 4
#: 5
#: 6
#: 7
#: 8
#: 9
#: 10
#: 11
#: 12
#: Made it to instance 0
#* Required substructure file Cross-1_Z1.sim does not exist.
#* File "C:/temp/Walgren/Cross-Optimization/AssemblyModifyEdit.py", line 1225, 
#* in <module>
#*     runAssembly()
#* File "C:/temp/Walgren/Cross-Optimization/AssemblyModifyEdit.py", line 1083, 
#* in runAssembly
#*     allSubInfo=partsInfo,nSubs=64,nVars=3,nAtt=4,pathName=path)
#* File "C:/temp/Walgren/Cross-Optimization/AssemblyModifyEdit.py", line 153, 
#* in importSubstructure
#*     mdb.models[modelName].PartFromSubstructure(name=partName, 
#* substructureFile=substructureFileName,odbFile=odbName)
