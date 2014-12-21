# -*- coding: utf-8 -*-
"""
Created on Mon Nov 24 00:36:10 2014

@author: Avilash
"""
#A port of a MATLAB retinal segmentation alogorithm 
#Using Dijkstra's algorithm to find the edges in an OCT image of the retina 
#(ILM and RPE)

#import cv2 #Only if you want to use the openCV tools
import numpy as np
#import retSeg1 as rS

#impletmentation of Dijkstra's algorithm.  Runs in O(m log n), m is the number
#of edges, and n the number of nodes.  Utilizes a priority queue dictionary.
import dijkstra as dj  #needs pdict.py
from scipy import misc, ndimage
from PIL import Image #Actually Pillow, the version of the python image library 
                      #that actually works

#from scipy import ndimage
import matplotlib.pyplot as plt


#creates the filter for the blurring step
#in the same way (almost) that MATLAB does it
def matlab_style_gauss2D(shape=(5,20),sigma=3):
    """
    2D gaussian mask - should give the same result as MATLAB's
    fspecial('gaussian',[shape],[sigma])
    """
    m,n = [(ss-1.)/2. for ss in shape]
    y,x = np.ogrid[-m:m+1,-n:n+1]
    h = np.exp( -(x*x + y*y) / (2.*sigma*sigma) )
    h[ h < np.finfo(h.dtype).eps*h.max() ] = 0
    sumh = h.sum()
    if sumh != 0:
        h /= sumh
    return h
    
#sparseToDict
#Takes three 1-D arrays of equal size, representing values in an array such that
# (xArray(i), yArray(i)) = valArray (i). (A represntation of a 
#directed graph)
#Returns the directed graph, stored as a dict of dicts.
def sparseToDict (xArray, yArray, valArray):
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
#        print (graph)
        return graph
    else:
        print ("error: cannot create sparse array")
        print ("input subscript vectors not equal size")

