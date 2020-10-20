'''
Substructure Script: Assembly and Analysis - Open and Modify Version

Last updated: 9/22/2020 by Patrick Walgren 

This script populates already imported substructures to fill a [n x m] rectangle with 
arbitrary structures (e.g., four circles and 6 sinusoids, all with different
design variables).
Currently, two load cases are conducted. A shear load and a rotation load
are applied to a rigid surface which is tied to the top of the assembly.
From these two analyses, the directional stiffnesses are extracted

Files needed:
	-All the possible substructure model files: For every substructure, the following 
	files need to be in the WORKING DIRECTORY: .sup, .sim, .prt, .mdl, .stt
	-This script (Assembly.py)
	-Post_P.py - Post-processing script to extract stiffnesses
	-assembly.cae - .cae file with all of the possible substructures already imported.
		DO NOT CHANGE THIS FILE (A copy is in the /Cross subdirectory)
	-partsInfo.p - pickle that contains the relevant arrays to describe 
				   the mapping between design variables and substructures
	-input.txt - input file that contains the input vector of design variables
				   

Things to change: 
	-Model parameters start at line 827. The following lines 
	should contain the only variables that would need to be changed 
	for the current analysis framework. 
	
To-do:
	Add failure flags for different types of failure. Currently, we're only considering
	failure due to yielding during rotation, but should make it modular from the start. 
	
'''

#############################
### MODULE IMPORT 
#############################
from abaqus import *
from abaqusConstants import *
from caeModules import *

from math import *
from random import randint
import numpy as np
from numpy import genfromtxt
import time 
import os
import sys
import pickle 

from Post_P import odbPostProcess

###############################
		### FUNCTION INITIALIZATION###
###############################


def csvColRange(fpath, fCol, lCol, dtype):
	'''
	Makes arrays or arrays of arrays using genfromtxt
	The function does not support using a range for usecols, thus this was used
	
	fpath: STR - filepath
	fCol: INT - First column
	lCol: INT - Last column
	dtype: DTYPE - Data type
	'''
	cols = np.empty([lCol-fCol],dtype='object')
	i = 0
	# Data starts at row 7 (8 now, need to change after next substructure gen)
	for n in range(fCol, lCol):
		print(n)
		cols[i] = genfromtxt(fpath, delimiter=',', dtype=dtype, skip_header=7, 
							 usecols=(n))
		# If only one column, avoid a nested 1x1x1 array
		if lCol - fCol == 1:
			cols = cols[i]
		i += 1
	return cols


def importSubstructure(modelData,geometryName,allSubInfo,nSubs,nVars,nAtt,pathName):#,var1set,var2set,pathName):
	'''
	Imports all possible substructures that were generated in the other two scripts.

	Parameters
	----------
	modelData : DICT 
		modelData = {
			'modelName':'Model-1',
			'stepName':'Step-1',
			'assemblyDim':assemblyDim,
			'dim':dim}
	geometryName : STR
		Name of the substructure parts created before. In the current implementation,
		possible names are 'Circle','Sine', and 'Cross'.
	allSubInfo : LISTS
		List of Arrays with substructure info that have been appended from
		previous calls of this function.
	nSubs : INT - # of substructure info rows in respective file
	nVars : INT - # of design variable columns
	nAtt : INT - # of attribute metric columns
	pathName : STR
		Path where the substructure files are located.

	Returns
	-------
	None.

	'''
	#Data Unpackaging
	
	substructureRef = {0:'CrossAsymmetric', 1:'Cross'}
	materialRef = {0:'Aluminum 2219',1:'Kovar Steel',2:'Titanium Alpha-Beta'}
	stressN = 3 # for # of max mises stress, could make this an input
	
	# File path of DataPoints.csv for generated geometry
	fpath = geometryName+'DataPoints.csv'
	
	# Header line is 7 in the current CSV, skip footer = # of substructures
	headers = genfromtxt(fpath, delimiter=',', dtype=str, skip_header=6, skip_footer=nSubs)
	
	# Data starts at row 8
	subType = csvColRange(fpath, 0, 1, str)
	subId = csvColRange(fpath, 1, 2, int)
	materials = csvColRange(fpath, 2, 3, str)
	atts = csvColRange(fpath, 3, 3+nAtt, float)
	stress = csvColRange(fpath, 3+nAtt, 3+nAtt+stressN, float)
	dvs = csvColRange(fpath, 3+nAtt+stressN, 3+nAtt+stressN+nVars, float)
	
	# Make array to append to allSubInfo
	
	add = np.empty([6],dtype='object')
	add[0] = subType
	add[1] = subId
	add[2] = materials
	add[3] = dvs
	add[4] = atts
	add[5] = stress
   
	####
	modelName = modelData['modelName']
	
	for lenList in range(len(add[0])):
		partName = add[0][lenList]+'-'+str(add[1][lenList])+'_Z'+str(add[1][lenList])
		jobName = add[0][lenList]+'-'+str(add[1][lenList])+'.odb'
		print('Made it to instance '+str(lenList))
		substructureName=add[0][lenList]+'-'+str(add[1][lenList])+'_Z'+str(add[1][lenList])+'.sim'
		substructureFileName=pathName+substructureName
		odbName=pathName+jobName

		mdb.models[modelName].PartFromSubstructure(name=partName, substructureFile=substructureFileName,odbFile=odbName)
   ####
	
	print('allSubInfo size: '+str(len(allSubInfo)))
	
	for row in range(6):
		print(row)
		allSubInfo[row].extend(add[row])
	
	return allSubInfo

