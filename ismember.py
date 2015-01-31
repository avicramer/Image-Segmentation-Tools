# -*- coding: utf-8 -*-
"""
Created on Tue Jan 13 01:24:45 2015

@author: Avilash
"""

import numpy as np

def ismember(a, b):
    bind = {}
    for i, elt in enumerate(b):
        if elt not in bind:
            bind[elt] = True
    return [bind.get(itm, False) for itm in a] 
    
