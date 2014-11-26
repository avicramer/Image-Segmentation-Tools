# -*- coding: utf-8 -*-
"""
Created on Wed Nov 26 05:28:48 2014

@author: Avilash
"""

import numpy as np

#sparser
#I/P: 2 equal vectors, vecM and vecN, a third vector of equal or smaller size,
#vecVal and two natural numbers, m and n
#O/P: A sparse array of dimension m x n, such that S(vec0[k],vec1[n]) 
# = vecVal([k])
def sparser (vecM, vecN, vecVal, m, n):
    if (len(vecM)) != (len(vecN)):
        print ("error: cannot create sparse array")
        print ("input subscript vectors not equal size")
    elif (len(vecVal)) > (len(vecM)):
        print ("error: cannot create sparse array")
        print ("more values than indicies")
    elif (max(vecM) > (m-1)) or (max(vecN) > (n-1)):
        print ("error: cannot create sparse array")
        print ("subscript index greater than array size")
    else:
        sparseArray = np.zeros((m, n))
        for i in range (0, (len(vecVal) )):
            sparseArray[(vecM[i]), (vecN[i])] = vecVal[i]
            
    return sparseArray

a = sparser ([1,1,1,2,0], [1,2,3,3,0], [1,2,3,4,5], 4, 4)