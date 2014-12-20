# -*- coding: utf-8 -*-
"""
Created on Fri Dec 19 22:49:36 2014

@author: Avilash
"""


from numpy import * 
from Tkinter import *  #Tkinter = python GUI package
from PIL import *  #Pillow = python image processing library.  THE STANDARD PIL
                   #WILL NOT WORK!
import ImageTk
import sys

import vtkTest5

def displayer (img):
    img = Image.open(img)
    rsFactor = 1
    img1 = img.resize( ( (int(img.size[0]*rsFactor)),(int(img.size[1]*rsFactor))) ,Image.ANTIALIAS)
    imarray = array(img1)
    img.seek(1)
    img1 = img.resize( ( (int(img.size[0]*rsFactor)),(int(img.size[1]*rsFactor))) ,Image.ANTIALIAS)
    imarray = array([imarray, array(img1)])
    for i in range(2,179):
        img.seek(i)
        img1 = img.resize( ( (int(img.size[0]*rsFactor)),(int(img.size[1]*rsFactor))) ,Image.ANTIALIAS)
        a = array(img1)
        imarray = concatenate((imarray, [a]), axis=0)
    data_matrix = (imarray).astype('uint8')
    return data_matrix
    
im1 = ('int1.tif')

canvas_width = 500
canvas_height = 500

#B-scans that we acquire on our system will be 6x6 or 12x12 mm
scale_factor_y = (2.0 / ( Image.open(im1).size[1])) #mm/pixel in y
scale_factor_x =  (2.0 / ( Image.open(im1).size[0])) #mm/pixel in x

