# -*- coding: utf-8 -*-
"""
Created on Tue Nov 11 22:47:51 2014

@author: Avilash
"""
#Finds the area within a simple polygon bounded n user determined points


from Tkinter import *  #Tkinter = python GUI package
from PIL import *  #Pillow = python image processing library
import ImageTk
import sys

canvas_width = 500
canvas_height = 900
#B-scans that we acquire on our system will be 6x6 or 12x12 mm
scale_factor_y = (2.0 / 792.0) #mm/pixel in y
scale_factor_x =  (2.0 / 375.0) #mm/pixel in x

class GUI_events:
    def __init__ (self, scale_factor_x, scale_factor_y, im1, photoim):
        self.count = 0 #keeps track of click #
        self.area = 0.0
        self.a_x = 0
        self.a_y = 0
        self.start_x = 0
        self.start_y = 0
        self.i = 0 #keeps track of slice #
        self.scale_factor_x = scale_factor_x
        self.scale_factor_y = scale_factor_y
        self.im1 = im1
        self.photoim = photoim
        self.perimeter = [] #scaled perimeter values (in mm)
        self.pixel_perimeter = [] #event coordinates (in pixels)
        
    def paint( self, event ):  #draws 
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
        else:
            canvas.create_oval( x1, y1, x2, y2, fill = my_color, tags="oval" )
            canvas.create_line(self.a_x, self.a_y, event.x, event.y, 
                               fill= my_color, tags="oval")
            self.a_x = event.x
            self.a_y = event.y        
            self.perimeter.append ( [(self.scale_factor_x * self.a_x),
                                     (self.scale_factor_y * self.a_y)] )
            self.pixel_perimeter.extend( (self.a_x, self.a_y) )
        return
        
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
        
    def erase( self, event ): #erases drawings
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
        
    def ChangeImageRight( self, event ): #move up through the stack
        if self.i < 178:
            self.i = self.i + 1
            self.im1.seek(self.i) #.seek(i) access the ith image in a stack
            self.photoim = ImageTk.PhotoImage(self.im1)
            canvas.delete(ALL)  #Make sure to delete or else the old images
                                #will be kept in memory
            canvas.create_image(20,20, anchor=NW, image=self.photoim)
            self.count = 0
        else: 
            self.i = 178       
        return 
        
    def ChangeImageLeft( self, event ):  #move down through the stack
        if self.i > 1:
            self.i = self.i - 1
            self.im1.seek(self.i)
            self.photoim = ImageTk.PhotoImage(self.im1)
            canvas.delete(ALL)
            canvas.create_image(20,20, anchor=NW, image=self.photoim)
            self.count = 0
        else:
            self.i = 1
        return 

master = Tk()
master.title( "Click region boundaries")  #Text that appears in window heading

canvas = Canvas(master, width=canvas_width, height=canvas_height)
im1 = Image.open('int1.tif')
photoim = ImageTk.PhotoImage(im1)  #I don't think it is possible to directly
                                   #display a .tif on the Tkinter canvas
gui_events = GUI_events(scale_factor_x, scale_factor_y, im1, photoim)

canvas.create_image(20,20, anchor=NW, image=photoim)
canvas.pack(expand = YES, fill = BOTH)
canvas.bind( "<Button-1>", gui_events.paint ) #binds drawing to LMB
canvas.bind( "<Button-3>", gui_events.erase ) #binds erasing to RMB
master.bind ("<Return>", gui_events.find_area) #enter to compute area
master.bind( "<Right>", gui_events.ChangeImageRight) #arrow keys to move                                               
master.bind( "<Left>", gui_events.ChangeImageLeft)   #through the stack

mainloop()


    