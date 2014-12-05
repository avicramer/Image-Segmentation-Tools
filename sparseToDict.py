# -*- coding: utf-8 -*-
"""
Created on Fri Dec 05 00:03:42 2014

@author: Avilash
"""

import numpy as np
#import dijkstra as dj

X = np.array([1,1,2,2,3,3])
Y = np.array([2,3,1,3,1,2])
Z = np.array([1,99,99,1,1,1])


def sparseToDict (xArray, yArray, valArray):
    if xArray.size == yArray.size == valArray.size:
        graph = {}
        
        for i in range(0, xArray.size):
            if graph.has_key(str(xArray[i])):
                ((graph[str(xArray[i])]))[(str(yArray[i]))] = valArray[i]
            else:
                graph[(str(xArray[i]))] = {(str(yArray[i])) : valArray[i]}  
#        print (graph)
        return graph
    else:
        print ("error: cannot create sparse array")
        print ("input subscript vectors not equal size")

#testGraph = sparseToDict (X,Y,Z)
#path  = dj.shortest_path(testGraph, '1', '3')
#print path

'''

dict['School'] = "DPS School"

if __name__=='__main__':
    # A simple edge-labeled graph using a dict of dicts
    graph = {'a': {'b':1, 'c':9999},
             'b': {'a':9999, 'c':1},
             'c': {'a':1, 'b':1}}







graph = {}

for i in range(0, X.size):
    if graph.has_key(str(X[i])):
        ((graph[str(X[i])])[0])[(str(Y[i]))] = Z[i]
    else:
        graph[(str(X[i]))] = [{(str(Y[i])) : Z[i]}]      
        
print graph

'''
