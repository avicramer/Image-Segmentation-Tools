# -*- coding: utf-8 -*-
"""
Created on Tue Jan 13 01:42:03 2015

@author: Avilash
"""

import numpy as np
from scipy import misc, ndimage
from PIL import Image

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

#Inputs: the native OCT image and a rescaling factor (determines precision,
#        computation intensity)
#Outputs: the adjacency matricies, updated image, image size
#         return RealadjMW, RealadjMmW, RealadjMX, RealadjMY, imgNew, szImg, 
#         szImgNew, gradImgUn
def getAdj (input_image, rsFactor):
    imgfull = (misc.imread(input_image))#[:,:,0] #Remove the [:,:,0] if needed

    #Blur the image (gaussian blur)
    kernel = matlab_style_gauss2D()
    img = Image.fromarray(ndimage.filters.correlate(imgfull, kernel, mode='constant'))
    #img = cv2.GaussianBlur(img, (5,21), 3) A different blurring technique.
    #You could try using that instead but I don't think it makes a big difference

    #resize the image, with antialiasing.  Otherwise will not be the 
    #same as MATLAB's resize.  
    img = img.resize( ( (int(img.size[0]*rsFactor)),(int(img.size[1]*rsFactor))) ,Image.ANTIALIAS)
    img = np.array(img)
    szImg = img.shape

    #add a column of zeros on both sides, which saves us from having to know the 
    #endpoints of the layers a priori.
    imgNew = np.lib.pad(img, ((0,0),(1,1)), 'constant')
    szImgNew = imgNew.shape
    gradImgUn = np.zeros(szImgNew)
    
    for i in range(0,(int(szImgNew[1]))):
        #Change to float, otherwise negative gradient values will be reported as 
        #(value)mod4 (and then converted to floats without telling anyone)
        #>:-(
        gradImgUn[:,i] = np.gradient(([float(ele) for ele in imgNew[:,i]]), 1)

    #vertical gradient, scaled so that all values are between 0 and 1
    gradImg = (gradImgUn - np.amin(gradImgUn))/(np.amax(gradImgUn) - np.amin(gradImgUn))
    #'inverts' the image 
    gradImgMinus = gradImg*(-1) + 1

    #Adjacency matrix
    minWeight = 1.0*10**(-5)
    #weights
    adjMW = np.empty((((int(szImgNew[0]))*(int(szImgNew[1]))),8))
    #neg weights
    adjMmW = np.empty((((int(szImgNew[0]))*(int(szImgNew[1]))),8))

    adjMX = np.empty((((int(szImgNew[0]))*(int(szImgNew[1]))),8))
    adjMY = np.empty((((int(szImgNew[0]))*(int(szImgNew[1]))),8))

    (adjMW[:], adjMmW[:], adjMX[:], adjMY[:])  = (np.NAN, np.NAN, 
                                                  np.NAN, np.NAN)

    neighborIter = np.array([[1, 1,  1, 0,  0, -1, -1, -1],
                             [1, 0, -1, 1, -1,  1,  0, -1]])
    
    szadjMW = adjMmW.shape
    ind = 0

    #creating the adjacency matrix- I think this part can be done faster
    while ind != ((int(szadjMW[0]))*(int(szadjMW[1]))-1):
        #order='F' means fortran style, or column-major (like MATLAB). 
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
        
    # Maybe break here??
    
    #ASSEMBLE the adjacency matrix
    a = np.logical_and(np.ravel(~np.isnan(adjMW[:]), order='F'), 
                       np.ravel(~np.isnan(adjMX[:]), order='F'))
    b = np.logical_and(np.ravel(~np.isnan(adjMY[:]), order='F'), 
                       np.ravel(~np.isnan(adjMmW[:]), order='F'))
    
    keepInd = np.logical_and(a,b)
    newLen = np.count_nonzero(keepInd)
    
    (RealadjMW, RealadjMmW, RealadjMX, RealadjMY)  = (np.zeros(newLen), 
                                                      np.zeros(newLen), 
                                                      np.zeros(newLen), 
                                                      np.zeros(newLen))
    
    q = 0
    for r in range (0, (keepInd.size)):
        if keepInd[r]:
            RealadjMW[q] = adjMW[np.unravel_index(r,szadjMW, order='F')]
            RealadjMmW[q] = adjMmW[np.unravel_index(r,szadjMW, order='F')]
            RealadjMX[q] = adjMX[np.unravel_index(r,szadjMW, order='F')]
            RealadjMY[q] = adjMY[np.unravel_index(r,szadjMW, order='F')]
            q = q + 1
            
    return RealadjMW, RealadjMmW, RealadjMX, RealadjMY, imgNew, szImg, szImgNew, gradImgUn, img