class GUI_events:
    def __init__ (self, scale_factor_x, scale_factor_y, im):
        self.count = 10 #keeps track of click #
        self.area = 0.0
        self.a_x = 0
        self.a_y = 0
        self.start_x = 0
        self.start_y = 0
        self.i = 0 #keeps track of slice #
        self.scale_factor_x = scale_factor_x
        self.scale_factor_y = scale_factor_y
        self.im = im
        self.im1 = Image.open(im)
        self.photoim = ImageTk.PhotoImage(self.im1)
        self.data_matrix = displayer(self.im)
        self.perimeter = [] #scaled perimeter values (in mm)
        self.pixel_perimeter = [] #event coordinates (in pixels)
        self.axis = 'x'
        
    def Reslice_x (self, event ):
        self.axis = 'x'
        self.i = 0
        self.photoim = ImageTk.PhotoImage(Image.fromarray(self.data_matrix[self.i,:,:]))
        canvas.delete(ALL)  
        canvas.create_image(0,0, anchor=NW, image=self.photoim)
        self.count = 0

    def Reslice_y (self, event ):
        self.axis = 'y'
        self.i = 0
        self.photoim = ImageTk.PhotoImage(Image.fromarray(self.data_matrix[:,self.i,:]))
        canvas.delete(ALL)  
        canvas.create_image(0,0, anchor=NW, image=self.photoim)
        self.count = 0
    
    def Reslice_z (self, event ):
        self.axis = 'z'
        self.i = 0
        self.photoim = ImageTk.PhotoImage(Image.fromarray(self.data_matrix[:,:,self.i]))
        canvas.delete(ALL)  
        canvas.create_image(0,0, anchor=NW, image=self.photoim)
        self.count = 0
        
    def ChangeImageRight( self, event ): #move up through the stack
        if self.axis == 'x':
            if self.i < (int(gui_events.data_matrix.shape[0]) -1):
                self.i = self.i + 1
                self.photoim = ImageTk.PhotoImage(Image.fromarray(self.data_matrix[self.i,:,:]))
                canvas.delete(ALL) 
                canvas.create_image(0,0, anchor=NW, image=self.photoim)
                self.count = 0
            else: 
                self.i = (int(gui_events.data_matrix.shape[0]) -1)     
        elif self.axis == 'y':
            if self.i < (int(gui_events.data_matrix.shape[1]) -1):
                self.i = self.i + 1
                self.photoim = ImageTk.PhotoImage(Image.fromarray(self.data_matrix[:,self.i,:]))
                canvas.delete(ALL)
                canvas.create_image(0,0, anchor=NW, image=self.photoim)
                self.count = 0
            else: 
                self.i = (int(gui_events.data_matrix.shape[1]) -1)     
        else:
            if self.i < (int(gui_events.data_matrix.shape[2]) -1):
                self.i = self.i + 1
                self.photoim = ImageTk.PhotoImage(Image.fromarray(self.data_matrix[:,:,self.i]))
                canvas.delete(ALL) 
                canvas.create_image(0,0, anchor=NW, image=self.photoim)
                self.count = 0
            else: 
                self.i = (int(gui_events.data_matrix.shape[2]) -1) 
        return 
        
    def ChangeImageLeft( self, event ):  #move down through the stack
        if self.axis == 'x':
            if self.i > 0:
                self.i = self.i - 1
                self.photoim = ImageTk.PhotoImage(Image.fromarray(self.data_matrix[self.i,:,:]))
                canvas.delete(ALL) 
                canvas.create_image(0,0, anchor=NW, image=self.photoim)
                self.count = 0
            else: 
                self.i = 0     
        elif self.axis == 'y':
            if self.i > 0:
                self.i = self.i - 1
                self.photoim = ImageTk.PhotoImage(Image.fromarray(self.data_matrix[:,self.i,:]))
                canvas.delete(ALL)
                canvas.create_image(0,0, anchor=NW, image=self.photoim)
                self.count = 0
            else: 
                self.i = 0     
        else:
            if self.i > 0:
                self.i = self.i - 1
                self.photoim = ImageTk.PhotoImage(Image.fromarray(self.data_matrix[:,:,self.i]))
                canvas.delete(ALL) 
                canvas.create_image(0,0, anchor=NW, image=self.photoim)
                self.count = 0
            else: 
                self.i = 0
        return     

    def caliper_button ( self, event ): 
        self.count = 0
        canvas.bind( "<Button-1>", gui_events.draw_line ) #binds drawing to LMB
        canvas.bind( "<Button-3>", gui_events.erase ) #binds erasing to LMB
    
    def area_button ( self, event ):
        self.count = 0
        canvas.bind( "<Button-1>", gui_events.draw_boundary )
        canvas.bind( "<Button-3>", gui_events.erase )
        master.bind ("<Return>", gui_events.find_area)
    
    def seg_button (self, event ):
        print ("one moment please")
        sys.stdout.flush()
        rS.retinal_segmentation(self.im)
        print ("All done.  Close window to see segmentation")
        sys.stdout.flush()
        
    def threeD_button (self, event ):
        vtkTest5.displayer(self.im)
        print ("It's alive")

    def draw_line( self, event ):  
        my_color = "#ffa500"
        x1, y1 = ( event.x - 2 ), ( event.y - 2 )
        x2, y2 = ( event.x + 2 ), ( event.y + 2 )
        if self.count == 0:
            self.count = 1
            canvas.create_oval( x1, y1, x2, y2, fill = my_color, tags="oval" )
            self.a_x = event.x
            self.a_y = event.y
        elif self.count == 1:
            self.count = 2
            canvas.create_oval( x1, y1, x2, y2, fill = my_color, tags="oval" )
            self.b_x = event.x
            self.b_y = event.y        
            canvas.create_line(self.a_x, self.a_y, self.b_x, self.b_y, 
                               fill= my_color, tags="oval")
            print (((self.scale_factor_x * (self.a_x - self.b_x))**2 + 
                    (self.scale_factor_y * (self.a_y - self.b_y))**2)**.5)
            sys.stdout.flush() #otherwise there is an event lag (ipython thing)
        else:
            self.count = 0
            canvas.delete("oval")
        return

    def draw_boundary( self, event ):  #draws, records points
        my_color = "#ffa500"
        x1, y1 = ( event.x - 2 ), ( event.y - 2 )
        x2, y2 = ( event.x + 2 ), ( event.y + 2 )
        if self.count == 0:
            self.count = 1
            canvas.create_oval( x1, y1, x2, y2, fill = my_color, tags="oval" )
            self.start_x = event.x 
            self.a_x = event.x
            self.a_y = event.y
            self.start_y = event.y
            self.perimeter.append ( [(self.scale_factor_x * self.a_x),
                                     (self.scale_factor_y * self.a_y)] )
            self.pixel_perimeter.extend( (self.a_x, self.a_y) )
        
        elif self.count == 1:
            canvas.create_oval( x1, y1, x2, y2, fill = my_color, tags="oval" )
            canvas.create_line(self.a_x, self.a_y, event.x, event.y, 
                               fill= my_color, tags="oval")
            self.a_x = event.x
            self.a_y = event.y        
            self.perimeter.append ( [(self.scale_factor_x * self.a_x),
                                     (self.scale_factor_y * self.a_y)] )
            self.pixel_perimeter.extend( (self.a_x, self.a_y) )
        else:
            self.count = self.count
        return
        
    def on_escape (self, event):
        self.count = 10
        self.erase(event)
        canvas.unbind("<Button-1>")
        canvas.unbind("<Button-3>")
        canvas.unbind("<Return>")
        
    def find_area( self, event): #shoelace formula
        canvas.create_line(self.a_x, self.a_y, self.start_x, self.start_y, 
                               fill= "#ffa500", tags="oval") 
        canvas.create_polygon(self.pixel_perimeter,fill="#ffa500",stipple='gray12',tags='oval')
        n = len(self.perimeter)
        for i in range(n):
            i1 = (i+1)%n
            self.area += (self.perimeter[i][0]*self.perimeter[i1][1]
            - self.perimeter[i1][0]*self.perimeter[i][1])  
        self.area = 0.5 * abs(self.area)
        print 'area = ', self.area
        sys.stdout.flush() #otherwise there is an event lag (IPython thing)
        self.area = 0.0
        return
        
    def erase( self, event ): #erases drawings, resets
        canvas.delete("oval")
        self.area = 0.0
        self.count = 0
        self.a_x = 0
        self.a_y = 0
        self.start_x = 0
        self.start_y = 0
        self.perimeter = []
        self.pixel_perimeter = []
        return     
    
    
    
    
