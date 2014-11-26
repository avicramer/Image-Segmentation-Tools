# -*- coding: utf-8 -*-
"""
Created on Mon Nov 10 22:44:55 2014

@author: Avilash
"""

# -*- coding: utf-8 -*-
"""
Created on Sun Nov 09 23:08:54 2014

@author: Avilash
"""

from Tkinter import *  #Tkinter = python GUI package
from PIL import *  #Pillow
import ImageTk
import sys #Needed for flush

canvas_width = 500
canvas_height = 900
#B-scans that we acquire on our system will be 6x6 or 12x12 mm
scale_factor_y = (2.0 / 792.0) #mm/pixel in y
scale_factor_x =  (2.0 / 375.0) #mm/pixel in x

# The tricky part here is figuring out how to pass in variables to the event
# binding.  I originally did this by declaring all my variables global, but 
# that seemed like poor practice and had to be done in within each function.
# The class system seemed more Pythonic, but a third option would be to pass 
# anonymous (lambda) functions into the bindings.

class GUI_events:
    def __init__ (self, scale_factor_x, scale_factor_y, im1, photoim):
        self.count = 0 #keeps track of click #
        self.a_x = 0
        self.a_y = 0
        self.b_x = 0
        self.b_y = 0
        self.i = 0 #keeps track of slice #
        self.scale_factor_x = scale_factor_x
        self.scale_factor_y = scale_factor_y
        self.im1 = im1
        self.photoim = photoim
    def paint( self, event ):  #draws 
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
    def erase( self, event ): #erases drawings
        canvas.delete("oval")
        self.count = 0
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
canvas.bind( "<Button-3>", gui_events.erase ) #binds erasing to LMB
master.bind( "<Right>", gui_events.ChangeImageRight) #arrow keys
master.bind( "<Left>", gui_events.ChangeImageLeft)

mainloop()
