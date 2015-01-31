# -*- coding: utf-8 -*-
"""
Created on Tue Jan 20 01:53:04 2015

@author: Avilash
"""

import numpy as np
import getAdj as gA
import ismember as iM
import dijkstra as dj
import matplotlib.pyplot as plt

#sparseToDict
#Takes three 1-D arrays of equal size, representing values in an array such that
# (xArray(i), yArray(i)) = valArray (i). (A represntation of a 
#directed graph)
#Returns the directed graph, stored as a dict of dicts, which can be read into
#dijkstra.py
def sparseToDict(xArray, yArray, valArray):
    if xArray.size == yArray.size == valArray.size:
        graph = {}
        for i in range(0, xArray.size):
            xI = str(xArray[i])
            yI = str(yArray[i])
            valI = valArray[i]
            if graph.has_key(xI):
                (graph[xI])[yI] = valI
            else:
                graph[xI] = {yI : valI}  
        return graph
    else:
        print ("error: cannot create sparse array")
        print ("input subscript vectors not equal size")

#Inputs: Adjacency Matricies, region of interest, image size
#Outputs: Layer boundaries (shortest path)

def pathFinder (adjMX, adjMY, Mweight, roi, szImgNew):  #Mweight can be either MW or MmW
    findroiImg = (np.nonzero(np.ravel(roi, order='F')))[0]   
    includeX = iM.ismember(adjMX, findroiImg)
    includeY = iM.ismember(adjMY, findroiImg)
    keepInd = np.logical_and (includeX, includeY)
    newLen = np.count_nonzero(keepInd)
    (RealadjMW, RealadjMX, RealadjMY)  = (np.zeros(newLen), 
                                          np.zeros(newLen), 
                                          np.zeros(newLen))
    q = 0
    for r in range (0, (keepInd.size)):
        if keepInd[r]:
            RealadjMW[q] = Mweight[r]
            RealadjMX[q] = adjMX[r]
            RealadjMY[q] = adjMY[r]            
            q = q + 1     
    strmin = str(np.amin(RealadjMX))
    strmax = str(np.amax(RealadjMX))

    #finding the 'shortest path' on the light to dark boundary (MW)
    #or dark to light boundary (MmW)
    wGraph = sparseToDict(RealadjMX, RealadjMY, RealadjMW) #convert graph to hashtable                                            
    pathW = dj.shortest_path(wGraph, strmin, strmax)
    fullPathLen = len(pathW)
    pathX, pathY = np.zeros(fullPathLen), np.zeros(fullPathLen)
    for a in range (0,fullPathLen):
        (pathY[a],pathX[a]) = np.unravel_index(int(float(pathW[a])),
                                                 szImgNew, order='F')

    xmin = np.amin(pathX)
    xmax = np.amax(pathX)
    truepathX1 = []
    truepathY1 = []
    #Removes the first and lost points (through the padded zeros)
    z = 0
    for xele in pathX:
        if xele != xmin and xele != xmax:
            truepathX1.append(xele - 1) #because you removed the first column
            truepathY1.append(pathY[z])
        z = z + 1
                                    
    return truepathX1, truepathY1

