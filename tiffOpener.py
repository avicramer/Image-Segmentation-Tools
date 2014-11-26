# -*- coding: utf-8 -*-
"""
Created on Fri Nov 07 02:27:15 2014

@author: Avilash
"""

from Tkinter import *

from PIL import Image
import ImageTk
import numpy

root = Tk()

im1 = Image.open('int1.tif')
imarray = numpy.array(im1)
im1.seek(1)
imarray = numpy.array([imarray, numpy.array(im1)])
'''
class ImageSequence:
    def __init__(self, im):
        self.im = im
    def __getitem__(self, ix):
        try:
            if ix:
                self.im.seek(ix)
            return self.im
        except EOFError:
            raise IndexError # end of sequence

for frame in ImageSequence(im):
    # ...do something to frame...


for i in range (1, (imarray.shape[0])):
    for j in range (100, 150):
        imarray[i,j]=0 
'''        

#im = Image.fromarray(imarray)

def showTiff (myOpenedImage):
    photoim = ImageTk.PhotoImage(myOpenedImage)
    Button(image=photoim).pack()
    root.mainloop()

showTiff(im1)
