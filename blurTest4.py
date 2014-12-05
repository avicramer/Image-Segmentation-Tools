# -*- coding: utf-8 -*-
"""
Created on Mon Nov 24 00:36:10 2014

@author: Avilash
"""
#A port of a MATLAB retinal segmentation alogorithm 
#Using Dijkstra's algorithm to find the edges in an OCT image of the retina


#import cv2
import numpy as np

#impletmentation of Dijkstra's algorithm.  Runs in O(m log n), m is the number
#of edges, and n the number of nodes
import dijkstra as dj
from scipy import misc, ndimage
from PIL import Image

#Changes the sparse array into a dict of dicts
#which can be read in by dijkstra.py
import sparseToDict as sD
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

kernel = matlab_style_gauss2D()
img = misc.imread('AVG_Gray_avi2.tif')


#Blur the image (gaussian blue)
img1 = ndimage.filters.correlate(img, kernel, mode='constant')
#img = cv2.GaussianBlur(img, (5,21), 3)
img = Image.fromarray(img1)

#resize the image, with antialiasing.  Otherwise will not be the same as 
#MATLAB's resize 
img = img.resize( (145 , 200), Image.ANTIALIAS) #indices seem to be reversed?
img = np.array(img)
szImg = img.shape

#add a column of zeros on both sides
imgNew = np.lib.pad(img, ((0,0),(1,1)), 'constant')
szImgNew = imgNew.shape
gradImg = np.zeros(szImgNew)

for i in range(0,(int(szImgNew[1]))):
    gradImg[:,i] = -1*np.gradient((imgNew[:,i]), 2)

#vertical gradient 
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
indR = 0
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

#finding the 'shortest path'from dark to light
wGraph = sD.sparseToDict(RealadjMX, RealadjMY, RealadjMW)
#finding the 'shortest path' from light to dark
mwGraph = sD.sparseToDict(RealadjMX, RealadjMY, RealadjMmW)
path1 = dj.shortest_path(wGraph, str(np.amin(RealadjMX)), str(np.amax(RealadjMX)))
path2 = dj.shortest_path(mwGraph, str(np.amin(RealadjMX)), str(np.amax(RealadjMX)))








#sparse matrices, 29400 * 29400

#adjMatrixW = sA.sparser(RealadjMX, RealadjMY, RealadjMW, imgNew.size, imgNew.size)
#adjMatrixMW = sA.sparser(RealadjMX, RealadjMY, RealadjMmW, imgNew.size, imgNew.size)

#plt.imshow(img, cmap=plt.cm.gray)
#plt.show
#print (gradImgMinus)
