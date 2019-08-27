#!/usr/bin/env python3
# v. 27-08-2019 B
"""
JUST FOR FUN
"""
import tkinter as tk
import tkinter.ttk as ttk
import tkinter.font as tkf
from tkinter import messagebox
import math
import os
import sys
from TkinterDnD2 import *
import time
import json
import pyinotify
from pathlib import Path

# the list: rect width, rect height, left pad (wpadx), right pad (wpady),
#... the background color of canvas, rect default colour,
#... highlight rect colour, icon size, font family of each widget,
#... font size of each widget, default font size of other elements and widgets,
#... reserved top space, reserved bottom space, reserved left space, reserved right space
#... desktop font colour;
canvas_config = [180, 150, 20, 20,
                 "gray70", "light gray",
                 "PaleGreen2", 96, "",
                 20, 20, 
                 50, 100, 50, 50,
                 "black"]
# the working dir
working_dir = os.path.realpath("DATA")
canvas_data = [working_dir]
# the image used as background
canvasBackground = "bg2.gif"
# 
screen_width = 0
screen_height = 0

# the list: each entry in the item_position.cfg file (dict)
list_position = []

# create the file if it not exists
if not os.path.exists("item_position.cfg"):
    Path("item_position.cfg").touch()

with open("item_position.cfg", "r") as f:
    rl = f.readline()
    while rl:
        try:
            # convert string to dict
            list_position.append(json.loads(rl))
            rl = f.readline()
        except:
            f.close()
            os.remove("item_position.cfg")
            list_position = []
            Path("item_position.cfg").touch()
            #
            break

# Watch Manager
wm = pyinotify.WatchManager()
# watched events
flags = pyinotify.IN_DELETE | pyinotify.IN_CREATE | pyinotify.IN_MODIFY | pyinotify.IN_MOVED_FROM | pyinotify.IN_MOVED_TO

# binding for stopping
notifier = object

## indicators
# item added
prog_mod = 0
# item modificated
prog_var = 0
# item deleted
prog_del = 0
# files changed
file_to_change = []