def nearestMatch(desiredAttributes, partsInfo, desiredComp, partsInfoIndex): #how should mass be handled
	'''
	Find nearest substructures based off of sum of square differences of attributes specified to compare

	Parameters
	----------
	desiredAttributes : LIST
		Being read in from text file outputted by optimizer
	partsInfo : list of Numpy ARRAYS [[STR],[INT],[STR],[ARRAYS of FLOATS],[ARRAYS of FLOATS],[ARRAYS of FLOATS]]
		Contains all substructure's names, ID, Materials, array of design variables, array of attribute metrics, array of max mises
	desiredComp : Numpy ARRAY
		Desired components to compare; array of columns to compare within design variables or attribute metrics
	partsInfoIndex : INT
		Index to use with parts info to access design variables or attribute metrics

	Returns
	-------
	Array of substructure names 

	'''

	# Input design variable ranges for accurate mapping (Need to change CSV to be able to read in these values)
	#thickness = 0.1, 0.8 
	thickMin = 0.05
	thickMax = 0.15
	#fillets = 0.1, 2.0 
	filletMin = 0.04
	filletMax = 0.175
	
	
	# Break up desiredAttributes into list of lists, each index having the attributes of a single substructure
	dAttOrig = np.reshape(desiredAttributes,(int(len(desiredAttributes)/desiredComp.size),desiredComp.size))
	# map thick13 DV 
	dAttOrig[:,0] = (thickMax-thickMin)*dAttOrig[:,0] + thickMin 
	# map thick24 DV 
	dAttOrig[:,1] = (thickMax-thickMin)*dAttOrig[:,1] + thickMin 
	#map fillet DV
	dAttOrig[:,2] = (filletMax-filletMin)*dAttOrig[:,2]+filletMin
	print(dAttOrig)
	# Initiate array for assembly modification
	assemblyMod = np.empty([dAttOrig.size/dAttOrig[0].size],dtype='object')
	actualDVs = np.empty([dAttOrig.size/dAttOrig[0].size],dtype='object')
	actualAMs = np.empty([dAttOrig.size/dAttOrig[0].size],dtype='object')
	
	# Transpose arrays of floats to where each index corresponds to a substructure's info
	dvsPartsInfo = np.transpose(partsInfo[3])
	amsPartsInfo = np.transpose(partsInfo[4])
	
	# print("dvsPartsInfo:")
	# print(dvsPartsInfo)
	# print(dvsPartsInfo[0].ravel())
	# print("amsPartsInfo:")
	# print(amsPartsInfo)
	# print(','.join(['%.3f' % num for num in amsPartsInfo.ravel()]))
	
	# Makes specified subarray for components to be compared and transposes the array
	pInfoOrig = np.transpose(partsInfo[partsInfoIndex][desiredComp[:, None], np.arange(len(partsInfo[partsInfoIndex][0]))])
	# print(pInfoOrig)
	# print(pInfoOrig.size)
	# print(dAttOrig.size)
	mass = 0
	# Loops through all arrays in dAttOrig
	for n in range(dAttOrig.size/dAttOrig[0].size):
		# print(n)
		# Makes array same size as pInfoOrig all filled with the values of a single array in dAttOrig (for one substructure)
		dAttFull = np.tile(dAttOrig[n], (pInfoOrig.size/dAttOrig[n].size,1))#np.full((pInfoOrig.size,dAttOrig[n].size), dAttOrig[n]) #Works in newer numpy version
		# Gets index of lowest sum of square differences
		# print(pInfoOrig.size/dAttOrig[n].size)
		# print(dAttFull)
		SubIndex = np.sum(np.square(np.subtract(pInfoOrig,dAttFull)),axis=1).argmin(axis=0)
		# Assign substructure to corresponding index
		assemblyMod[n] = partsInfo[0][SubIndex]+'-'+str(partsInfo[1][SubIndex])+'_Z'+str(partsInfo[1][SubIndex])
		actualDVs[n] = dvsPartsInfo[SubIndex]
		actualAMs[n] = amsPartsInfo[SubIndex]
		# Get mass from actuaAMs
		mass += actualAMs[n][-1]
	return assemblyMod, actualDVs, actualAMs, mass

def instanceAssembly(modelData,newSubstructures):	  
	'''
	Instance RANDOM substructures to fill the predetermined m-by-n rectangle
	of substructure shapes.

	Parameters
	----------
	modelData : DICT 
		modelData = {
			'modelName':'Model-1',
			'stepName':'Step-1',
			'assemblyDim':assemblyDim,
			'dim':dim}
	partList : LIST
		List of all possible substructures to instance.
	
	Example assembly order:
	 ___________
	|1	   |3    |5	 |	
	|___|___|___|
	|0	   |2	  |4	 |
	|___|___|___|

	Returns
	-------
	None.

	'''
	#Data unpackaging 
	modelName = modelData['modelName']
	assemblyDim = modelData['assemblyDim']
	# Construct Assembly 
	a = mdb.models[modelName].rootAssembly
	a.DatumCsysByDefault(CARTESIAN) 
	dim = modelData['dim']
	xLength = dim[3] - dim[0]
	yLength = dim[4] - dim[1]
	
	n = 0
	
	print(newSubstructures)
	
	for x in range(0,assemblyDim[0]):
		for y in range(0,assemblyDim[1]):
			xMove = xLength*(x)
			yMove = yLength*(y)
			# index = randint(0,len(partList)-1)
			partName = str(newSubstructures[n])
			
			print(str(partName))
			
			p = mdb.models[modelName].parts[partName]
			a = mdb.models[modelName].rootAssembly
			repeatChecker = filter(lambda x:partName in x,instanceNames)
			repeatCounter = len(repeatChecker)+1
			instanceName = partName+'_'+str(repeatCounter)
			instanceNames.append(instanceName)
			a.Instance(name=instanceName,part = p,dependent = ON)
			a.translate(instanceList=(instanceName, ), vector=(xMove,yMove,0.0))
			n += 1
			
	return instanceNames
	
