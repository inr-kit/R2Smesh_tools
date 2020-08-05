# python script to convert decay gamma source file from 
# R2Smesh-3.0 (A.Travleev) to CDGS format.

# !!!!!!!!!!! Hard Codes !!!!!!!!!!
# 1. input file name "dgs", output file name "cdgs"
# 2. Gamma photon groups 24; FISPACT group structure
# 3. one mesh, one cooling time step 
# 4. rectangular mesh
# #################################
import pdb
import datetime

inFile = open("dgs",'r')
outFile = open("cdgs",'w')

# ###global variables ###
# {"X":0, "Y":0, "Z":0, "Gamma":[]}
data = []	# each element has format of {"X":0, "Y":0, "Z":0, "Gamma":[24]}
bounds = {"X":[], "Y":[], "Z":[] } # boundaries of the mesh: X, Y, Z
intX = 0 	# interval X (boundary X -1)
intY = 0 	# interval Y (boundary Y -1)
intZ = 0 	# interval Z (boundary Z -1)
isUniform = False 	# is  uniform mesh ? default no
volVoxel = 0.0 		# volume of the voxel, if 0 then it is not uniform voxel
totIntensity = 0.0 	# total source intensity. 
coolingTime = 0  	# cooling time, here we use the interval number in FISPACT cal.
energyBounds = [0.00,0.01,0.02,0.05,0.10,0.20,0.30,0.40,0.60,0.80,1.00,1.22,1.44,1.66,2.00,2.50,3.00,4.00,5.00,6.50,8.00,10.0,12.0,14.0,20.0 ] # hard coded energy bounds
sourcePoints = 0

##### start to read the dgs file  #####
lineCnt = 0
for line in inFile:
	lineCnt += 1
	# to process the header info
	if lineCnt == 1:
		# no. of boundaries. convert to no. of intervals
		lineSplit = [int(x) for x in line.split()]
		intX, intY, intZ = lineSplit[0] - 1, lineSplit[1] - 1, lineSplit[2] - 1
	elif lineCnt == 2:
		# X boundaries 
		bounds["X"] = [float(a) for a in line.split()]
		if len(bounds["X"]) != intX +1:
			print "warning: X boundaries read not equal to no. boundary defined in first line!"
		# boundary steps
		boundStep = [ m - n for m,n in zip(bounds["X"][1:] , bounds["X"][0:-1] )] 
		# if max - min < small number, then it is uniform mesh, otherwise not.
		if abs ( max(boundStep) - min (boundStep)) < 1e-4:
			isUniform = True
			avgXstep =  sum(boundStep)/len(boundStep)			
	elif lineCnt == 3:
		# Y boundaries 
		bounds["Y"] = [float(a) for a in line.split()]
		if len(bounds["Y"]) != intY +1:
			print "warning: Y boundaries read not equal to no. boundary defined in first line!"
		# boundary steps
		boundStep = [ m - n for m,n in zip(bounds["Y"][1:] , bounds["Y"][0:-1] )] 
		# if max - min < small number, then it is uniform mesh, otherwise not.
		if abs ( max(boundStep) - min (boundStep)) < 1e-4:
			isUniform = True and isUniform
			avgYstep =  sum(boundStep)/len(boundStep)		
	elif lineCnt == 4:
		# Z boundaries 
		bounds["Z"] = [float(a) for a in line.split()]
		if len(bounds["Z"]) != intZ +1:
			print "warning: Z boundaries read not equal to no. boundary defined in first line!"
		# boundary steps
		boundStep = [ m - n for m,n in zip(bounds["Z"][1:] , bounds["Z"][0:-1] )] 
		# if max - min < small number, then it is uniform mesh, otherwise not.
		if abs ( max(boundStep) - min (boundStep)) < 1e-4:
			isUniform = True and isUniform
			avgZstep =  sum(boundStep)/len(boundStep)		
	elif lineCnt == 5:
		# no. of source data lines
		sourcePoints = int(line) 
	else:
		lineSplit = line.split()
		# a line muss contain: time interval, x, y, z, gamma*24 (energyBounds = 25)
		if len(lineSplit) != len(energyBounds) + 3 : 
			print "error in line ", lineCnt, ": unexpected number of data!"
			exit(-1)
		#checking the cooling time mismatch. Should not happen.
		if lineCnt == 6:
			coolingTime = int (lineSplit[0])
		else:
			if int (lineSplit[0]) != coolingTime:
				print "warning in line ", lineCnt, ": cooling time differs from previous source line!"
				coolingTime = int (lineSplit[0])
		#save the data
		srcLine = {"X":0, "Y":0, "Z":0, "Gamma":[]}
		srcLine["X"],srcLine["Y"],srcLine["Z"] = int(lineSplit[1]),  int( lineSplit[2] ),  int( lineSplit[3] )
		srcLine["Gamma"] =  [float(a) for a in lineSplit[4:]]
		totIntensity += sum( srcLine["Gamma"] )
		data.append(srcLine)