####### main class
class Application(ttk.Frame):
    
    def __init__(self, master=None, k=None, dd=None):
        super().__init__(master)
        self.master = master
        self.k = k
        self.dd = dd
        # working dir
        self.working_dir = self.dd[0]
        
        self.pack(fill="both", expand=True)
        
        # font size to all widgets except popup
        self.s = ttk.Style()
        self.s.configure('.', font=('', self.k[9]))
        
        ## the text height related to the font and size used
        t_Font = tkf.Font(family='', size=self.k[10])
        self.linespace = t_Font.metrics("linespace")

        #
        self.master.update_idletasks()
        ##### PYINOTIFY 
        class EventHandler(pyinotify.ProcessEvent):
            
            def __init__(self2):
                pass
                
            def process_IN_CREATE(self2, event):
                print("Creating:", event.pathname)
                # repopulate canvas
                global prog_mod
                prog_mod = 1
                # repopulate canvas
                self.checkVariations(event.name)
            def process_IN_DELETE(self2, event):
                print("Removing:", event.pathname)
                global prog_del
                prog_del = 1
                # change the canvas
                self.checkVariations(event.name)
            def process_IN_MODIFY(self2, event):
                print("Modifying:", event.pathname)
                
            def process_IN_MOVED_FROM(self2, event):
                print("Moving from:", event.pathname)
                # renaming or moving
                global prog_var
                prog_var = 1
                global file_to_change
                file_to_change = []
                file_to_change.append(event.name)
                # repopulate canvas
                self.checkVariations()
            def process_IN_MOVED_TO(self2, event):
                print("Moving to:", event.pathname)
                global prog_var
                # repopulate canvas if not renaming
                if prog_var == 0:
                    global prog_mod
                    prog_mod = 1
                # if renaming
                elif prog_var == 1:
                    prog_var = 2
                    global file_to_change
                    file_to_change.append(event.name)
                # repopulate canvas
                self.checkVariations()
                
        
        global notifier
        handler = EventHandler()
        notifier = pyinotify.ThreadedNotifier(wm, handler)
        wdd = wm.add_watch(self.working_dir, flags, rec=True)
        notifier.start()
        
        #
        self.create_widgets()
   
    ###
    
    def checkVariations(self, item=None):
        global prog_mod
        global prog_var
        global prog_del
        # for create
        if prog_mod == 1:
            self.createItem(item)
            # reset
            prog_mod = 0
        # for renaming: moved_to and moved_from
        if prog_var == 2:
            self.renameItem(file_to_change)
            prog_var = 0
        # for delete
        if prog_del == 1:
            self.deleteItem(item)
            prog_del = 0

    # create an item
    def createItem(self, nitem):
        # if the item exists
        for item in list_position:
            if item["name"] == nitem:
                print("the file {} already exists".format(nitem))
                return
        # create the item
        self.create_the_item(nitem)
        

    # related to the previous function
    def create_the_item(self, nitem):
        
        # rect dimensions
        ww = self.k[0]
        wh = self.k[1]
        # space between the rects and from the borders
        wpadx = self.k[2]
        wpady = self.k[3]
        # reserved space at top, at bottom, at left and at right
        tpad = self.k[11]
        bpad = self.k[12]
        lpad = self.k[13]
        rpad = self.k[14]
        # number of rect per row
        num_rect_row = int((self.dim_w-lpad-rpad)/(wpadx+ww))
        # max lines 
        num_row = int((self.dim_h-tpad-bpad)/(wpady+wh+(self.linespace*2)))
        # max items to allocate - one reserved to recycle bin
        num_max = (num_row * num_rect_row) - 1
        # if too much items print a message
        if len(list_position) > num_max:
            print("the item cannot be displayed")
            return
        #
        # add the item
        # list of item names already processed
        old_items = []
        for item in list_position:
            old_items.append(item["name"])
        
        # check if el is a new item
        if nitem not in old_items:
            ret = self.allocateNewItem(num_row, num_rect_row)
            rr = ret[0]
            r = ret[1]

            dict = self.arrange_item(lpad, tpad, wpadx, wpady, ww, wh, r, rr, nitem)
            # write the new item in the config file
            fin = open("item_position.cfg", "rt")
            fout = open("item_position.cfg_temp", "wt")
            for line in fin:
                # from string to dict
                lline = json.loads(line)
                fout.write(line)
            fout.write(json.dumps(dict))
            fout.write("\n")
            fin.close()
            fout.close()
            #
            os.remove("item_position.cfg")
            os.rename("item_position.cfg_temp", "item_position.cfg")
            # used as tag
            self.ii += 1
            #
            # add the item to list_position
            list_position.append(dict)
            ## renew the lists of folders and files
            # with full path
            self.d = self.create_list_of_items()
            # only filename
            self.d2 = self.create_list_of_items2()
            # renew the list of cell occupied
            self.list_cellOcc = []
            self.cellOcc()

    
    # delete the item
    def deleteItem(self, nitem):
        for item in list_position:
            if item["name"] == nitem:
                # remove the entry in the file
                fin = open("item_position.cfg", "rt")
                fout = open("item_position.cfg_temp", "wt")
                for line in fin:
                    # from string to dict
                    lline = json.loads(line)
                    if not lline["name"] == nitem: 
                        fout.write(line)
                fin.close()
                fout.close()
                # restore the file
                os.remove("item_position.cfg")
                os.rename("item_position.cfg_temp", "item_position.cfg")
                ## reset
                #global file_to_change
                #file_to_change = []
                # delete the item
                self.delete_the_item(item)
                ##
                #break
    
    # related to the previous function
    def delete_the_item(self, item):
        posx = int(item["x"])
        posy = int(item["y"])
        # 
        x1 = self.k[13] + (self.k[2] + self.k[0]) * (posy)
        y1 = self.k[11] + (self.k[3] + self.k[1]) * (posx)
        x2 = x1 + self.k[0]
        y2 = y1 + self.k[1] + self.linespace*2

        item_objects = self.w.find_overlapping(x1,y1,x2,y2)
        print("RI_items_objects::", item_objects)
        # remove all the objects - 1 is the background image
        for el in item_objects:
            if el != 1:
                self.w.delete(el)
                # remove the ids from the lists
                if el in self.rectangle_list:
                    self.rectangle_list.remove(el)
                if el in self.image_list:
                    self.image_list.remove(el)
                if el in self.text_list:
                    self.text_list.remove(el)
        
        # remove item from list_position
        list_position.remove(item)
        ## renew the lists of folders and files
        # with full path
        self.d = self.create_list_of_items()
        # only filename
        self.d2 = self.create_list_of_items2()
        # renew the list of cell occupied
        self.list_cellOcc = []
        self.cellOcc()
        
        return


    # list of file and folder in the working dir with absolute path
    def create_list_of_items(self):
        item_list = []
        list_file = os.listdir(self.working_dir)
        for ffile in list_file:
            item_list.append(os.path.join(self.working_dir, ffile))
   
        return item_list

    # list of folder and file in the working dir - only filename
    def create_list_of_items2(self):
        item_list = []
        
        # from self.d - see the previous function
        for item in self.d:
            item_list.append(os.path.basename(item))
        return item_list

    def create_widgets(self):
        
        ########### canvas
        self.w = tk.Canvas(self)
        self.w.configure(bg=self.k[4])
        self.w.pack(side="left", fill="both", expand=True)
        
        ####### mouse operations
        # LMB
        self.w.bind("<Button-1>", self.mouseDown)
        self.w.bind("<Button1-Motion>", self.mouseMotion)
        self.w.bind("<Button1-ButtonRelease>", self.mouseUp)
        self.w.bind("<Double-Button-1>", self.mouseDoubleDown)
        # RMB
        self.w.bind("<Button-3>", self.mouseRDown)
        # Ctrl+LMB - pressed and released
        self.w.bind("<Control-Button-1>", self.CmouseLDown)
        self.w.bind("<Control-Button1-ButtonRelease>", self.CmouseLUp)
        ##
        #self.bind("<Button1-ButtonRelease>", self.fmouseUp)
        ####### DnD
        # add a boolean flag to the canvas which can be used to disable
        # files from the canvas being dropped on the canvas again
        self.dragging = False
        # DROP
        self.drop_target_register(DND_FILES)
        self.dnd_bind('<<DropEnter>>', self.drop_enter)
        self.dnd_bind('<<DropPosition>>', self.drop_position)
        self.dnd_bind('<<DropLeave>>', self.drop_leave)
        self.dnd_bind('<<Drop>>', self.drop)
        # DRAG
        self.w.drag_source_register(1, DND_FILES)
        self.w.dnd_bind('<<DragInitCmd>>', self.drag_init)
        self.w.dnd_bind('<<DragEndCmd>>', self.drag_end)
   
        ########### rubberband
        # the rubberband
        self.rubberbandBox = None
        # the mouse moves around canvas
        self.w.bind('<Motion>', self.cMotion)
   
        ###########
        self.w.pack(side="left", fill="both", expand=True)
        # add the background image
        self.cbackground = tk.PhotoImage(file=canvasBackground)
        self.idbg = self.w.create_image(0, 0, image=self.cbackground, anchor=tk.NW, tags=("cbackground", ))
        # populate the canvas
        self.populate_canvas()
        self.w.focus_force()

    #
    def cMotion(self, event):
        cx = self.w.canvasx(event.x)
        cy = self.w.canvasy(event.y)
    
    def populate_canvas(self):
        ## lists of folders and files
        # with full path
        self.d = self.create_list_of_items()
        # only filename
        self.d2 = self.create_list_of_items2()
        
        # MLB
        self.button1_mouse = 0
   
        # dragging with the mouse
        self.drag_mouse = 0
   
        # CTRL+LMB - select one item at time
        self.ctrl_lmb = 0
   
        # list of all canvas object except the background image
        self.list_all_canvas_object = []
   
        # list of selected items by mouse
        self.dragged_items = []
   
        # list of all id of the rects created
        self.rectangle_list = []
   
        # list of all if of the icons added
        self.image_list = []
           
        # list of the text id
        self.text_list = []
   
        # rect selected: LMB down
        self.rect_selected = 0
   
        # the DnD starts
        self.items_dragged_for_dropped = 0
   
        # the drop terminated in the canvas
        self.drop_in_canvas = 0
   
        # Frame dimensions
        self.dim_w = self.winfo_width()
        self.dim_h = self.winfo_height()
   
        # rect dimensions
        ww = self.k[0]
        wh = self.k[1]
        # space between the rects and from the borders
        wpadx = self.k[2]
        wpady = self.k[3]
        # reserved space at top, at bottom, at left and at right
        tpad = self.k[11]
        bpad = self.k[12]
        lpad = self.k[13]
        rpad = self.k[14]
   
        # list of the image objects
        self.img_list = []
   
        # list of images
        self.fcreate_image_list()
   
        # list of cell occupied - list of tuples
        self.list_cellOcc = []
        # ... and the function
        self.cellOcc()
        
        ########
        # amount of rects to insert
        num_rect = len(self.d)
        print("Items to add:", num_rect)
        # number of rect per row
        num_rect_row = int((self.dim_w-lpad-rpad)/(wpadx+ww))
        print("Number of rect for each lins: ", num_rect_row)
        # max lines 
        num_row = int((self.dim_h-tpad-bpad)/(wpady+wh+(self.linespace*2)))
        print("Max number of lines: ", num_row)
        # lines needed
        num_row2 = math.ceil(num_rect/num_rect_row)
        print("Number of lines: ", num_row2)
        #
        # if the item in the folder is gt than the number of cell print a message
        if len(self.d) > ((num_row * num_rect_row) - 1):
            print("Warning, too many items to add!")
        
        # open the file item_position
        f = open("item_position.cfg", "r+")
        
        global list_position
        # copy of the list of dicts
        list_position2 = list_position
        # ... and reset the original list
        list_position = []
        
        # used as tag of each element
        self.ii = 1
        
        # if the file item_position.cfg is empty create the file
        if os.stat("item_position.cfg").st_size == 0:
            # for each row - x in list_position
            for rr in range(num_row):
                # for each column - y in list_position
                for r in range(num_rect_row):
                    # the last cell is reserved to the recycle bin
                    if rr == num_row -1 and r == num_rect_row - 1:
                        print("too many items to add")
                        break
                        
                    if (self.ii-1) < num_rect:
                        rtext = os.path.basename(self.d[self.ii-1])
                        # the position in the list if it exists
                        for item in list_position:
                            if item["name"] == rtext:
                                rr = int(item["x"])
                                r = int(item["y"])
                        dict = self.arrange_item(lpad, tpad, wpadx, wpady, ww, wh, r, rr, rtext)
                        # write into the file item_position.cfg
                        list_position.append(dict)
                        f.write(json.dumps(dict))
                        f.write("\n")
                        
                        self.ii += 1
                    else:
                        break
        # if not empty
        else:
            # max items to allocate - one reserved to recycle bin
            num_max = (num_row * num_rect_row) - 1
            ## 
            # if too much items print a message
            if len(list_position) > num_max:
                print("some items cannot be displayed")
                messagebox.showinfo("Info", "Some items cannot be displayed.")
            #
            for item2 in self.d2:
                # old items
                for item in list_position2[0:num_max]:
                    if item["name"] == item2:
                        rtext = item["name"]
                        rr = int(item["x"])
                        r = int(item["y"])
                        # if the position is outside the grid
                        # empty the config file and repopulate
                        if rr > num_row -1 or r > num_rect_row - 1:
                            print("the desktop is smaller, need to repopulate")
                            f.close()
                            os.remove("item_position.cfg")
                            list_position = []
                            Path("item_position.cfg").touch()
                            self.delete_all_items_and_populate()
                            return
                        
                        dict = self.arrange_item(lpad, tpad, wpadx, wpady, ww, wh, r, rr, rtext)
                        # write into the file item_position.cfg
                        list_position.append(dict)
                        f.write(json.dumps(dict))
                        f.write("\n")
                        # used as tag
                        self.ii += 1
                        #
                        break
            # new items
            # list of item names already processed
            old_items = []
            for item in list_position:
                old_items.append(item["name"])
            #
            if len(list_position2) < num_max:
                num_el = num_max - len(list_position2)
                #
                for el in self.d2:
                    # if not room in the desktop exit
                    if num_el == 0:
                        break
                    # check if el is a new item
                    if el not in old_items:
                        ret = self.allocateNewItem(num_row, num_rect_row)
                        rr = ret[0]
                        r = ret[1]

                        dict = self.arrange_item(lpad, tpad, wpadx, wpady, ww, wh, r, rr, el)
                        # write into the file item_position.cfg
                        list_position.append(dict)
                        f.write(json.dumps(dict))
                        f.write("\n")
                        # used as tag
                        self.ii += 1
                        #
                        num_el -= 1

           
        # close the file item_position.cfg
        f.close()
        
        ### add the recycle bin item
        
        # add the text
        x1 = lpad+(wpadx+ww)*(num_rect_row-1)+wpadx+(self.k[0]/2)
        y1 = tpad+(wpady+wh)*(num_row-1)+wh+wh
        rbtext = "Bin"
        #self.w.create_text(x1, y1, text="Bin", font=(self.k[8], self.k[9]+1, "bold"), justify="center", width=self.k[0]-20, anchor="n", fill="white")
        self.w.create_text(x1+1, y1+1, text=rbtext, font=(self.k[8], self.k[9]), justify="center", anchor="n", fill="white")
        idt = self.w.create_text(x1, y1, text=rbtext, font=(self.k[8], self.k[9]), justify="center", width=self.k[0]-20, anchor="n", fill=self.k[15], tags=(-1, "bin"))
        
        # add the rectangle
        x1 = lpad+(wpadx+ww)*(num_rect_row-1) + wpadx
        y1 = tpad+(wpady+wh+(self.linespace*2))*(num_row-1) + wpady
        x2 = x1 + ww
        y2 = y1 + wh + self.linespace#*2
        #idr = self.w.create_rectangle(x1, y1, x2, y2, fill=self.k[5], outline="black", tags=(-1, "bin"))
        idr = self.w.create_rectangle(x1, y1, x2, y2, fill="", outline="", tags=(-1, "bin"))
        self.w.tag_lower(idr)
        
        # add the image - self.k[7] icon size
        x1 = lpad+(wpadx+ww)*(num_rect_row-1)+wpadx+(ww-self.k[7])/2
        y1 = tpad+(wpady+wh)*(num_row-1)+wh+(wh-self.k[7])/2
        self.bin_image = tk.PhotoImage(file="icons/trash.png")
        self.w.create_image(x1, y1, image=self.bin_image, anchor="nw", tags=(-1, "bin"))
        
        ### set the wallpaper in the background
        self.w.tag_lower(self.idbg)
        # update canvas
        self.update()
        # pointer position while dragging
        self.xpos = 0
        self.ypos = 0

    # create a list of grid cell occupied
    def cellOcc(self):
        for item in list_position:
            self.list_cellOcc.append((item["x"], item["y"]))
    
    # num_row is x (row) - num_rect_row is y (column)
    def allocateNewItem(self, num_row, num_rect_row):
        #
        i = 0
        ii = 0
        
        while i < num_row:
            while ii < num_rect_row:
                if not (str(i), str(ii)) in self.list_cellOcc:
                    # put the tuple in the list
                    self.list_cellOcc.append((str(i), str(ii)))
                    return [i, ii]
                else:
                    ii += 1
            i += 1

    # function to populate the canvas
    def arrange_item(self, lpad, tpad, wpadx, wpady, ww, wh, r, rr, rtext):
        #
        ## add the text
        x1 = lpad+(wpadx+ww)*(r) + wpadx
        y1 = tpad+(wpady+wh+(self.linespace*2))*(rr) + wpady
        rect_height_text = self.add_text(x1, y1, rtext)
        #
        ## add the rect
        fill = self.k[5]
        # x column - y row
        x2r = x1 + ww
        y2r = y1 + wh + rect_height_text
        self.add_rect(x1, y1, x2r, y2r, fill, rtext)
        #
        ## add immage
        item_path = os.path.join(self.working_dir, rtext)
        # if folder
        if os.path.isdir(item_path):
            item_image = self.img_list[0]
        # if file
        elif os.path.isfile(item_path):
            item_image = self.img_list[1]
        #
        img_padx = (self.k[0]-self.k[7])/2
        img_pady = (self.k[1]-self.k[7])/2
        self.add_image(x1+img_padx, y1+img_pady, item_image, self.ii)
        # return the dict
        dict = {"x":"{}".format(str(rr)), "y":"{}".format(str(r)), "name":"{}".format(rtext)}
        #
        return dict
        

