# -*- coding: utf-8 -*-
"""
Created on Mon Nov 24 00:36:10 2014

@author: Avilash
"""

import cv2
import numpy as np
from scipy import misc
#from scipy import ndimage
import matplotlib.pyplot as plt
img = misc.imread('AVG_Gray_avi2.tif')

#gaussian blur
img = cv2.GaussianBlur(img, (5,19), 3)
#resizing
img = misc.imresize(img, 0.1)
#padding

szImg = img.shape

#imgNew = np.zeros((int(szImg[0]),(int(szImg[1] + 2))))
imgNew = np.lib.pad(img, ((0,0),(1,1)), 'constant')
szImgNew = imgNew.shape
gradImg = np.zeros(szImgNew)

for i in range(0,(int(szImgNew[1])-1)):
    gradImg[:,i] = -1*np.gradient((imgNew[:,i]), 2)

#vertical gradient image
gradImg = (gradImg - np.amin(gradImg))/(np.amax(gradImg) - np.amin(gradImg))

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
    (i,j) = np.unravel_index(ind,szadjMW, order='F') 
    (iX,iY) = np.unravel_index(i,szImgNew, order='F') 
    (jX,jY) = ((iX + neighborIter[0,j]), (iY + neighborIter[1,j]))
    if jX >= 1 and jX <= (int(szImgNew[0])-1) and jY >=1 and jY <= (int(szImgNew[1])-1):
        if jY == 1 or jY == int(szImgNew[1]):
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

newLen = 1
for p in range (0, (keepInd.size-1)) :
    if keepInd[p]:
        newLen = newLen + 1 

RealadjMW = np.zeros(newLen)
RealadjMmW = np.zeros(newLen)
RealadjMX = np.zeros(newLen)
RealadjMY = np.zeros(newLen)

q = 0
for r in range (0, (keepInd.size - 1)):
    if keepInd[r]:
        RealadjMW[q] = adjMW[np.unravel_index(r,szadjMW, order='F')]
        RealadjMmW[q] = adjMmW[np.unravel_index(r,szadjMW, order='F')]
        RealadjMX[q] = adjMX[np.unravel_index(r,szadjMW, order='F')]
        RealadjMY[q] = adjMY[np.unravel_index(r,szadjMW, order='F')]
        q = q + 1


#sparse matrices

adjMatrixW = 


#plt.imshow(img, cmap=plt.cm.gray)
#plt.show
#print (gradImgMinus)