def AssemblyConnectivity(assemblyDim):
	'''
	Create connectivity matrix between the substructures for tie constraints.

	Parameters
	----------
	assemblyDim : LIST
		#[Number of substructures to instance in x-direction,
		# Number of substructure to instance in y-direction]

	Returns
	-------
	NOD : DICT
		Dictionary that describes which substructures are connected to which.

	'''
	instanceLength = assemblyDim[0]*assemblyDim[1]
	NOD = {}
	for i in range(1,instanceLength+1):
		connectivity=[]
		remainder = i % assemblyDim[1]
		#Left Connectivity 
		if i-assemblyDim[1]>0:
			connectivity.append(i-assemblyDim[1])
		else:
			connectivity.append(0)
		
		#Bottom Connectivity 
		if i-1>0 and (remainder -1)!= 0:
			connectivity.append(i-1)
		else:
			connectivity.append(0)
		#Right Connectivity 
		if i+assemblyDim[1]<=instanceLength:
			connectivity.append(i+assemblyDim[1])
		else:
			connectivity.append(0)
		#Top Connectivity 
		if i+1<=instanceLength and remainder != 0:
			connectivity.append(i+1)
		else:
			connectivity.append(0)



		
		NOD[i]=connectivity

	return NOD

def BoundarySets(modelData,instanceNames):
	'''
	Create sets for each substructure boundary for ease of boundary condition
	application later. Boolean operations are applied to the corner nodes, as
	currently I don't know a way for a substructure retained DOF to be assigned 
	two conflicting boundary conditions.
	

	Parameters
	----------
	modelData : DICT 
		modelData = {
			'modelName':'Model-1',
			'stepName':'Step-1',
			'assemblyDim':assemblyDim,
			'dim':dim}	  
			dim : LIST
				Overall model geometric parameters 
				dim = [minX,minY,minZ,maxX,maxY,maxZ]
	instanceNames : LIST
		List of all instances in the assembly.

	Returns
	-------
	None.

	'''
	#Data unpackaging 
	modelName = modelData['modelName']
	assemblyDim = modelData['assemblyDim']
	dim = modelData['dim']
	xLength = dim[3] - dim[0]
	yLength = dim[4] - dim[1]
	
	j=0
	for x in range(0,assemblyDim[0]):
		for y in range(0,(assemblyDim[1])):
			instance = instanceNames[j]
			center = [xLength*x,yLength*y,0.0]
			# dim =	 [minX,minY,minZ,maxX,maxY,maxZ]
			xMin = center[0]+dim[0]
			yMin = center[1]+dim[1]
			xMax = center[0]+dim[3]
			yMax = center[1]+dim[4]
			# tBB = topBoundingBox, for brevity
			tBB = [xMin,yMax,0.0,xMax,yMax,0.0]
			bBB = [xMin,yMin,0.0,xMax,yMin,0.0]
			rBB = [xMin,yMin,0.0,xMin,yMax,0.0]
			lBB = [xMax,yMin,0.0,xMax,yMax,0.0]
			tLC=[xMin,yMax,0.0]
			tRC=[xMax,yMax,0.0]
			bLC=[xMin,yMin,0.0]
			bRC=[xMax,yMin,0.0]
			
			print(tBB)
			a = mdb.models[modelName].rootAssembly
			n1=a.instances[instance].nodes
			nodesTop=[]
			nodesBottom=[]
			nodesRight=[]
			nodesLeft=[]
			# Top
			nodesTop.append(n1.getByBoundingBox(tBB[0],tBB[1],
				tBB[2],tBB[3],tBB[4],tBB[5]))
			# Bottom
			nodesBottom.append(n1.getByBoundingBox(bBB[0],bBB[1],
				bBB[2],bBB[3],bBB[4],bBB[5]))
			# Right 
			nodesRight.append(n1.getByBoundingBox(rBB[0],rBB[1],
				rBB[2],rBB[3],rBB[4],rBB[5]))
			# Left
			nodesLeft.append(n1.getByBoundingBox(lBB[0],lBB[1],
				lBB[2],lBB[3],lBB[4],lBB[5]))

			
			topName = instance + '_Top'
			bottomName = instance + '_Bottom' 
			rightName = instance + '_Right'
			leftName = instance + '_Left'
			region1 = a.Set(nodes=nodesTop,name = topName)
			region2 = a.Set(nodes=nodesBottom,name=bottomName)
			region3 = a.Set(nodes=nodesRight,name=leftName)
			region4 = a.Set(nodes=nodesLeft,name=rightName)
			j+=1
			
			#Apply Boolean to deselect corner nodes 
			a.SetByBoolean(name=topName, operation=DIFFERENCE, sets=(
				a.sets[topName], a.sets[leftName], ))
			a.SetByBoolean(name=topName, operation=DIFFERENCE, sets=(
				a.sets[topName], a.sets[rightName], ))
			
			a.SetByBoolean(name=bottomName, operation=DIFFERENCE, sets=(
				a.sets[bottomName], a.sets[leftName], ))
			a.SetByBoolean(name=bottomName, operation=DIFFERENCE, sets=(
				a.sets[bottomName], a.sets[rightName], ))
			
			
			
	return 