########## ITEM CREATION

    # remove all the elements in canvas except the background and repopulate it
    def delete_all_items_and_populate(self):
        for iid in self.list_all_canvas_object:
            self.w.delete(iid)
        self.update()
        self.populate_canvas()

    # rename the item
    def renameItem(self, rfile):
        for item in list_position:
            if item["name"] == rfile[0]:
                item["name"] = rfile[1]
                # replace the text in the file
                fin = open("item_position.cfg", "rt")
                fout = open("item_position.cfg_temp", "wt")
                for line in fin:
                    fout.write(line.replace(rfile[0], rfile[1]))
                fin.close()
                fout.close()
                # restore the file
                os.remove("item_position.cfg")
                os.rename("item_position.cfg_temp", "item_position.cfg")
                # reset
                global file_to_change
                file_to_change = []
                # rename the item
                self.rename_the_item(item, rfile[1])
                #
                break
    
    # related to the previous function
    def rename_the_item(self, item, new_name):
        posx = int(item["x"])
        posy = int(item["y"])
        ## find the id of the related text object in canvas
        x_pos = self.k[13] + (self.k[2] + self.k[0]) * (posy) + self.k[0]/2
        y_pos = self.k[11] + (self.k[3] + self.k[1]) * (posx) + self.k[1]/2
        # find all the objects in the point
        item_objects = self.w.find_overlapping(x_pos, y_pos, x_pos, y_pos)
        # find the id of the text object
        rect_id = item_objects[1]
        rbbox = self.w.bbox(rect_id)
        # all the objects in the box
        item_objects2 = self.w.find_overlapping(rbbox[0], rbbox[1], rbbox[2], rbbox[3])
        for el in item_objects2:
            if el in self.text_list:
                self.w.itemconfigure(el, text=new_name)
                break
    
    # the rect
    def add_rect(self, x1, y1, x2, y2, ifill, item_name):
        radius=9
        points = [x1+radius, y1,
                  x1+radius, y1,
                  x2-radius, y1,
                  x2-radius, y1,
                  x2, y1,
                  x2, y1+radius,
                  x2, y1+radius,
                  x2, y2-radius,
                  x2, y2-radius,
                  x2, y2,
                  x2-radius, y2,
                  x2-radius, y2,
                  x1+radius, y2,
                  x1+radius, y2,
                  x1, y2,
                  x1, y2-radius,
                  x1, y2-radius,
                  x1, y1+radius,
                  x1, y1+radius,
                  x1, y1]
        # rounded rectangle
        id = self.w.create_polygon(points, fill="", outline="", smooth=True, tags=(self.ii, item_name), stipple="gray50")
        #id = self.w.create_rectangle(x1, y1, x2, y2, fill="", outline="", tags=(self.ii, item_name), stipple="gray50")
        #id = self.w.create_rectangle(x1, y1, x2, y2, fill=ifill, outline="black", tags=(self.ii, item_name))
        self.w.tag_lower(id)
        self.rectangle_list.append(id)
        # add to list all the objects
        self.list_all_canvas_object.append(id)

    # file and folder icons
    def fcreate_image_list(self):
        self.image = tk.PhotoImage(file="icons/folder.png")
        self.img_list.append(self.image)
        self.image = tk.PhotoImage(file="icons/file.png")
        self.img_list.append(self.image)

    # the icon
    def add_image(self, x, y, image, n):
        id = self.w.create_image(x, y, image=image, anchor="nw")
        # add id to list
        self.image_list.append(id)
        # add to list all the objects
        self.list_all_canvas_object.append(id)

    # the text 
    def add_text(self, x, y, rtext):
        ttext = self.truncate_text(rtext)
        #self.w.create_text(x+(self.k[0]/2)+1, y+self.k[1]+1, text=ttext, font=(self.k[8], self.k[9]), justify="center", anchor="n", width=self.k[0]-20, fill="white")
        id = self.w.create_text(x+(self.k[0]/2), y+self.k[1], text=ttext, font=(self.k[8], self.k[9]), justify="center", anchor="n", width=self.k[0]-20, fill=self.k[15])
        id_box = self.w.bbox(id)
        id_height = id_box[3]-id_box[1]
        # add id to list all the objects
        self.list_all_canvas_object.append(id)
        # add id to the text objects list
        self.text_list.append(id)
        
        return id_height

    # the text in two lines max
    def truncate_text(self, text):
        size_font = self.k[10]
        t_Font = tkf.Font(family='', size=size_font)
        text_width = t_Font.measure(text)
        max_text_width = self.k[0]-20
        new_text = ""
        text_temp = text[0]
        list_text_temp = []
        if text_width > max_text_width:
            for chr in text[1:]:
                ssize = t_Font.measure(text_temp + chr)
                
                if ssize > max_text_width:
                    new_text += text_temp+"\n"
                    list_text_temp.append(text_temp)
                    text_temp = chr
                    
                else:
                    if (new_text + text_temp + chr).replace("\n","") == text:
                        new_text += text_temp + chr
                        list_text_temp.append(text_temp + chr)
                    else:
                        text_temp += chr
        else:
            list_text_temp.append(text)
        
        #return list_text_temp
        #
        if len(list_text_temp) > 2:
            return list_text_temp[0]+"\n"+list_text_temp[1][0:-3]+"..."
        elif len(list_text_temp) == 2:
            return list_text_temp[0]+"\n"+list_text_temp[1]
        elif len(list_text_temp) == 1:
            return list_text_temp[0]