def retinal_segmentation (input_image):
    img = misc.imread(input_image)

    #Blur the image (gaussian blur)
    kernel = matlab_style_gauss2D()
    img = Image.fromarray(ndimage.filters.correlate(img, kernel, mode='constant'))
    #img = cv2.GaussianBlur(img, (5,21), 3) A different blurring technique

    #resize the image (to 1/10th), with antialiasing.  Otherwise will not be the 
    #same as MATLAB's resize.  
    rsFactor = 0.1
    img = img.resize( ( (int(img.size[0]*rsFactor)),(int(img.size[1]*rsFactor))) ,Image.ANTIALIAS)
    img = np.array(img)
    szImg = img.shape

    #add a column of zeros on both sides, which saves us from having to know the 
    #endpoints of the layers a priori.
    imgNew = np.lib.pad(img, ((0,0),(1,1)), 'constant')
    szImgNew = imgNew.shape
    gradImg = np.zeros(szImgNew)
    
    for i in range(0,(int(szImgNew[1]))):
        #Change to float, otherwise negative gradient values will be reported as 
        #(value)mod4 (and then converted to floats without telling anyone)
        #>:-(
        gradImg[:,i] = np.gradient(([float(ele) for ele in imgNew[:,i]]), 2)


    #vertical gradient, scaled so that all values are between 0 and 1
    gradImg = (gradImg - np.amin(gradImg))/(np.amax(gradImg) - np.amin(gradImg))
    #'inverts' the image 
    gradImgMinus = gradImg*(-1) + 1


    #Adjacency matrix

    minWeight = 1.0*10**(-5)

    #weights
    adjMW = np.empty((((int(szImgNew[0]))*(int(szImgNew[1]))),8))
    #neg weights
    adjMmW = np.empty((((int(szImgNew[0]))*(int(szImgNew[1]))),8))
    #point A
    adjMX = np.empty((((int(szImgNew[0]))*(int(szImgNew[1]))),8))
    #point B
    adjMY = np.empty((((int(szImgNew[0]))*(int(szImgNew[1]))),8))

    adjMW[:] = np.NAN
    adjMmW[:] = np.NAN
    adjMX[:] = np.NAN
    adjMY[:] = np.NAN

    neighborIter = np.array([[1, 1,  1, 0,  0, -1, -1, -1],
                             [1, 0, -1, 1, -1,  1,  0, -1]])
    
    szadjMW = adjMmW.shape

    ind = 0
    #indR = 0
    #creating the adjacency matrix
    while ind != ((int(szadjMW[0]))*(int(szadjMW[1]))-1):
        #order='F' means fortran style, or column-major (like MATLAB)
        (i,j) = np.unravel_index(ind,szadjMW, order='F') 
        (iX,iY) = np.unravel_index(i,szImgNew, order='F') 
        (jX,jY) = ((iX + neighborIter[0,j]), (iY + neighborIter[1,j]))
        if jX >= 0 and jX <= (int(szImgNew[0])-1) and jY >=0 and jY <= (int(szImgNew[1])-1):
            if jY == 0 or jY == (int(szImgNew[1]) - 1):
                adjMW[i,j] = minWeight
                adjMmW[i,j] = minWeight
            else:
                adjMW[i,j] = 2 - gradImg[iX,iY] - gradImg[jX, jY] + minWeight
                adjMmW[i,j] = 2 - gradImgMinus[iX,iY] - gradImgMinus[jX, jY] + minWeight
            #save subscripts
            adjMX[i,j] = np.ravel_multi_index((iX,iY), szImgNew, order='F')
            adjMY[i,j] = np.ravel_multi_index((jX,jY), szImgNew, order='F')
        ind = ind + 1
    
    #ASSEMBLE
    a = np.logical_and(np.ravel(~np.isnan(adjMW[:]), order='F'), np.ravel(~np.isnan(adjMX[:]), order='F'))
    b = np.logical_and(np.ravel(~np.isnan(adjMY[:]), order='F'), np.ravel(~np.isnan(adjMmW[:]), order='F'))
    keepInd = np.logical_and(a,b)

    newLen = 0
    for p in range (0, (keepInd.size)) :
        if keepInd[p]:
            newLen = newLen + 1 

    RealadjMW = np.zeros(newLen)
    RealadjMmW = np.zeros(newLen)
    RealadjMX = np.zeros(newLen)
    RealadjMY = np.zeros(newLen)

    q = 0
    for r in range (0, (keepInd.size)):
        if keepInd[r]:
            RealadjMW[q] = adjMW[np.unravel_index(r,szadjMW, order='F')]
            RealadjMmW[q] = adjMmW[np.unravel_index(r,szadjMW, order='F')]
            RealadjMX[q] = adjMX[np.unravel_index(r,szadjMW, order='F')]
            RealadjMY[q] = adjMY[np.unravel_index(r,szadjMW, order='F')]
            q = q + 1

    #finding the 'shortest path' on the dark to light boundary
    wGraph = sparseToDict(RealadjMX, RealadjMY, RealadjMW)
    path1 = dj.shortest_path(wGraph, str(np.amin(RealadjMX)), str(np.amax(RealadjMX)))

    #finding the 'shortest path' on the light to dark boundary
    mwGraph = sparseToDict(RealadjMX, RealadjMY, RealadjMmW)
    path2 = dj.shortest_path(mwGraph, str(np.amin(RealadjMX)), str(np.amax(RealadjMX)))

    fullPathLen1 = len(path1)
    fullPathLen2 = len(path2)

    pathX1 = np.zeros(fullPathLen1)
    pathY1 = np.zeros(fullPathLen1)
    pathX2 = np.zeros(fullPathLen2)
    pathY2 = np.zeros(fullPathLen2)

    #indicies reversed again??
    for a in range (0,fullPathLen1):
        (pathY1[a],pathX1[a]) = np.unravel_index(int(float(path1[a])),szImgNew, order='F')
    for b in range (0,fullPathLen2):
        (pathY2[b],pathX2[b]) = np.unravel_index(int(float(path2[b])),szImgNew, order='F')

    
    #display 
    fig = plt.figure(figsize = (12,12))
    imgplot = plt.imshow(imgNew, cmap=plt.cm.gray, figure = fig)
    plt.plot(pathX1,pathY1,'b-', figure = fig)
    plt.plot(pathX2,pathY2,'r-', figure = fig)

#retinal_segmentation('int1.tif')

#sparse matrices, 29400 * 29400
#adjMatrixW = sA.sparser(RealadjMX, RealadjMY, RealadjMW, imgNew.size, imgNew.size)
#adjMatrixMW = sA.sparser(RealadjMX, RealadjMY, RealadjMmW, imgNew.size, imgNew.size)

#plt.imshow(img, cmap=plt.cm.gray)
#plt.show
#print (gradImgMinus)