def TieInstances(modelData,instanceNames,NOD):
	'''
	Ties instances in the assembly together

	Parameters
	----------
	modelData : DICT 
		modelData = {
			'modelName':'Model-1',
			'stepName':'Step-1',
			'assemblyDim':assemblyDim,
			'dim':dim}
	instanceNames : LIST
		List of all instances in the assembly.
	NOD : DICT
		Dictionary that describes which substructures are connected to which.


	Returns
	-------
	None.

	'''
	#Data unpackaging 
	modelName = modelData['modelName']
	assemblyDim = modelData['assemblyDim']
	setOrder = ['Left','Bottom','Right','Top']
	reverseSetOrder = ['Right','Top','Left','Bottom']

	j=1
	instanceNumber = 0
	for x in range(0,assemblyDim[0]):
		for y in range(0,assemblyDim[1]):
			if (x+y+2)%2==0:
				i=0

				for side in NOD[instanceNumber+1]:
					 i+=1
					 tieInstance1 = instanceNames[instanceNumber]
					 

					 if side == 0:
						 #skipping
						 dummyCount=0
					 else:
						 tieSide1=setOrder[i-1]
						 tieInstance2 = instanceNames[side-1]

						 tieSide2=reverseSetOrder[i-1]

						 a = mdb.models[modelName].rootAssembly
						 tie1=tieInstance1+'_'+tieSide1 
						 tie2=tieInstance2+'_'+tieSide2		
				 
						 region1=a.sets[tie1]
						 region2=a.sets[tie2]
						 tieName='Constraint-'+str(j)
						 j+=1
						 mdb.models[modelName].Tie(name=tieName, master=region1, slave=region2, 
							positionToleranceMethod=COMPUTED, adjust=ON, tieRotations=ON, 
							thickness=OFF)
			instanceNumber+=1
	return 

def CreateStep(modelData):
	'''
	Create static general analysis step for the entire assembly.
	
	Parameters
	----------
	modelData : DICT 
		modelData = {
			'modelName':'Model-1',
			'stepName':'Step-1',
			'assemblyDim':assemblyDim,
			'dim':dim}
	Returns
	-------
	None.

	'''
	#Data unpackaging 
	modelName = modelData['modelName']
	stepName = modelData['stepName']
	#Create Step 
	mdb.models[modelName].StaticStep(name=stepName, previous='Initial', 
		maxNumInc=1000, initialInc=1.0, minInc=1e-15)
	return
	
def CreateBottomBC(assemblyDim,instanceNames):
	'''
	Create encastre boundary condition on the bottom surface of the assembly.

	Parameters
	----------
	assemblyDim : LIST
		#[Number of substructures to instance in x-direction,
		# Number of substructure to instance in y-direction]
	instanceNames : LIST
		List of all instances in the assembly.

	Returns
	-------
	None.

	'''
	i=0
	setNameArray={}
	instanceNumber=-1	
	for x in range(0,assemblyDim[0]):
		for y in range(0,assemblyDim[1]):
			 instanceNumber+=1
			
			 if y==0:
				
				instance = instanceNames[instanceNumber]

				a = mdb.models['Model-1'].rootAssembly
				setNameArray[i] = instance+'_'+'Bottom'
				i+=1
	#Combine the set
	a.SetByBoolean(name='BottomBCNodes', sets=(a.sets[setNameArray[0]],	 ))
	for i in range(1,len(setNameArray)):
		 a.SetByBoolean(name='BottomBCNodes', sets=(a.sets[setNameArray[i]],a.sets['BottomBCNodes']	 ))
	

	#Create EncastreBC 
	a = mdb.models['Model-1'].rootAssembly
	region = a.sets['BottomBCNodes']
	mdb.models['Model-1'].EncastreBC(name='BottomBC', createStepName='Initial', 
		region=region, localCsys=None)
	return

def tieRigidBodyandParts(assemblyDim,instanceNames):
	'''
	Create vertical displacement boundary condition on the 
	top surface of the assembly.

	Parameters
	----------
	assemblyDim : LIST
		#[Number of substructures to instance in x-direction,
		# Number of substructure to instance in y-direction]
	instanceNames : LIST
		List of all instances in the assembly.

	Returns
	-------
	None.

	'''
	i=0
	setNameArray={}
	instanceNumber=-1	
	for x in range(0,assemblyDim[0]):
		for y in range(0,assemblyDim[1]):
			 instanceNumber+=1
			
			 if y==assemblyDim[1]-1:
				
				instance = instanceNames[instanceNumber]
				a = mdb.models['Model-1'].rootAssembly
				setNameArray[i] = instance+'_'+'Top'
				i+=1
	#Combine the set
	a = mdb.models['Model-1'].rootAssembly
	a.SetByBoolean(name='TopBCNodes', sets=(a.sets[setNameArray[0]],  ))
	for i in range(1,len(setNameArray)):
		 a.SetByBoolean(name='TopBCNodes', sets=(a.sets[setNameArray[i]],a.sets['TopBCNodes']  ))
	
	
	
	# Apply the BC
	a = mdb.models['Model-1'].rootAssembly
	region2 = a.sets['TopBCNodes']
	region1=a.surfaces['RigidBody']
	mdb.models['Model-1'].Tie(name='Tie', master=region1, slave=region2, 
		positionToleranceMethod=COMPUTED, adjust=ON, tieRotations=ON, 
		thickness=OFF)
	return