# pdb.set_trace()
# checking the lines read and source point defined
if sourcePoints != lineCnt - 5 :
	print "warning: number of source line read does not match with defined in the 5th line"
	
if isUniform:
	volVoxel = avgXstep * avgYstep * avgZstep

##### start to write the cR2s file  #####
outFile.write("num_meshes 1\n")
outFile.write("total_source " + "{: .6e}".format(totIntensity)  + "\n")
outFile.write("mesh_id 1\n")
outFile.write("Convert from R2Smesh-3.0 dgs file at " + datetime.datetime.now().strftime("%I:%M%p on %B %d, %Y") + "\n" )
outFile.write("cooling_time " + str(float(coolingTime)) + "\n")
outFile.write("mesh_source " + "{: .6e}".format(totIntensity)  + "\n")
outFile.write("energy_type bins\n")
outFile.write("energy_boundaries " + str(len (energyBounds) ) + "\n")
for i,e in enumerate(energyBounds):
	outFile.write( '%6s' %str(e)  )
	if i%8 == 7:
		outFile.write("\n")
outFile.write("\n")
outFile.write("mesh_type rec\n")
#print the boundaries
outFile.write("mesh_boundaries " + str( intX +1 ) + " " + str( intY +1 ) + " " + str( intZ +1 ) + "\n")
outFile.write(" 0.0 0.0 0.0 1.0 0.0 0.0 0.0 1.0 0.0 \n")
for i,e in enumerate(bounds["X"]) :
	outFile.write(  " " + "{: .4e}".format(e))
	if i%8 == 7:
		outFile.write("\n")
outFile.write("\n")
for i,e in enumerate(bounds["Y"]):
	outFile.write(  " " + "{: .4e}".format(e))
	if i%8 == 7:
		outFile.write("\n")
outFile.write("\n")
for i,e in enumerate(bounds["Z"]):
	outFile.write(  " " + "{: .4e}".format(e))
	if i%8 == 7:
		outFile.write("\n")
outFile.write("\n")
# print the source data
outFile.write("source_data\n")
for aSrc in data:
	# print the element line
	# in the example, the element ID starts from 1. it is assume that 
	# the first element id is ( 0 * intY * intZ + 0 * intZ + 0 ) + 1 
	# Noted that the  aSrc["X/Y/Z"] are start from 1
	elmID = ( (aSrc["X"]-1) * intY * intZ + (aSrc["Y"]-1) * intZ + (aSrc["Z"]-1) ) +1
	outFile.write('%14s' % str(elmID) )
	sumIntensity = sum ( aSrc["Gamma"] )
	outFile.write( " " + "{: .6e}".format ( sumIntensity ))
	if isUniform:
		outFile.write( " " + "{: .6e}".format ( volVoxel ) + '%14s' % "1" + "\n")
	else:
		# Noted that the  aSrc["X/Y/Z"] are start from 1.
		vol = ( bounds["X"][aSrc["X"]] - bounds["X"][aSrc["X"]-1] ) * \
			( bounds["Y"][aSrc["Y"]] - bounds["Y"][aSrc["Y"]-1] ) * \
			( bounds["Z"][aSrc["Z"]] - bounds["Z"][aSrc["Z"]-1] ) 
		outFile.write( " " + "{: .6e}".format ( vol )+ '%14s' % "1" + "\n")
	#outFile.write('%14s' % "1" + "\n")
	
	#print the cell line
	outFile.write('%14s' % "0" )
	outFile.write('%14s' % "1.0" )
	outFile.write( " " + "{: .6e}".format ( sumIntensity ) + "\n")
	
	#print the source data
	for i in range(48):
		if i < len( aSrc["Gamma"] ):
			outFile.write( " " + "{: .6e}".format ( aSrc["Gamma"][i] ) )
		else:
			outFile.write( " " + "{: .6e}".format ( 0.0 ) )
		if i%8 == 7:
			outFile.write("\n")
outFile.write("end_source_data\n")






