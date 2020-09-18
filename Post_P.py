'''
Assembly FEA - post-processing script

Extracts the displacement at the upper midpoint

Files needed: jobname+'.odb' - The job file you want to run. 
              
Hardcoded Lines:
    Line 27: the step is hardcoded to 'Step-1' - that could be modified 
             to be specified by the user (via a dictionary of relevant model
             information)
    Line 32, 33: The set names are hardcoded to correspond to the 'Assembly.py' 
                 script. With substructures, these set names appear to make no 
                 sense, so if you are getting an error for line 32, please let me know
    
'''

from abaqus import *
from abaqusConstants import *
import visualization
import math 
import numpy as np 


def odbPostProcess(jobName,loadFlag,assemblyDim):
    print('in post processing script')
    ### Obtain Rotation Array 
    odbName = jobName+'.odb'
    odb = visualization.openOdb(odbName)
    step=odb.steps['Step-1']

    ## Call for RP-2 Node Set 
    try:
        nodeSet = odb.rootAssembly.nodeSets['REFERENCE_POINT_PART-1-1        1']
    except:
        nodeSet = odb.rootAssembly.nodeSets['REFERENCE_POINT_PART-1-1        2']
    print('found RP-2 node set')
    elsetName = 'ALL_PART'
    elset = elemset = None 
    region = 'over the entire model'
    assembly = odb.rootAssembly 

    i=0
    frame = step.frames[-1] # we only care about the last frame (snapshot) of data
    forceField = frame.fieldOutputs['RF'] # RF = reaction force 
    forceField_nodeSet = forceField.getSubset(region=nodeSet)
    dispField = frame.fieldOutputs['U'] # U = displacement 
    dispField_nodeSet = dispField.getSubset(region=nodeSet)
    if loadFlag == 1: #x-displacement
        performanceMetric = forceField_nodeSet.values[0].data[0]/dispField_nodeSet.values[0].data[0]
    elif loadFlag == 2: #y-displacement 
        performanceMetric = forceField_nodeSet.values[0].data[1]/dispField_nodeSet.values[0].data[1]
    elif loadFlag == 3: #z-rotation
        momentField = frame.fieldOutputs['RM']
        momentField_nodeSet = momentField.getSubset(region=nodeSet)
        rotationField = frame.fieldOutputs['UR']
        rotationField_nodeSet = rotationField.getSubset(region=nodeSet)
        performanceMetric = momentField_nodeSet.values[0].data[2]/rotationField_nodeSet.values[0].data[2]
        print('calculated performance metric')
    odb.close()
    print('closed odb')
    # combinedOdb = 'Combined_'+jobName+'.odb'
    # odb = visualization.openOdb(combinedOdb)
    # step=odb.steps['Step-1']
    # assembly = odb.rootAssembly
    # frame = step.frames[-1]
    maxMises = -0.1
    #Iterate through different ODBs for stress recovery
    if loadFlag ==3: #Only check stress on the rotation job
        for i in range(1,assemblyDim[0]*assemblyDim[1]+1):
            odbName = jobName+'_'+str(i)+'.odb'
            odb = visualization.openOdb(odbName)
            step=odb.steps['Step-1']
            frame = step.frames[-1]
            allFields = frame.fieldOutputs
            stress = allFields['S']
            maxMisesSub = max(stress.bulkDataBlocks[0].mises)
            odb.close()
            
            if maxMisesSub > maxMises:
                maxMises = maxMisesSub
    

    
    return performanceMetric,maxMises 
    