master = Tk()
fr = Frame(master)
master.title( "Avilash's reslice")  #Text that appears in window heading
gui_events = GUI_events(scale_factor_x, scale_factor_y, im1)

#creating the buttons
b = Button(fr, text="Caliper", anchor=NW, justify=LEFT, padx=2)
c = Button(fr, text="Area", anchor=NW, justify=LEFT, padx=2)
#d = Button(f, text="Segmentation", anchor=NW, justify=LEFT, padx=2)
e = Button(fr, text="3D Display", anchor=NW, justify=LEFT, padx=2)
f = Button(fr, text="Reslice: X", anchor=NW, justify=LEFT, padx=2)
g = Button(fr, text="Reslice: Y", anchor=NW, justify=LEFT, padx=2)
h = Button(fr, text="Reslice: Z", anchor=NW, justify=LEFT, padx=2)
b.pack(anchor=NW, side=LEFT)
c.pack(anchor=NW, side=LEFT)
#d.pack(anchor=NW, side=LEFT)
f.pack(anchor=NW, side=LEFT)
g.pack(anchor=NW, side=LEFT)
h.pack(anchor=NW, side=LEFT)
e.pack(anchor=NW, side=LEFT)

canvas = Canvas(master, width=canvas_width, height=canvas_height)
canvas.create_image(0, 0, anchor=NW, image=gui_events.photoim) 
fr.pack(anchor=NW)
canvas.pack(anchor=NW)

#Button bindings
b.bind("<Button-1>", gui_events.caliper_button )
c.bind("<Button-1>", gui_events.area_button )
#d.bind("<Button-1>", gui_events.seg_button )
e.bind("<Button-1>", gui_events.threeD_button )
f.bind("<Button-1>", gui_events.Reslice_x )
g.bind("<Button-1>", gui_events.Reslice_y )
h.bind("<Button-1>", gui_events.Reslice_z )

#Keyboard bindings
master.bind( "<Escape>", gui_events.on_escape ) #binds erasing to RMB
master.bind( "<Right>", gui_events.ChangeImageRight) #arrow keys to move                                               
master.bind( "<Left>", gui_events.ChangeImageLeft)   #through the stack

mainloop()


    