def CreateJob(jobName):
	'''
	Create job but DO NOT RUN 
	
	Parameters 
	-----------
	jobName : STR
		Identifier for particular job.
	Returns
	-------
	job : Job Object
		For running and waiting for completion later.

	'''

	# Create Job 
	job = mdb.Job(name=jobName, model='Model-1', description='', type=ANALYSIS, 
		atTime=None, waitMinutes=0, waitHours=0, queue=None, memory=90, 
		memoryUnits=PERCENTAGE, getMemoryFromAnalysis=True, 
		explicitPrecision=SINGLE, nodalOutputPrecision=SINGLE, echoPrint=OFF, 
		modelPrint=OFF, contactPrint=OFF, historyPrint=OFF, userSubroutine='', 
		scratch='', resultsFormat=ODB, multiprocessingMode=DEFAULT, numCpus=1, 
		numGPUs=0)
		
	# delete lock file, which for some reason tends to hang around, if it exists
	if os.access('%s.lck'%jobName,os.F_OK):
		os.remove('%s.lck'%jobName)
	
	return jobName,job 
   
def FieldOutputRequest(instanceNames):
	'''
	Request certain field outputs to be recorded for each substructure instance
	within the assembly. Crucial for data transfer during post processing.

	Parameters
	----------
	instanceNames : LIST
		List of all instances in the assembly.

	Returns
	-------
	None.

	'''
	setName = []
	mdb.models['Model-1'].FieldOutputRequest(name='SubstructureFieldOutput', 
		createStepName='Step-1', variables=('S','MISES', 'E', 'U', 'UR', 'ENER', 'ELEN', 
		'ELEDEN'))
	for i in range(0,len(instanceNames)):
		instance = instanceNames[i]
		setName.append(instance+'.Entire Substructure')
	mdb.models['Model-1'].fieldOutputRequests['SubstructureFieldOutput'].setValues(
		substructures=(setName ))
  
def odbDisplay(assemblyDim,instanceNames,jobName):
	'''
	Iterates over all possible odbs (master assembly and individual substructures)
	and opens all of them for future combining.

	Parameters
	----------
	assemblyDim : LIST
		#[Number of substructures to instance in x-direction,
		# Number of substructure to instance in y-direction]
	instanceNames : LIST
		List of all instances in the assembly.
	jobName : STR
		Identifier for particular job.

	Returns
	-------
	str
		Flag that the script completed.

	'''
	pathName = os.getcwd()
	overallOdbName = pathName+'/'+str(jobName)+'.odb'

	o3 = session.openOdb(name=overallOdbName)
	
	
	# Iterate to open the substructure odbs
	for i in range(0,len(instanceNames)):
		substructureOdbName[i] = pathName+str(jobName)+'_'+str(i)+'.odb'
	return '1'

def xmlGenerate(modelData,jobName,path):
	'''
	Generates text for xml file that is needed to combine the odb (as of 
	Abaqus 6.14-2 in 2017)

	Parameters
	----------
	modelData : DICTIONARY
		modelData = {
			'modelName':'Model-1',
			'stepName':'Step-1',
			'assemblyDim':assemblyDim,
			'dim':dim}
	jobName : STR
		Identifier for particular job.
	path : STR
		path to the current working directory

	Returns
	-------
	xmlTemplate : STR
		String of all XML commands needed to combine an odb automatically.

	'''
	#Data Unpackaging 
	assemblyDim = modelData['assemblyDim']
	masterOdb = str(path)+'/' +str(jobName)+'.odb'
	xmlTemplate = """<?xml version="1.0" ?>"""
	xmlTemplate += """\n<OdbInput>\n\t<MasterOdb Name="""+'"'+str(masterOdb)+'"/>'
	
	totalNumber = assemblyDim[0]*assemblyDim[1]
	
	for i in range(1,totalNumber+1):
		odbName = str(path)+'/'+str(jobName)+'_'+str(i)+'.odb'
		xmlTemplate += """\n\t<Odb Name="""+'"'+str(odbName)+'"/>'
		
	xmlTemplate += """\n</OdbInput> """

	return xmlTemplate

def odbCombineFunc(CombinedODB,xmlFileName):
	'''
	Runs the abaqus-internal odb combine function. May need to find the 
	new location of this function if version is changed from version 6.14-2
	
	Parameters
	----------
	CombinedODB : STR
		name of the combined odb file to be created.
	xmlFileName : STR
		file name of the xml file that contains the combine ODB information.

	Returns
	-------
	None.

	'''
	import sys
	import os 
	CombinedODBFile = CombinedODB+'.odb'

	import os.path
	from os import path
	if path.exists(CombinedODBFile) == True:
		os.remove(CombinedODBFile)
	sys.path.insert(19, 
	r'c:/SIMULIA/CAE/2018/win_b64/code/python2.7/lib/abaqus_plugins/odbCombine')
	import odbCombineKernel
	# Combine ODBs 
	odbCombineKernel.combineOdbs(jobName=CombinedODB, 
		configName=xmlFileName,loadODB=0)
	return
	