######## END ITEM CREATION

##### DRAG AND DROP

## DRAG

    # drag methods
    def drag_init(self, event):
        
        # the variabie
        self.items_dragged_for_dropped = 1
   
        # if there are selected items
        if self.dragged_items:
            # the list of the elements
            data = ()
            for item in self.dragged_items:
                file_name = self.w.gettags(item)[1]
                print("TAGS::", self.w.gettags(item))
                item_data = (os.path.join(self.working_dir, file_name), )
                data += item_data
           
            print("Selected for drag and drop: ", data)
            
            self.dragging = True
            return ((COPY, MOVE), DND_FILES, data)

    
    def drag_end(self, event):

        self.items_dragged_for_dropped = 0
        # reset the "dragging" flag to enable drops again
        self.dragging = False
        

## DROP

    # drop methods
    def drop_enter(self, event):
        event.widget.focus_force()
        return event.action

    def drop_position(self, event):
        return event.action

    def drop_leave(self, event):
        return event.action

    def drop(self, event):
        global screen_width
        global screen_height
        # drag e drop in the same program
        if self.dragging:
            # set the variable
            self.drop_in_canvas = 1
            # reset 
            self.dragging == False
            #
            ##### when the pointer has been released
            # item dragged
            dragged_item = self.w.find_overlapping(self.startx, self.starty, self.startx, self.starty)
            print("drop2_dragged_item::", dragged_item)
            ### if on background 
            selected_item = self.w.find_overlapping(self.xpos, self.ypos, self.xpos, self.ypos)
            print("drop2_selected_item::", selected_item)
            # if the drop ends on the background
            if len(selected_item) == 1:
                if selected_item[0] == 1:
                    print("is_background")
                    # if not more than one item selected
                    if len(self.dragged_items) == 1:
                        # move the item into another destination
                        # dragged item
                        drag_item = dragged_item[1]
                        # the coords box of item dragged
                        ibbox = self.w.bbox(drag_item)
                        ix = ibbox[0]
                        iy = ibbox[1]
                        #### drag the item in the grid
                        
                        # rect dimensions
                        ww = self.k[0]
                        wh = self.k[1]
                        # space between the rects and the borders
                        wpadx = self.k[2]
                        wpady = self.k[3]
                        # reserved space at top, at bottom, at left and at right
                        tpad = self.k[11]
                        bpad = self.k[12]
                        lpad = self.k[13]
                        rpad = self.k[14]
 
                        # amount or rect to insert
                        num_rect = len(self.d)
                        # number of rect per row
                        num_rect_row = int((self.dim_w-lpad-rpad)/(wpadx+ww))
                        # number of lines max
                        num_rrow = int(self.dim_h/(wpadx*2+wh+(self.linespace*2)+tpad+bpad))
                        # lines to use
                        num_row = math.ceil(num_rect/num_rect_row)
                        #
                        ###
                        print("XYPOS::", self.xpos, self.ypos)
                        
                        sc_w = screen_width - lpad - rpad
                        sc_h = screen_height - tpad - bpad
                        # wpadx wpady self.linespace*2
                        
                        # space occupied by each cell
                        cell_w = ww + wpadx
                        cell_h = wh + self.linespace*2 + wpady
                        
                        # grid position - float
                        xx = (self.xpos - lpad) / cell_w
                        yy = (self.ypos - tpad) / cell_h
                        # grid position - int
                        pos_x = int(xx) # column
                        pos_y = int(yy) # row
                        # if off the canvas do nothing
                        if pos_x > (num_rect_row-1) or pos_y > num_rrow or pos_x < 0 or pos_y <0:
                            print("off the border::", num_rect_row)
                            return 'break'
                        # if the cell is occupied do nothing
                        item = self.w.find_overlapping(self.xpos-wpadx, self.ypos-self.linespace-wpady, self.xpos, self.ypos)
                        if item and len(item) > 1:
                            print("Item found::", self.w.gettags(item[1]))
                            return 'break'
                        
                        coord_x = lpad + (wpadx+self.k[0])*pos_x + wpadx
                        coord_y = tpad + (wpady+self.k[1]+(self.linespace*2))*pos_y + wpady
                        #### move the item
                        # rectangle
                        self.w.move(drag_item, coord_x - ix, coord_y - iy)
                        # icon
                        self.w.move(drag_item+1, coord_x - ix, coord_y - iy)
                        # text
                        self.w.move(drag_item-1, coord_x - ix, coord_y - iy)
                        # update the file item_position.cfg
                        item_name = self.w.gettags(dragged_item[1])[1]
                        global list_position
                        for item in list_position:
                            if item["name"] == item_name:
                                # update the item in the list
                                item["y"] = str(pos_x) # row
                                item["x"] = str(pos_y) # column
                        
                        # write into the file the updated data
                        f = open("item_position.cfg", "w")
                        for item in list_position:
                            print("added::", item)
                            f.write(json.dumps(item))
                            f.write("\n")
                        f.close()
                            
                        return 'break'
            ### not on the background
            elif len(selected_item) > 1:
                # dragged item
                drag_item = dragged_item[1]
                # destination item
                dest_item = selected_item[1]
                # if destination is the same item nothing to do
                if drag_item == dest_item:
                    print("same widget")
                    return 'break'
                else:
                    print("different widget")
                    # if file or folder
                    # get the tag
                    item_tag = self.w.gettags(dest_item)
                    # if dest is the recycle bin
                    if item_tag[1] == "bin":
                        print("moved the item '{}' into the recycle bin".format(os.path.basename(event.data)))
                        return event.action
                    # if dest is dir
                    # if destination folder exists
                    if os.path.isdir(self.working_dir+"/"+item_tag[1]):
                        # if data
                        if event.data:
                            files = self.w.tk.splitlist(event.data)
                            print("item received: ", files)
                            action = event.action
                            print("action::", action)
                            print("IS_DIR, copying the item in the dir")
                    
                        return event.action
        # drop from another program
        else:
            print("from another program")
            if event.data:
                files = self.w.tk.splitlist(event.data)
                print("Item received: ", files)
                action = event.action
                print("action::", action)
                #
                ## find the coordinate in the program
                x = self.master.winfo_pointerx()
                y = self.master.winfo_pointery()
                xpos = self.master.winfo_pointerx() - self.master.winfo_rootx()
                ypos = self.master.winfo_pointery() - self.master.winfo_rooty()
                # find the item in the canvas
                selected_item = self.w.find_overlapping(xpos, ypos, xpos, ypos)
                print("drop2_selected_item_B::", selected_item)
                # the background
                if len(selected_item) == 1:
                    if selected_item[0] == 1:
                        print("is_background")
                        return 'break'
                #
                elif len(selected_item) > 1:
                    # destination item
                    dest_item = selected_item[1]
                    # if destination is the same item nothing to do
                    # if file or folder
                    # get the tag
                    item_tag = self.w.gettags(dest_item)
                    # if dest is dir
                    #
                    if os.path.isdir(self.working_dir+"/"+item_tag[1]):
                        # received some data
                        if event.data:
                            files = self.w.tk.splitlist(event.data)
                            print("Item received: ", files)
                            action = event.action
                            print("action::", action)
                            print("IS_DIR, copying the item in the dir")
                    
                        return event.action

