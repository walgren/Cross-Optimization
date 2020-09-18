	
def odbDisplay(AssemblyDim,instanceNames,jobName):
	pathName = 'D:/pwalgren58/Research/CRDF/Substructure Modeling/BaselineProblem/Assembly/'
	overallOdbName = pathName+str(jobName)+'.odb'

	o3 = session.openOdb(name=overallOdbName)
	
	
	# Iterate to open the substructure odbs
	for i in range(0,len(instanceNames)):
		substructureOdbName[i] = pathName+str(jobName)+'_'+str(i)+'.odb'
	return '1'

	

def xmlGenerate(AssemblyDim,jobName,path):
	masterOdb = str(path)+str(jobName)+'.odb'
	xmlTemplate = """<?xml version="1.0" ?>"""
	xmlTemplate += """\n<OdbInput>\n\t<MasterOdb Name="""+'"'+str(masterOdb)+'"/>'
	
	totalNumber = AssemblyDim[0]*AssemblyDim[1]
	
	for i in range(1,totalNumber+1):
		odbName = str(path)+str(jobName)+'_'+str(i)+'.odb'
		xmlTemplate += """\n\t<Odb Name="""+'"'+str(odbName)+'"/>'
		
	xmlTemplate += """\n</OdbInput> """

	print xmlTemplate
	return xmlTemplate
	

	
def odbCombineFunc(CombinedODB,xmlFileName):
	import sys
	import os 
	CombinedODBFile = CombinedODB+'.odb'

	import os.path
	from os import path
	if path.exists(CombinedODBFile) == True:
		os.remove(CombinedODBFile)
	sys.path.insert(9, 
		r'c:/SIMULIA/Abaqus/6.14-2/code/python2.7/lib/abaqus_plugins/odbCombine')
	import odbCombineKernel
	# Combine ODBs 
	odbCombineKernel.combineOdbs(jobName=CombinedODB, 
		configName=xmlFileName, 
		loadODB=0)
	return