def createAnalyticalSurface(modelData):
	'''
	Creates an analytical rigid surface to easily apply boundary conditions 
	
	Parameters
	----------
	modelData : DICTIONARY
		modelData = {
			'modelName':'Model-1',
			'stepName':'Step-1',
			'assemblyDim':assemblyDim,
			'dim':dim}
	dim : LIST
		Overall model geometric parameters 
		dim = [minX,minY,minZ,maxX,maxY,maxZ]
	assemblyDim : LIST
		[Number of substructures to instance in x-direction,
		Number of substructure to instance in y-direction]

	Returns
	-------
	None
	'''
	#Data unpackaging 
	modelName = modelData['modelName']
	dim = modelData['dim']
	assemblyDim = modelData['assemblyDim']
	minX = dim[0]
	maxX = dim[3]+(assemblyDim[0]-1)*(dim[3]-dim[0])
	s1 = mdb.models[modelName].ConstrainedSketch(name='__profile__', 
		sheetSize=200.0)
	g, v, d, c = s1.geometry, s1.vertices, s1.dimensions, s1.constraints
	s1.setPrimaryObject(option=STANDALONE)
	s1.Line(point1=(minX*1.5, 0.0), point2=(maxX*1.5, 0.0))
	p = mdb.models[modelName].Part(name='Surface', dimensionality=THREE_D, 
		type=ANALYTIC_RIGID_SURFACE)
	p = mdb.models[modelName].parts['Surface']
	p.AnalyticRigidSurfExtrude(sketch=s1, depth=10.0)
	s1.unsetPrimaryObject()
	p = mdb.models[modelName].parts['Surface']
	
	return 

def instanceAnalyticalSurface(modelData):
	'''
	Places the Analytical rigid surface in the assembly, currently at the top (in the y-dimension)
	of the part.
	
	THE GEOMETRY IS ASSUMING THAT THE FIRST SUBSTRUCTURE IS CENTERED AT (0,0).
	
	Parameters
	----------
	modelData : DICTIONARY
		modelData = {
			'modelName':'Model-1',
			'stepName':'Step-1',
			'assemblyDim':assemblyDim,
			'dim':dim}
	dim : LIST
		Overall model geometric parameters 
		dim = [minX,minY,minZ,maxX,maxY,maxZ]
	assemblyDim : LIST
		[Number of substructures to instance in x-direction,
		Number of substructure to instance in y-direction]

	Returns
	-------
	None	
	'''
	#Data unpackaging
	modelName = modelData['modelName']
	dim = modelData['dim']
	assemblyDim = modelData['assemblyDim']
	
	minXSurface = dim[0]
	maxXSurface = dim[3]+(assemblyDim[0]-1)*(dim[3]-dim[0])
	surfaceLength = 1.5*(maxXSurface-minXSurface)
	xMove = -0.5*dim[0]-(surfaceLength/1.5)/4.0
	yMove = dim[4]+(assemblyDim[1]-1)*(dim[4]-dim[1])
	# Instance Part 
	a1 = mdb.models[modelName].rootAssembly
	p = mdb.models[modelName].parts['Surface']
	a1.Instance(name='Surface-1', part=p, dependent=ON)

	# Move surface to top (in y-dimension) of the part
	a1 = mdb.models[modelName].rootAssembly
	a1.translate(instanceList=('Surface-1', ), vector=(xMove, yMove, 0.0))

	
	return 
	
def defineRigidBody(modelData):
	'''
	Creates a rigid body definition for the analytical rigid surface based on a 
	reference point (defined in this function as well).
	
	ALL OF THE GEOMETRY IS ASSUMING THAT THE FIRST SUBSTRUCTURE IS CENTERED AT (0,0,0).
	
	NEED TO CHECK IF THE REFERENCE POINT INDEX (Currently hardcoded at r1[10]) CHANGES.
	THIS IS ACCOMPLISHED PASSIVELY BY THE PRINT STATEMENT 
	Parameters
	----------
	modelData : DICTIONARY
		modelData = {
			'modelName':'Model-1',
			'stepName':'Step-1',
			'assemblyDim':assemblyDim,
			'dim':dim}
	dim : LIST
		Overall model geometric parameters 
		dim = [minX,minY,minZ,maxX,maxY,maxZ]
	assemblyDim : LIST
		[Number of substructures to instance in x-direction,
		Number of substructure to instance in y-direction]

	Returns
	-------
	None	
	'''
	#Data unpackaging
	modelName = modelData['modelName']
	dim = modelData['dim']
	assemblyDim = modelData['assemblyDim']
	yMax = dim[4]+(assemblyDim[1]-1)*(dim[4]-dim[1])
	xMin = dim[0]
	xMax = dim[3]+(assemblyDim[0]-1)*(dim[3]-dim[0])
	xMid = (xMax-xMin)/2.0+dim[0]
	
	#Create reference point 
	a = mdb.models[modelName].rootAssembly
	a.ReferencePoint(point=(xMid, yMax, 0.0))
	
	#Create rigid body definition
	a = mdb.models[modelName].rootAssembly
	s1 = a.instances['Surface-1'].faces
	side2Faces1 = s1.findAt(((xMid, yMax, -0.0), ))
	region5=a.Surface(side2Faces=side2Faces1, name='RigidBody')
	a = mdb.models[modelName].rootAssembly
	r1 = a.referencePoints
	# print(r1.keys()[0])
	refPoints1=(r1[r1.keys()[0]], ) # This convoluted line of code ensures to grab the first
	#reference point, no matter the key. If there are multiple reference points in the model,
	#this may fail. 
	region1=regionToolset.Region(referencePoints=refPoints1)
	mdb.models[modelName].RigidBody(name='RigidBody', refPointRegion=region1, 
		surfaceRegion=region5)
	
	return	   