#Inputs: native OCT image
#Outputs:  Three boundary layers: Viterous-NFL, IS-OS, and RPE-Choroid 
#(the hyper reflective boundaries, and the RPE-choroid boundary)
def hyperReflect(inputImg):
    rsFactor = 0.2 #bigger is better, more computationally intensive
                   #0.1 should be fine for debugging, 0.2 preferred
    offsets = np.arange(-20,21) #should have 41 elements
    offSize = np.size(offsets)
    [adjMW, adjMmW, adjMX, adjMY, imgNew, szImg, szImgNew, gy, img] = gA.getAdj(inputImg, rsFactor)
    gymean = np.mean(gy)
    roiImg = np.zeros(szImgNew)
    roiImg[(gy > gymean)] = 1 
    roiImgMmW = (roiImg - 1) * (-1)
    count = 0
    pathXList = []
    pathYList = []
    #Find the RPE-choroid boundary
    (RPEx, RPEy) = pathFinder(adjMX, adjMY, adjMmW, roiImgMmW, szImgNew)
    #Find the two hyperreflective layers
    while count < 2:        
        roiImg[:,0] = 1 #set first and last column (the padded zeros) to 1
        roiImg[:,-1] = 1
        (pathX1, pathY1) = pathFinder(adjMX, adjMY, adjMW, roiImg, szImgNew)
        pathXList.append(pathX1)
        pathYList.append(pathY1)
        count = count + 1
        
        #remove the path from the graph, by changing the ROI                                                                                     
        pathXArr = np.tile(pathX1, (offSize,offSize)) #offsize = 41 for now
        pathYArr = np.tile(pathY1, (offSize,offSize))
        for i in range(0,offSize):
            pathYArr[i,:] = pathYArr[i,:] + offsets[i]
        condition0 = np.logical_and((pathYArr >= 0),  (pathYArr < szImgNew[1]))
        pathYArr = (pathYArr[condition0]).astype(int)
        pathXArr = (pathXArr[condition0]).astype(int)
        pathArr = (np.ravel_multi_index((pathYArr,pathXArr),szImgNew,order='F')) 
        pathArr = np.unravel_index(pathArr, roiImg.shape,order='F')
        roiImg[pathArr] = 0
                                                 
    if np.mean(pathYList[0]) < np.mean(pathYList[1]):
        (ILMx, ILMy) = (pathXList[0], pathYList[0])
        (ISOSx, ISOSy) = (pathXList[1], pathYList[1])
    else:
        (ILMx, ILMy) = (pathXList[1], pathYList[1])
        (ISOSx, ISOSy) = (pathXList[0], pathYList[0])
     
    #INLOPL     
     
    roiImg = np.ones(szImgNew)
    
    for x in range(1, (szImgNew[1] -1)):
        roiImg[0:((ILMy[x-1])+5), x] = 0
        roiImg[((ISOSy[x-1])-5):(szImgNew[0]), x] = 0

    
#    print roiImg
    (INLOPLx, INLOPLy) = pathFinder(adjMX, adjMY, adjMW, roiImg, szImgNew)
    
    #NFLGCL

    roiImg = np.ones(szImgNew)    
    
    for x in range(1, (szImgNew[1] -1)):
        roiImg[0:((ILMy[x-1])+2), x] = 0
        roiImg[((INLOPLy[x-1])-6):(szImgNew[0]), x] = 0
        
    (NFLGCLx, NFLGCLy) = pathFinder(adjMX, adjMY, adjMmW, roiImg, szImgNew)
    
    #IPLINL - MmW, between NFLGCL and INLOPL
    
    roiImg = np.ones(szImgNew)
    
    for x in range(1, (szImgNew[1] -1)):
        roiImg[0:((NFLGCLy[x-1])+2), x] = 0
        roiImg[((INLOPLy[x-1])-2):(szImgNew[0]), x] = 0
    
    (IPLINLx, IPLINLy) = pathFinder(adjMX, adjMY, adjMmW, roiImg, szImgNew)
    
    #OPLONL - MmW, between INLOPL and ISOS
    
    roiImg = np.ones(szImgNew)
    
    for x in range(1, (szImgNew[1] -1)):
        roiImg[0:((INLOPLy[x-1])+2), x] = 0
        roiImg[((ISOSy[x-1])-2):(szImgNew[0]), x] = 0
    
    (OPLONLx, OPLONLy) = pathFinder(adjMX, adjMY, adjMmW, roiImg, szImgNew)
        
        
    return ILMx, ILMy, ISOSx, ISOSy, RPEx, RPEy,INLOPLx, INLOPLy, NFLGCLx, NFLGCLy, IPLINLx, IPLINLy,OPLONLx, OPLONLy, img
    
(ILMx, ILMy, ISOSx, ISOSy, RPEx, RPEy,INLOPLx, INLOPLy, NFLGCLx, NFLGCLy, IPLINLx, IPLINLy, OPLONLx, OPLONLy, img) = hyperReflect('cass3.tif')
    
fig = plt.figure(figsize = (12,12))
imgplot = plt.imshow(img, cmap=plt.cm.gray, figure = fig)
plt.plot(RPEx,RPEy,'b-', figure = fig)
plt.plot(ILMx,ILMy,'r-', figure = fig)   
plt.plot(ISOSx,ISOSy,'r-', figure = fig)    
plt.plot(INLOPLx,INLOPLy,'m-', figure = fig) 
plt.plot(NFLGCLx, NFLGCLy,'y-', figure = fig) 
plt.plot(IPLINLx, IPLINLy,'c-', figure = fig) 
plt.plot(OPLONLx, OPLONLy,'w-', figure = fig) 


         
