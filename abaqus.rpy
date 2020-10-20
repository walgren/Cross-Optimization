# -*- coding: mbcs -*-
#
# Abaqus/CAE Release 2018 replay file
# Internal Version: 2017_11_07-11.21.41 127140
# Run by sebastian.chirinos on Tue Oct 20 13:21:05 2020
#

# from driverUtils import executeOnCaeGraphicsStartup
# executeOnCaeGraphicsStartup()
#: Executing "onCaeGraphicsStartup()" in the site directory ...
from abaqus import *
from abaqusConstants import *
session.Viewport(name='Viewport: 1', origin=(0.0, 0.0), width=98.9899978637695, 
    height=102.979995727539)
session.viewports['Viewport: 1'].makeCurrent()
session.viewports['Viewport: 1'].maximize()
from caeModules import *
from driverUtils import executeOnCaeStartup
executeOnCaeStartup()
session.viewports['Viewport: 1'].partDisplay.geometryOptions.setValues(
    referenceRepresentation=ON)
execfile('AssemblyModifyEdit.py', __main__.__dict__)
#: A new model database has been created.
#: The model "Model-1" has been created.
session.viewports['Viewport: 1'].setValues(displayedObject=None)
#: The model database "C:\Users\sebastian.chirinos\MEEN 491H\Cross-Optimization\assembly.cae" has been opened.
session.viewports['Viewport: 1'].setValues(displayedObject=None)
#: [[ 0.1229278   0.1106299   0.10096546]
#:  [ 0.0531292   0.0534012   0.05866793]
#:  [ 0.1429226   0.1000093   0.05001511]
#:  [ 0.1262358   0.1493523   0.14218069]
#:  [ 0.0674831   0.0766214   0.08961898]
#:  [ 0.0859148   0.121051    0.05932485]
#:  [ 0.1040496   0.0779587   0.12316175]
#:  [ 0.0980807   0.0734466   0.07170745]
#:  [ 0.0501486   0.0527737   0.08316382]
#:  [ 0.1076083   0.0764493   0.16115386]
#:  [ 0.1058911   0.1492242   0.15619922]
#:  [ 0.0620565   0.1334104   0.13914454]
#:  [ 0.1396654   0.0565115   0.13882567]
#:  [ 0.0719231   0.0700809   0.12181175]
#:  [ 0.0776443   0.0623943   0.16151107]
#:  [ 0.0653107   0.1254109   0.12464486]
#:  [ 0.1462771   0.1345947   0.0451111 ]
#:  [ 0.0881154   0.1184537   0.08897746]
#:  [ 0.1055312   0.1153771   0.08912825]
#:  [ 0.0789408   0.1088449   0.11916616]
#:  [ 0.1243913   0.0758318   0.16713503]
#:  [ 0.0663774   0.0800509   0.09562256]
#:  [ 0.1248907   0.0578649   0.0791392 ]
#:  [ 0.0938524   0.1375132   0.10571152]
#:  [ 0.1111591   0.0648938   0.09885568]
#:  [ 0.1340524   0.1102578   0.07771603]
#:  [ 0.115314    0.1016698   0.06008422]
#:  [ 0.1265292   0.0733969   0.06579553]
#:  [ 0.1058719   0.0908538   0.11506162]
#:  [ 0.1078735   0.1318556   0.04561546]
#:  [ 0.0746744   0.1088836   0.13181647]
#:  [ 0.0634847   0.0690952   0.14998423]
#:  [ 0.1174238   0.1478781   0.06959983]
#:  [ 0.1253231   0.1343104   0.15770002]
#:  [ 0.1154683   0.0652365   0.08973373]
#:  [ 0.0773196   0.0977856   0.04445149]
#:  [ 0.0883755   0.1163811   0.06852037]
#:  [ 0.0794796   0.0965748   0.06740365]
#:  [ 0.0871951   0.0886466   0.16902841]
#:  [ 0.0577027   0.1373829   0.15362531]
#:  [ 0.0994185   0.0996008   0.17359789]
#:  [ 0.0968957   0.0978804   0.04555579]
#:  [ 0.0671453   0.0936757   0.07127086]
#:  [ 0.0703066   0.1306268   0.14968048]
#:  [ 0.0883962   0.0569527   0.05480221]
#:  [ 0.0629497   0.0561379   0.1708744 ]
#:  [ 0.0617172   0.0800939   0.04280395]
#:  [ 0.0975276   0.0566151   0.0580954 ]
#:  [ 0.0623458   0.0715667   0.07126087]
#:  [ 0.1253357   0.1147877   0.10451906]
#:  [ 0.0873885   0.0671067   0.05086912]
#:  [ 0.0836731   0.0929833   0.060822  ]
#:  [ 0.1165032   0.1307081   0.16779505]
#:  [ 0.0970276   0.07989     0.15378488]
#:  [ 0.0827442   0.0813418   0.16545901]
#:  [ 0.1174996   0.0994596   0.11767427]
#:  [ 0.1090855   0.0606377   0.06964141]
#:  [ 0.1011133   0.1481819   0.13497763]
#:  [ 0.1088528   0.0577823   0.05823594]
#:  [ 0.068873    0.1191973   0.12605156]
#:  [ 0.1021991   0.1231301   0.05717173]
#:  [ 0.1107546   0.0636915   0.13681444]
#:  [ 0.0740839   0.0880308   0.1354369 ]
#:  [ 0.0626581   0.0961981   0.09958805]]
#: [Cross-22_Z22 Cross-1_Z1 Cross-37_Z37 Cross-43_Z43 Cross-6_Z6 Cross-21_Z21
#:  Cross-23_Z23 Cross-18_Z18 Cross-2_Z2 Cross-24_Z24 Cross-28_Z28
#:  Cross-11_Z11 Cross-35_Z35 Cross-3_Z3 Cross-20_Z20 Cross-11_Z11
#:  Cross-41_Z41 Cross-22_Z22 Cross-22_Z22 Cross-23_Z23 Cross-24_Z24
#:  Cross-6_Z6 Cross-18_Z18 Cross-26_Z26 Cross-18_Z18 Cross-38_Z38
#:  Cross-21_Z21 Cross-34_Z34 Cross-23_Z23 Cross-25_Z25 Cross-7_Z7 Cross-3_Z3
#:  Cross-26_Z26 Cross-44_Z44 Cross-18_Z18 Cross-21_Z21 Cross-22_Z22
#:  Cross-22_Z22 Cross-24_Z24 Cross-12_Z12 Cross-24_Z24 Cross-21_Z21
#:  Cross-6_Z6 Cross-11_Z11 Cross-17_Z17 Cross-4_Z4 Cross-5_Z5 Cross-17_Z17
#:  Cross-2_Z2 Cross-38_Z38 Cross-17_Z17 Cross-21_Z21 Cross-28_Z28
#:  Cross-24_Z24 Cross-24_Z24 Cross-23_Z23 Cross-18_Z18 Cross-27_Z27
#:  Cross-17_Z17 Cross-7_Z7 Cross-21_Z21 Cross-19_Z19 Cross-7_Z7 Cross-6_Z6]
#: Cross-22_Z22
#: Cross-1_Z1
#: Cross-37_Z37
#: Cross-43_Z43
#: Cross-6_Z6
#: Cross-21_Z21
#: Cross-23_Z23
#: Cross-18_Z18
#: Cross-2_Z2
#: Cross-24_Z24
#: Cross-28_Z28
#: Cross-11_Z11
#: Cross-35_Z35
#: Cross-3_Z3
#: Cross-20_Z20
#: [-0.005, 0.005, 0.0, 0.005, 0.005, 0.0]
#* The boolean operation failed
#* File "AssemblyModifyEdit.py", line 1225, in <module>
#*     runAssembly()
#* File "AssemblyModifyEdit.py", line 1117, in runAssembly
#*     BoundarySets(modelData,instanceNames=instanceNames)
#* File "AssemblyModifyEdit.py", line 442, in BoundarySets
#*     a.sets[topName], a.sets[leftName], ))
cliCommand("""a = mdb.models['Model-1'].rootAssembly""")
cliCommand("""n1=a.instances['Cross-22_Z22_1'].nodes""")
cliCommand("""nodesTop=[]""")
cliCommand("""nodesTop.append(n1.getByBoundingBox(-0.005,0.005,0.0,0.005,0.005,0.0))""")
cliCommand("""print(nodesTop)""")
#: [mdb.models['Model-1'].rootAssembly.instances['Cross-22_Z22_1'].nodes[0:0]]
a = mdb.models['Model-1'].rootAssembly
session.viewports['Viewport: 1'].setValues(displayedObject=a)
session.viewports['Viewport: 1'].assemblyDisplay.setValues(
    optimizationTasks=OFF, geometricRestrictions=OFF, stopConditions=OFF)
#: Coordinates of node 36 :-5.E-03,-5.E-03,0.
#: Coordinates of node 36 :5.E-03,5.E-03,0.
session.viewports['Viewport: 1'].view.setValues(nearPlane=0.116455, 
    farPlane=0.116783, width=0.000357707, height=0.00035463, 
    viewOffsetX=-0.015061, viewOffsetY=-0.00502876)
cliCommand("""nodesTop.append(n1.getByBoundingBox(-0.005,0.005,-0.001,0.005,0.005,0.001))""")
cliCommand("""print(nodesTop)""")
#: [mdb.models['Model-1'].rootAssembly.instances['Cross-22_Z22_1'].nodes[0:0], mdb.models['Model-1'].rootAssembly.instances['Cross-22_Z22_1'].nodes[0:0]]
cliCommand("""print(n1[0])""")
#: ({'coordinates': (-0.00313431466929615, 0.0024272077716887, 0.0), 'instanceName': 'Cross-22_Z22_1', 'label': 1})
cliCommand("""print(n1[1])""")
#: ({'coordinates': (-0.0024272077716887, 0.00313431466929615, 0.0), 'instanceName': 'Cross-22_Z22_1', 'label': 2})