def xDisplacement(modelData):
	'''Creates a displacement at the top reference point
	
	Parameters
	--------------
	modelData : DICTIONARY
		modelData = {
			'modelName':'Model-1',
			'stepName':'Step-1',
			'assemblyDim':assemblyDim,
			'dim':dim}
	dim : LIST
		Overall model geometric parameters 
		dim = [minX,minY,minZ,maxX,maxY,maxZ]
	assemblyDim : LIST
		[Number of substructures to instance in x-direction,
		Number of substructure to instance in y-direction]
		'''
	#Data unpackaging 
	modelName = modelData['modelName']
	stepName = modelData['stepName']
	a1 = mdb.models[modelName].rootAssembly
	r1 = a1.referencePoints
	refPoints1=(r1[r1.keys()[0]], )
	region = a1.Set(referencePoints=refPoints1, name='TOP_RP')
	mdb.models[modelName].DisplacementBC(name='MOVE_RP', createStepName=stepName, 
		region=region, u1=1E-6, u2=0.0, u3=UNSET, ur1=UNSET, ur2=UNSET, ur3=0.0, 
		amplitude=UNSET, fixed=OFF, distributionType=UNIFORM, fieldName='', 
		localCsys=None)
		
	return 
	
def readlastline(file):
	with open(file, "rb") as f:
		f.seek(-2, 2)  # Jump to the second last byte.
		while f.read(1) != b"\n":  # Until EOL is found ...
			f.seek(-2, 1)  # ... jump back, over the read byte plus one more.
		last = np.char.split(f.read().decode().strip(), sep=',') # Convert binary string to UTF-8 stripped string array
		last = np.array(last.tolist()).astype(float)	# Getting rid of 
	f.close()
	return last	 # Read all data from this point on.


#################################
### ANALYSIS INITIALIZATION 
#################################

# Initialize Wall clock time 
startTime = time.clock()

# Line to save findAts instead of masks
# To grab indices (F[i]), replace COORDINATE with INDEX
session.journalOptions.setValues(replayGeometry=COORDINATE,recoverGeometry=COORDINATE)

######################################################
### MODEL PARAMETERS (All things to change are here)
######################################################

visualizationFlag = 1 #Flag for combining odbs or not. 
	# 0 = don't combine for computational efficiency (~15% faster)
	# 1 = combine to visualize entire assembly results 
dim = [-10.0, -10.0, 0.0, 10.0, 10.0, 5.0] #[minX,minY,minZ,maxX,maxY,maxZ]
assemblyDim = [5,3] #[Number of substructures to instance in x-direction,
					# Number of substructure to instance in y-direction]
# xDispJobName = 'X_DISP' #Job name for x-displacement load conditions 
# rotateJobName= 'ROT' #Job name for rotation load conditions 

# Substructure variables (two variables right now, thickness and fillet)
substructureNames = np.array(['Cross'])
thicknessSet = np.arange(0.1,0.8,0.2)#(0.2,0.5,0.05)
filletSet = np.arange(0.1,2,0.5)#(0.1,0.8,0.05)
numSubs = 4 ** 3

### Empty lists 
assemblyList = []
instanceNames = []
#Replacing with parts info array
partList = []
partsInfo = [[],[],[],[],[]]


### Collate data 
# modelData = {
	# 'modelName':'Model-1',
	# 'stepName':'Step-1',
	# 'assemblyDim':assemblyDim,
	# 'dim':dim}