########## FINE DRAG AND DROP

######## MOUSE BINDINGS

    def mouseDown(self, event):
        # starting coords
        self.startx = self.w.canvasx(event.x)
        self.starty = self.w.canvasy(event.y)
        #
        selected_item = self.w.find_overlapping(self.startx, self.starty, self.w.canvasx(event.x), self.w.canvasy(event.y))
        print("ASAA_md::", selected_item)
        
        #############
        # the background
        if len(selected_item) == 1:
            # deselect all the rects
            if self.dragged_items:
                for item in self.dragged_items:
                    self.w.itemconfigure(item, fill="")#self.k[5])
            # empty the list of the selected rects
            self.dragged_items = []
            # reset
            self.button1_mouse = 0
            # hide the menu if shown - if not an error occours
            try:
                self.popup_menu.unpost()
            except:
                pass
            
            return
        ###########

        # on the background is 1, otherwise more
        if len(selected_item) == 1:
            if selected_item[0] == 1:
                print("is_background")
                return
        # clicking the rectangle do nothing, only the icon and the text are selectable
        elif len(selected_item) > 2:
            # if bin do nothing
            ttag = self.w.gettags(selected_item[1])
            
            if ttag[0] == '-1' and ttag[1] == 'bin':
                print("selected recycle bin")
                return
            # the rect selected variable
            self.rect_selected = 1
            #
            # clicked on an already selected item
            if selected_item[1] in self.dragged_items:
                # almost one item in the list
                if len(self.dragged_items) > 0:
                    return
            # not in list
            else:
                # deselect everything
                if self.dragged_items:
                    for i in self.dragged_items:
                        self.w.itemconfigure(i, fill="")#self.k[5])
                #
                # select the item
                self.button1_mouse = 1
                # the id of the selected item
                selected_item_id = selected_item[1]
                # the tag of the selected item
                item_tag = self.w.gettags(selected_item_id)
                # select the rect
                self.w.itemconfigure(selected_item_id, fill=self.k[6])
                print("Selected a single item: ", self.w.gettags(selected_item_id)[1])
                # update
                self.dragged_items = [selected_item_id]
   
        self.button1_mouse = 0
   
    def mouseMotion(self, event):
        # the pointer position during dragging
        self.xpos = self.w.canvasx(event.x)
        self.ypos = self.w.canvasy(event.y)
        
        if self.ctrl_lmb:
            return
      
        if self.rect_selected:
            return
        # start from the background
        if self.button1_mouse == 0:
            self.drag_mouse = 1
            
            x = self.w.canvasx(event.x)
            y = self.w.canvasy(event.y)

            if (self.startx != event.x)  and (self.starty != event.y) :
                self.w.delete(self.rubberbandBox)
                self.rubberbandBox = self.w.create_rectangle(self.startx, self.starty, x, y, fill="cornsilk2",stipple='gray25')
                self.update_idletasks()
            #########
            motion_data = self.w.find_overlapping(self.startx, self.starty, self.w.canvasx(event.x), self.w.canvasy(event.y)), self.startx, self.starty, self.w.canvasx(event.x), self.w.canvasy(event.y)
            item_selected = list(motion_data[0])
            #
            # > 3 because there is another data
            if len(item_selected) > 3:
                # for each rect
                for i in self.rectangle_list:
                    # if selected the background colour is changed
                    if i in item_selected:
                        # if a new item
                        if i not in self.dragged_items:
                            self.w.itemconfigure(i, fill=self.k[6])
                            # add it to the list
                            self.dragged_items.append(i)
                    # restore the original colour
                    else:
                        self.w.itemconfigure(i, fill="")#self.k[5])
                        # remove from the list if present
                        if i in self.dragged_items:
                            self.dragged_items.remove(i)
            else:
                # all the rect width the default color
                for i in self.rectangle_list:
                    self.w.itemconfigure(i, fill="")#self.k[5])
                # resetto
                self.dragged_items = []

    # LMB released
    def mouseUp(self, event):
        
        # reset the single rect selected variable
        self.rect_selected = 0
        # if select using CTRL+LMB do nothing
        if self.ctrl_lmb:
            return
        print("self.drop_in_canvas::", self.drop_in_canvas)
        # if the drop ends in the canvas: on a file or folder
        if self.drop_in_canvas:
            # reset
            self.drop_in_canvas = 0
       
            # which rect the pointer is on
            startx = self.w.canvasx(event.x)
            starty = self.w.canvasy(event.y)
            selected_item = self.w.find_overlapping(startx, starty, self.w.canvasx(event.x), self.w.canvasy(event.y))
            print("selected_item_20::", selected_item)
            # if it isn't the background
            if len(selected_item) > 1:
                selected_item_id = selected_item[1]
                name_file = self.w.gettags(selected_item_id)[1]
                print("selected_item_id_20::", selected_item_id, "name_file::", name_file)
                # full path
                item_full_path = os.path.join(self.working_dir, name_file)
                # if it is a folder print a message
                if selected_item_id not in self.dragged_items:
                    if os.path.isdir(item_full_path):
                        print("Item(s) dropped on folder: {}".format(name_file))
           
            return
   
        # if click on the background deselect everything
        self.startx = self.w.canvasx(event.x)
        self.starty = self.w.canvasy(event.y)
        selected_item = self.w.find_overlapping(self.startx, self.starty, self.w.canvasx(event.x), self.w.canvasy(event.y)), self.startx, self.starty, self.w.canvasx(event.x), self.w.canvasy(event.y)
        print("selected_item_a::", selected_item)
        #
        # if it is the desktop
        if len(selected_item[0]) == 1:
            return
        # rect clicked
        # clicking the rectangle do nothing, only the icon and the text are selectable
        elif len(selected_item[0]) > 2:
            print("TTAAGGSS::", self.w.gettags(selected_item[0][1]))
            # 
            if not self.drag_mouse:
                # if bin do nothing
                ttag = self.w.gettags(selected_item[0][1])
                #
                if ttag[0] == '-1' and ttag[1] == 'bin':
                    print("deselected recycle bin")
                    return
                
                print("selected_item_b::", selected_item)
                # the rect id
                selected_item_id = selected_item[0][1]
                # deselect all the others
                for item in self.dragged_items:
                    if item != selected_item_id:
                        self.w.itemconfigure(item, fill="")#self.k[5])
                        # reset the list
                        self.dragged_items = []
                        # add the rect
                        self.dragged_items.append(selected_item_id)
       
        # mouse dragging action
        if self.drag_mouse:
            # reset
            self.drag_mouse = 0
            self.w.delete(self.rubberbandBox)
            ######
            # all the objects of the selected item
            item_selected_rough = self.w.find_overlapping(self.startx, self.starty, self.w.canvasx(event.x), self.w.canvasy(event.y)), self.startx, self.starty, self.w.canvasx(event.x), self.w.canvasy(event.y)
            # reset
            self.button1_mouse = 0
            #
            # print the name of the selected items
            for item in self.dragged_items:
                print("Selected items:", self.w.gettags(item)[1])

    # LMB double click
    def mouseDoubleDown(self, event):
        # starting coords
        startx = self.w.canvasx(event.x)
        starty = self.w.canvasy(event.y)
        # selected item 
        selected_item = self.w.find_overlapping(startx, starty, self.w.canvasx(event.x), self.w.canvasy(event.y)), startx, starty, self.w.canvasx(event.x), self.w.canvasy(event.y)
        # if it is a rect
        if len(selected_item[0]) > 1:
            selected_item_id = selected_item[0][1]
            item_tag = self.w.gettags(selected_item_id)
            print("Double click on item: ", item_tag[1])

    def mouseRDown(self, event):
        # starting coords
        startx = self.w.canvasx(event.x)
        starty = self.w.canvasy(event.y)
        # the selected rect
        selected_item = self.w.find_overlapping(startx, starty, self.w.canvasx(event.x), self.w.canvasy(event.y)), startx, starty, self.w.canvasx(event.x), self.w.canvasy(event.y)
        #
        # if it is a rect
        if len(selected_item[0]) > 1:
            selected_item_id = selected_item[0][1]
            item_tag = self.w.gettags(selected_item_id)
            # if bin deselect all
            if item_tag[1] == "bin":
                # deselect all the rect
                if self.dragged_items:
                    for i in self.dragged_items:
                        self.w.itemconfigure(i, fill="")#self.k[5])
                    # reset
                    self.dragged_items = []
                # menu
                self.mouseRpopup3(event, "bin")
                return
            # select the rect if not already selected
            if selected_item_id not in self.dragged_items:
                # if the rect exists
                if selected_item_id in self.rectangle_list:
                    print("Selected with RMB: ", item_tag[1])
                    # deselect all the rects
                    if self.dragged_items:
                        for i in self.dragged_items:
                            self.w.itemconfigure(i, fill="")#self.k[5])
                    # change the background colour of each rect
                    # ... e set this rect as selected
                    self.w.itemconfigure(selected_item_id, fill=self.k[6])
                    self.dragged_items = [selected_item_id]
                # show a popup if one item is selected
                self.mouseRpopup3(event, "")
            # if it is selected with others
            else:
                # print the name of all selected items
                for item in self.dragged_items:
                    print("Selected using the RMB:", self.w.gettags(item)[1])
                # show a popup - more than one item selected
                self.mouseRpopup3(event, "")
        # on the background
        else:
            # deselect all
            if self.dragged_items:
                for i in self.dragged_items:
                    self.w.itemconfigure(i, fill="")#self.k[5])
                # reset
                self.dragged_items = []
            # menu
            self.mouseRpopup3(event, "background")
    
    # CTRL+LMB
    def CmouseLDown(self, event):
        # hide the menu if shown - if not an error occours
        try:
            self.popup_menu.unpost()
        except:
            pass
        # set the variable
        self.ctrl_lmb = 1
        # coords
        startx = self.w.canvasx(event.x)
        starty = self.w.canvasy(event.y)
        # the selected rect
        selected_item = self.w.find_overlapping(startx, starty, self.w.canvasx(event.x), self.w.canvasy(event.y)), startx, starty, self.w.canvasx(event.x), self.w.canvasy(event.y)
        # if not the background
        if len(selected_item[0]) > 1:
            selected_item_id = selected_item[0][1]
            # item selected
            # if the rect exists
            if selected_item_id in self.rectangle_list:
                # select the rect if it not already selected
                if selected_item_id not in self.dragged_items:
                    # change its background colour
                    # ... add it to the list of selected item
                    self.w.itemconfigure(selected_item_id, fill=self.k[6])
                    self.dragged_items.append(selected_item_id)
                    # print the name of the selected items
                    for item in self.dragged_items:
                        print("Selected with CTRL+LMB:", self.w.gettags(item)[1])
                # deselect it if it is selected
                else:
                    self.w.itemconfigure(selected_item_id, fill="")#self.k[5])
                    self.dragged_items.remove(selected_item_id)
                    # stampo il nome degli elementi deselezionato
                    print("Deselected with CTRL+LMB:", self.w.gettags(selected_item_id)[1])

    def CmouseLUp(self, event):
        # reset
        self.ctrl_lmb = 0

