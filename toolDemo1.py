# -*- coding: utf-8 -*-
"""
Created on Tue Dec 09 23:03:46 2014

@author: Avilash
"""

from Tkinter import *  #Tkinter = python GUI package
from PIL import *  #Pillow = python image processing library
from PIL import Image
import ImageTk
import sys
import retSeg2 as rS

canvas_width = 500
canvas_height = 900
#B-scans that we acquire on our system will be 6x6 or 12x12 mm
scale_factor_y = (2.0 / 792.0) #mm/pixel in y
scale_factor_x =  (2.0 / 375.0) #mm/pixel in x


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
        self.perimeter = [] #scaled perimeter values (in mm)
        self.pixel_perimeter = [] #event coordinates (in pixels)

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
        print ("hi")
        rS.retinal_segmentation(self.im)
        sys.stdout.flush()
        return
        
    def draw_line( self, event ):  #draws 
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

    def draw_boundary( self, event ):  #draws 
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

im1 = ('testfiles/int1.tif')
#photoim = ImageTk.PhotoImage(im1)  #I don't think it is possible to directly
#display a .tif on the Tkinter canvas

#rS.retinal_segmentation(im1)
gui_events = GUI_events(scale_factor_x, scale_factor_y, im1)

b = Button(master, text="Caliper", anchor=W, justify=LEFT, padx=2)
b.pack(side=LEFT, expand=1)
c = Button(master, text="Area", anchor=W, justify=LEFT, padx=2)
c.pack(side=LEFT, expand=1)
d = Button(master, text="Segmentation", anchor=W, justify=LEFT, padx=2)
d.pack(side=LEFT, expand=1)

canvas.create_image(20,20, anchor=NW, image=gui_events.photoim)
canvas.pack(expand = YES, fill = BOTH)
b.bind("<Button-1>", gui_events.caliper_button )
c.bind("<Button-1>", gui_events.area_button )
d.bind("<Button-1>", gui_events.seg_button )
#canvas.bind( "<Button-1>", gui_events.draw_boundary ) #binds drawing to LMB
master.bind( "<Escape>", gui_events.on_escape ) #binds erasing to RMB
#master.bind ("<Return>", gui_events.find_area) #enter to compute area
master.bind( "<Right>", gui_events.ChangeImageRight) #arrow keys to move                                               
master.bind( "<Left>", gui_events.ChangeImageLeft)   #through the stack

mainloop()


    