def runAssembly():
	import numpy as np
	xDispJobName = 'X_DISP' #Job name for x-displacement load conditions 
	rotateJobName= 'ROT' #Job name for rotation load conditions 
	
	visualizationFlag = 0 #Flag for combining odbs or not. 
	# 0 = don't combine for computational efficiency (~15% faster)
	# 1 = combine to visualize entire assembly results 
	dim = [-0.005, -0.005, 0.0, 0.005, 0.005, 0.0025] #[minX,minY,minZ,maxX,maxY,maxZ]
	assemblyDim = [5,3] #[Number of substructures to instance in x-direction,

		# Line to save findAts instead of masks
	# To grab indices (F[i]), replace COORDINATE with INDEX
	session.journalOptions.setValues(replayGeometry=COORDINATE,recoverGeometry=COORDINATE)

	substructureNames = np.array(['CrossAsymmetric'])

	instanceNames = []
	partsInfo = [[],[],[],[],[],[]]

	modelData = {
		'modelName':'Model-1',
		'stepName':'Step-1',
		'assemblyDim':assemblyDim,
		'dim':dim}

	#Import Cross Substructure 
	path = os.getcwd()+'/'
	
	###################################################
	### The following lines of code are needed when not 
	### using the open/modify method
	###################################################
	
	#Check if Cross-3_Z3.prt exists
	# file = 'Cross-3_Z3.prt'
	# if os.path.isfile(file) == True:
		# pass
	# else:
		# print('Cross-3_Z3.prt is not in the file')
		# repositoryFolder = 'C:/temp/Cross Optimization/Cross Assembly/Cross Assembly/Cross/'
		# assemblyFolder = 'C:/temp/Cross Optimization/Cross Assembly/Open and Modify/'
		# shutil.move(repositoryFolder+file, 
			# assemblyFolder+file)
	#  Need to change nSubs to get value from updated CSV file headers
	# Mdb()
	# openMdb('assembly.cae')
	# partsInfo = importSubstructure(modelData=modelData,geometryName=substructureNames[0],
		 # allSubInfo=partsInfo,nSubs=64,nVars=3,nAtt=4,pathName=path)

	# for arr in range(len(partsInfo)): #Changing lists of lists to Array of lists
		 # partsInfo[arr] = np.array(partsInfo[arr])
		
	## Could save at this point to avoid importing substructures each run
	# pickle.dump( partsInfo, open( "partsInfo.p", "wb" ) )
	
	# Save cae at this point
	# mdb.save()

	# Stop execution of code to change partsInfo.p
	# sys.exit()

	Mdb()
	openMdb('assembly.cae')
	
	# Read in all relevant substructure information (previously the output of the 'importSubstructure'
	# function)
	partsInfo = pickle.load( open( 'partsInfo.p', "rb" ))
	#Read in design variables from matlab via inputs.txt
	desiredAttributes = np.loadtxt('input.txt', dtype=float)

	#Add function to take in design variables[3]/attribute metrics[4] from optimizer, return array with new substructures for assembly
	newSubstructures, actDVs, actAMs, mass = nearestMatch(desiredAttributes, partsInfo, desiredComp=np.array([0,1,2]), partsInfoIndex=3)

	# Instance substructures in the assembly
	instanceNames = instanceAssembly(modelData,newSubstructures=newSubstructures)

	# Create a connectivity matrix based on the assembly dimensions
	NOD = AssemblyConnectivity(assemblyDim=assemblyDim)

	# Create geometry sets for each substructure edge 
	BoundarySets(modelData,instanceNames=instanceNames)

	# Tie all instances together
	TieInstances(modelData,instanceNames=instanceNames,NOD=NOD)

	# Create static, general step 
	CreateStep(modelData)

	#Create analytical surface for boundary conditions 
	createAnalyticalSurface(modelData)

	#Instance surface in assembly 
	instanceAnalyticalSurface(modelData)

	#Define surface as a rigid body
	defineRigidBody(modelData)

	#Encastre bottom edges of bottom substructures
	CreateBottomBC(assemblyDim=assemblyDim,instanceNames=instanceNames)

	#Tie analytical surface to top edges of top substructures 
	tieRigidBodyandParts(assemblyDim,instanceNames)

	#Create x-displacement BC on the surface 
	xDisplacement(modelData)

	#Request substructure field output for post-processing and visualization
	FieldOutputRequest(instanceNames=instanceNames)
	if visualizationFlag == 1:
		###############################################################
		# Create XML files for substructure visualization (odb combine)
		###############################################################	   
		ODBpath=os.getcwd()

		xDispJobCombined = 'Combined_'+xDispJobName
		xdispFile = '/'+xDispJobCombined+'.xml'
		xdispFileName = ODBpath+xdispFile 
		xmlXDisp = xmlGenerate(modelData,
			jobName=xDispJobName,path=ODBpath)


		rotateJobCombined = 'Combined_'+rotateJobName
		rotateFile = '/'+rotateJobCombined+'.xml'
		rotateFileName = ODBpath+rotateFile
		xmlRotate = xmlGenerate(modelData,
			jobName=rotateJobName,path=ODBpath)

		outfile = open(rotateFileName,'w')
		outfile.write(xmlRotate)
		outfile.close()

		outfile = open(xdispFileName,'w')
		outfile.write(xmlXDisp)
		outfile.close()

	###################################
	## Job Creation and Post Processing
	###################################
	
	#Stiffness k_xy
	
	[xDispJobName,xDispJob] = CreateJob(jobName = xDispJobName)
	 
	xDispJob.submit()
	xDispJob.waitForCompletion()
	if visualizationFlag == 1:
		odbCombineFunc(CombinedODB=xDispJobCombined,xmlFileName=xdispFileName)

	k_xy,maxMises1 = odbPostProcess(jobName=xDispJobName,
		loadFlag=1,assemblyDim = assemblyDim)

	#Stiffness k_theta 
	
	#Change boundary condition to rotation 
	mdb.models[modelData['modelName']].boundaryConditions['MOVE_RP'].setValues(u1=UNSET,
		u2=UNSET, ur3=0.052)
	[rotateJobName,rotateJob] = CreateJob(jobName = rotateJobName)

	rotateJob.submit()
	rotateJob.waitForCompletion()
	if visualizationFlag == 1:
		odbCombineFunc(CombinedODB=rotateJobCombined,xmlFileName=rotateFileName)

	k_theta,maxMises2 = odbPostProcess(jobName=rotateJobName, 
		loadFlag=3,assemblyDim = assemblyDim)

	print time.clock()-startTime, 'seconds process time'
	#Write outputs to master text file for post-processing. NOT USED IN OPTIMIZATION
	fData=open('AssemblyOutput.txt', "a")
	fData.write(str(k_xy)+','+str(maxMises1)+','+str(k_theta)+','+str(maxMises2)+','+str(-mass)+'\n') #mass is sent in as negative to minimize in optimizer
	fData.close()
	if maxMises2 > 1000E6: #Yield stress of titanium = 1000 MPA
		output = [1.0E10,-1.0E10,-1.0E10]
	else:
		output = [k_xy,-k_theta,-mass]
	#Write output data to a pickle 
	pickle.dump( output, open( "output.p", "wb" ) )
	
	#Write desired and actual DVs to master text file. NOT USED IN OPTIMIZATION
	fOptimizerInfo=open('PlottingInfo.txt','a')
	fOptimizerInfo.write(','.join(['%.3f' % num for num in desiredAttributes])+';'+','.join(['%.3f' % num for num in np.array(actDVs.tolist()).astype(float).flatten()])+';'+','.join(['%.3f' % num for num in np.array(actAMs.tolist()).astype(float).flatten()]))
	fOptimizerInfo.close()
	

	return


# Should change importing procedure and assembly procedure to 2 functions in future iterations
runAssembly()

# if __name__ == "__main__":
	# runAssembly("Example_OptimizerOutput.txt")
	