####### END MOUSE BINDINGS


######## WINDOW

    def create_window(self, item):
        window = tk.Toplevel(self)
        # title of the window
        window.title("Info")
        window.minsize(300, 300)
        #
        dim_selected_items = len(self.dragged_items)
        # if one item has been selected
        if dim_selected_items == 1:
            item_name = self.w.gettags(self.dragged_items[0])[1]
        # if more than one item has been selected
        elif dim_selected_items > 1:
            item_name = "more than one item"
        # the recycle bin
        if item == "bin":
            item_name = item
        # the background
        if item == "background":
            item_name = "desktop"
        label1 = ttk.Label(window, text="File name: "+item_name)
        label1.pack()
        #
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        window.update()
        ww = window.winfo_width()
        wh = window.winfo_height()
        # the window in the center of the screen
        x = int((sw-ww)/2)
        y = int((sh-wh)/2)
        window.geometry('+{}+{}'.format(x, y))

    # popup
    def mouseRpopup3(self, event, item):
        self.popup_menu = tk.Menu(self, tearoff=0, font=("", self.k[9]))
        self.popup_menu.add_command(label="One", command=lambda: self.create_window(item))
        try:
            self.popup_menu.post(event.x_root+10, event.y_root)
        finally:
            self.popup_menu.grab_release()

########### END WINDOW


########### MAIN

def windowExit():
    notifier.stop()
    root.destroy()

root = TkinterDnD.Tk()

# if the folder is readable and writable
if not os.access(working_dir, os.W_OK | os.R_OK):
    messagebox.showinfo("ERROR", "the folder is not readable or writable")
    root.destroy()
    sys.exit()

root.protocol('WM_DELETE_WINDOW', windowExit)

###### the program as desktop
#root.overrideredirect(True)
#root.wm_attributes("-type", "desktop")
#root.lower()
#root.update_idletasks()
## the size of the screen
#screen_width = root.winfo_screenwidth()
#screen_height = root.winfo_screenheight()
#root.geometry('{}x{}'.format(screen_width, screen_height))
######

###### the program in a window
root.update_idletasks()
screen_width = 1200
screen_height = 860
print(screen_width,screen_height)
root.geometry('{}x{}'.format(screen_width, screen_height))
######

app = Application(master=root, k=canvas_config, dd=canvas_data)

######

app.mainloop()
