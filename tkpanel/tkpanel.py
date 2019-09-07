#!/usr/bin/env python3
"""
JUST FOR FUN
"""
# V. 09-06-2019 A

import tkinter as tk
import tkinter.ttk as ttk
import tkinter.font as tkf
from tkinter import messagebox
import os
import sys
import math
from pathlib import Path
import subprocess
import threading

from user_modules import pop_menu
try:
    from user_modules import right_frame
except:
    pass
try:
    from user_modules import left_frame
except:
    pass

import Xlib
import Xlib.display

disp = Xlib.display.Display()
rootx = disp.screen().root

rootx.change_attributes(event_mask=Xlib.X.PropertyChangeMask|Xlib.X.SubstructureNotifyMask|Xlib.X.StructureNotifyMask)#|Xlib.X.SubstructureRedirectMask)

# the folder program dir
working_dir = "."
# width and height of the program
prog_width = 0
prog_height = 50
# with and height of the screen
screen_width = 0
screen_height = 0
# menu icon size
menu_icon_size = 36
# vertical virtual desktop buttons padding
vd_btn_pady = (prog_height - menu_icon_size) / 4
 
### font sizes
font_size = 20
font_size2 = 20
font_size3 = 20

# just to save some lines of code
wnck = "wmctrl"

######### the virtual desktop

## the number of virtual desktops
atom_vs = disp.intern_atom('_NET_NUMBER_OF_DESKTOPS')
vd_v = rootx.get_full_property(atom_vs, Xlib.X.AnyPropertyType).value
virtual_desktops = vd_v.tolist()[0]

## the active virtual desktop - 0 is 1 etc.
atom_cvd = disp.intern_atom("_NET_CURRENT_DESKTOP")
vd_cv = rootx.get_full_property(atom_cvd, Xlib.X.AnyPropertyType).value
active_virtual_desktop = vd_cv.tolist()[0]

###### atoms
NET_WM_NAME = disp.intern_atom('_NET_WM_NAME')
NET_CLIENT_LIST_ATOM = disp.intern_atom('_NET_CLIENT_LIST')
NET_CLIENT_LIST_ATOM_N = disp.intern_atom('_NET_WM_WINDOW_TYPE_NORMAL')
NET_CLIENT_LIST_ATOM_T = disp.intern_atom('_NET_WM_WINDOW_TYPE')
NET_ACTIVE_WINDOW = disp.intern_atom('_NET_ACTIVE_WINDOW')

##### to get a window property
def getProp(disp,win, prop):
    try:
        p = win.get_full_property(disp.intern_atom('_NET_WM_' + prop), 0)
        return [None] if (p is None) else p.value
    except:
        return [None]

##### hex function bug - add the leading 0
# h class string
def right_hex(h):
    c = h.strip("0x")
    if len(c) == 7:
        return "0x0"+c
    elif len(c) > 7:
        if c[0] != "0":
            return "0x0"+c
    else:
        return h

#### list of normal windows
## tuple id, name, desktop number (the first is 0)
list_normal_win = []

##### populate the list
def fListNormalWin():
    winid_list = rootx.get_full_property(NET_CLIENT_LIST_ATOM, Xlib.X.AnyPropertyType).value
    for winid in winid_list:
        window = disp.create_resource_object('window', winid)

        ppp = getProp(disp,window,'DESKTOP')
        on_desktop = ppp.tolist()[0]
        
        prop = window.get_full_property(NET_CLIENT_LIST_ATOM_T, Xlib.X.AnyPropertyType)
        if prop:
            if prop.value.tolist()[0] == NET_CLIENT_LIST_ATOM_N:
                # add to list
                # workaround for the char "—" chr(8212): not recognized the name of the window
                if not isinstance(window.get_wm_name(), str):
                    window_name = "Unknown"
                else:
                    window_name = window.get_wm_name()
                list_normal_win.append((right_hex(hex(window.id)), window_name, on_desktop))

fListNormalWin()

########### list of existent normal windows 
lllist = []
def get_win_desktop(wid):
    
    wl_data = subprocess.check_output(["wmctrl", "-l"])
    wl = wl_data.decode()
    aa = wl.splitlines()
    
    for el in aa:
        bb = el.split()
        lllist.append(bb)
    
    # find the wid
    for el in lllist:
        if int(el[0], 16) == wid:
            return el[1]
    
    return None


##########

last_seen = {'xid': None}

# CDThread
cd_event = object
# to stop the CDThread - needed to exit from the progran nicely
stopCD = 0

# the active window: tuple: b'name' and wid type int
sct = []
# the var related to the active window 
sctVar = object

########## ACTIVE WINDOW
def get_active_window1():
    window_id = rootx.get_full_property(NET_ACTIVE_WINDOW,
                                       Xlib.X.AnyPropertyType).value[0]

    focus_changed = (window_id != last_seen['xid'])
    last_seen['xid'] = window_id
    
    # the window id - boolean
    return window_id, focus_changed

def get_window_name1(window_id):
    try:
        window_obj = disp.create_resource_object('window', window_id)
        window_name = window_obj.get_full_property(NET_WM_NAME, 0).value
    except Xlib.error.XError:
        window_name = None

    return window_name 
############### END ACTIVE WINDOW
    
# the active window at startup
def firstActiveWin():
    ########## ACTIVE WINDOW
    win, changed = get_active_window1()
    if win and changed:
        global sct
        # tuple: b'name' and wid type int
        sct = [get_window_name1(win), win]
    ########## END ACTIVE WINDOW
firstActiveWin()

## the var related to the amount of window buttons
# after a windows has been closed - the wid
numButt = ""
# the new window
tcd = object
# virtual desktops - var
virt_desk = object

# track a created or closed window or a changed active window
class CDThread(threading.Thread):
    
    def __init__(self3, application):
        threading.Thread.__init__(self3)
        self3.event = threading.Event()
        global cd_event
        cd_event = self3.event
        self3.application = application
    
    ########## ACTIVE WINDOW
    def get_active_window(self3):
        window_id = rootx.get_full_property(NET_ACTIVE_WINDOW,
                                           Xlib.X.AnyPropertyType).value[0]

        focus_changed = (window_id != last_seen['xid'])
        last_seen['xid'] = window_id
        
        # the window id - boolean
        return window_id, focus_changed

    def get_window_name(self3, window_id):
        try:
            window_obj = disp.create_resource_object('window', window_id)
            window_name = window_obj.get_full_property(NET_WM_NAME, 0).value
        except Xlib.error.XError:
            window_name = None

        return window_name 
    ############### END ACTIVE WINDOW
    
    def run(self3):
        
        while not self3.event.is_set():
            
            # to get a property of a window
            def getProp(disp,win, prop):
                try:
                    p = win.get_full_property(disp.intern_atom('_NET_WM_' + prop), 0)
                    return [None] if (p is None) else p.value
                except:
                    return [None]

            ####
            while True:
                if stopCD == 1:
                    break
                
                ########## ACTIVE WINDOW
                win, changed = self3.get_active_window()
                if win and changed:
                    global sct
                    # tuple: b'name' and wid type int
                    sct = [self3.get_window_name(win), win] #.decode()
                    # set the related var with univocal data
                    sctVar.set(win)
                ########## END ACTIVE WINDOW
                
                
                def handle_event(event):
                    global list_normal_win
                    # a new window is created
                    if (event.type == Xlib.X.CreateNotify):
                        window = disp.create_resource_object('window', event.window)

                        is_type = None
                        try:
                            winName = getProp(disp, event.window, 'NAME')
                            winPid = getProp(disp, event.window, 'PID')[0]
                            is_type = getProp(disp, event.window,'WINDOW_TYPE')[0]
                        except:
                            pass
                        
                        # if it is a normal type
                        if is_type and disp.get_atom_name(is_type) == "_NET_WM_WINDOW_TYPE_NORMAL":
                            # se non sono None
                            if winName and winPid:
                                        
                                # if the window is a normal one
                                prop = window.get_full_property(NET_CLIENT_LIST_ATOM_T, Xlib.X.AnyPropertyType)
                                if prop:
                                    # on which desktop
                                    on_desktop = None
                                    while on_desktop == None:
                                        on_desktop = get_win_desktop(event.window.id)

                                    win_hex = right_hex(hex(event.window.id))
                                    newData = (win_hex, winName.decode(), int(on_desktop))
                                    if not newData in list_normal_win:
                                        list_normal_win.append(newData)
                                        # add the button in the frame
                                        self3.application.flist_desktop_windows3("add", newData)
                    #######
                    # number of virtual desktops
                    if (event.type == Xlib.X.PropertyNotify):
                        # change the number of virtual desktops
                        if disp.get_atom_name(event.atom) == '_NET_NUMBER_OF_DESKTOPS':
                            vd_v = rootx.get_full_property(atom_vs, Xlib.X.AnyPropertyType).value
                            global virt_desk
                            # type int
                            virt_desk.set(vd_v.tolist()[0])
                        # change the current desktop
                        if disp.get_atom_name(event.atom) == "_NET_CURRENT_DESKTOP":
                            # the new current virtual desktop
                            cvd_v = rootx.get_full_property(atom_cvd, Xlib.X.AnyPropertyType).value
                            #
                            global active_virtual_desktop
                            # get the previous current virtual desktop
                            previous_virtual_desktop = active_virtual_desktop
                            # set the var
                            active_virtual_desktop = cvd_v.tolist()[0]
                            #
                            self3.application.fsvd(previous_virtual_desktop)
                        if disp.get_atom_name(event.atom) == "_NET_CLIENT_LIST_STACKING":
                            # the current list
                            old_list_normal_win = list_normal_win
                            # reset the list
                            list_normal_win = []
                            # repopulate the list
                            fListNormalWin()
                            #
                            if len(old_list_normal_win) == len(list_normal_win):
                                if old_list_normal_win != list_normal_win:
                                    #
                                    for el in list_normal_win:
                                        if el not in old_list_normal_win:
                                            if el[2] != active_virtual_desktop:
                                                # remove the button from the frame
                                                self3.application.flist_desktop_windows3("change", el)
                    #
                    # a window is closed/destroyed
                    if (event.type == Xlib.X.DestroyNotify):

                        # temporary list of the wid of the windows after one is closed
                        tmp_list = []
                        
                        # list all root windows
                        rchildren = rootx.get_full_property(NET_CLIENT_LIST_ATOM, Xlib.X.AnyPropertyType).value
                        for child in rchildren:
                            try:
                                window2 = disp.create_resource_object('window', child)
                                prop2 = window2.get_full_property(disp.intern_atom('_NET_WM_WINDOW_TYPE'), Xlib.X.AnyPropertyType)
                                wmname2 = window2.get_wm_name()
                                
                                if prop2.value.tolist()[0] == NET_CLIENT_LIST_ATOM_N:
                                    # add to list - wid 
                                    tmp_list.append(right_hex(hex(window2.id)))
                            except:
                                pass
                        ##
                        if len(tmp_list) == len(list_normal_win) - 1:
                            # if a window in list_normal_win is not in tmp_list
                            for el in list_normal_win:
                                if str(right_hex(el[0])) not in tmp_list:
                                    # wid to var
                                    global numButt
                                    numButt = right_hex(el[0])
                                    ###the index of the closed window
                                    idx = list_normal_win.index(el)
                                    ### remove el
                                    list_normal_win.remove(el)
                                    # remove the button from the frame
                                    self3.application.flist_desktop_windows3("remove", el)
                                    break

                while True:
                    if stopCD == 1:
                        break
                    event = disp.next_event()
                    handle_event(event)
                    
                    # ACTIVE WINDOW
                    if (event.type == Xlib.X.PropertyNotify and
                            event.atom == NET_ACTIVE_WINDOW):
                        break
            
            if self3.event.is_set():
                return False


####### main class
class Application(ttk.Frame):
    
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        
        self.pack(fill="both", expand=True)

        # font size to all widgets except popup
        self.s = ttk.Style()
        self.s.configure('.', font=('', font_size))
        
        ## the text height related to the font and size used
        t_Font = tkf.Font(family='', size=font_size2)
        self.linespace = t_Font.metrics("linespace")
        
        # the colour of the frame
        self.style = ttk.Style()
        self.style.configure("Color.TFrame", background="#222c3d")
        self.config(style='Color.TFrame')
        
        #
        self.master.update_idletasks()
        
        # the show the desktop switcher
        self.desk_switcher = "off"
        
        # list of the name of the windows 
        self.list_desktop_windows_temp = []
        self.list_desktop_windows = []
        
        # list of window id - button id - desktop in which it is
        self.list_id = []
        
        # num buttons counter
        self.i = 0
        
        # used to close the menu if open 
        self.mw_isopen = 0
        
        #
        self.create_widgets()
    
    # highlight the current active window - check var sctVar/self.sct_var
    def flist_desktop_windows(self, wdata):
        curr_win = wdata[1] 
        #
        for el in self.list_id:
            if int(el[0], 16) == curr_win:
                # set its state
                el[1].state(["pressed"])
            else:
                # set the state of the other buttons
                el[1].state(["!pressed"])

    # the tooltip
    def btn_tooltip_win(self, widget, text):
        self.tw = tk.Toplevel(widget)
        self.tw.wm_overrideredirect(True)
        x = widget.winfo_rootx()
        # if the pointer in the second half of the screen (width)
        ## TO DO
        y = widget.winfo_rooty() - 35
        self.tw.wm_geometry("+%d+%d" % (x, y))
        label = tk.Label(self.tw, text=text, font=("", font_size), background="#222c3d", foreground="white", borderwidth=1)
        label.pack(ipadx=3)
        
    # the button taskwindow tooltip
    def btn_tooltip(self, widget, win_id):
        # get the title of the window
        window = disp.create_resource_object('window', int(win_id, 16))
        prop = window.get_full_property(NET_CLIENT_LIST_ATOM_T, Xlib.X.AnyPropertyType)
        if prop:
            if prop.value.tolist()[0] == NET_CLIENT_LIST_ATOM_N:
                widget_name = window.get_wm_name()
                # after a little delay
                widget.after(300, lambda:self.btn_tooltip_win(widget, widget_name))
        
    # the pointer on the button
    def btn_on_enter(self, event, win_id):
        self.btn_tooltip(event.widget, win_id)

    # the pointer leaves the button
    def btn_on_leave(self, event):
        # destroy the tooltip
        if self.tw:
            self.tw.destroy()
    
    # the middle button closes the window
    def on_middle(self, event, win_id):
        # get the window
        window = disp.create_resource_object('window', int(win_id, 16))
        # delete the window
        window.destroy()
        disp.flush()
    
    # add buttons for existent opened windows at this program launch
    def flist_desktop_windows2(self):
        actual_virtual_desktop = active_virtual_desktop
        # add a button to the frame if a window has been found...
        for el in list_normal_win:
            #... in the current desktop
            if el[2] == actual_virtual_desktop:
                # button text max 13 character long
                if len(el[1]) > 13:
                    btext = el[1][0:10]+"..."
                else:
                    btext = el[1]
                #
                self.btn = ttk.Button(self.win_btns_frame, style="Color.TButton", text=btext, command=lambda x=el[0]: self.fwinbtn(x))
                # the binds - el[0] is the window id (hex)
                self.btn.bind("<Enter>", lambda event,x=el[0]: self.btn_on_enter(event, x))
                self.btn.bind("<Leave>", self.btn_on_leave)
                self.btn.bind('<ButtonRelease-2>', lambda event,x=el[0]: self.on_middle(event, x))
                # wid - btn - desktop in which the window it is
                self.list_id.append([el[0], self.btn, el[2]])
                self.btn.grid(row=0, column=self.i, ipady=vd_btn_pady, sticky="ns")
                self.i += 1
            # or in other desktops
            else:
                self.btn = ttk.Button(self.win_btns_frame, style="Color.TButton", text=el[1][0:10]+"...", command=lambda x=el[0]: self.fwinbtn(x))
                # add to list
                self.list_id.append([el[0], self.btn, el[2]])
    
        ########## highlight the current window button
        for el in self.list_id:
            if int(el[0], 16) == sct[1]:
                # set its state
                el[1].state(["pressed"])
            else:
                # set the state of the other buttons
                el[1].state(["!pressed"])
    
    # add or remove a button when a new normal window is created or deleted
    # action type: add - remove; el the element: window_id - name - active_virtual_desktop
    def flist_desktop_windows3(self, action_type, el):
        # add a button
        if action_type == "add":
            tmp_list = []
            for el1 in self.list_id:
                tmp_list.append(el1[0])

            # the size of the window buttons frame
            frame_size = self.win_btns_frame.winfo_width()
            
            # if in the current desktop
            if el[2] == active_virtual_desktop:
                if el[0] not in tmp_list:
                    # button text max 13 character long
                    if len(el[1]) > 13:
                        btext = el[1][0:10]+"..."
                    else:
                        btext = el[1]
                    self.btn = ttk.Button(self.win_btns_frame, style="Color.TButton", text=btext, command=lambda x=el[0]: self.fwinbtn(x))
                    self.btn.grid(row=0, column=self.i, ipady=vd_btn_pady, sticky="ns")
                    # the binds - el[0] is the window id (hex)
                    self.btn.bind("<Enter>", lambda event,x=el[0]: self.btn_on_enter(event, x))
                    self.btn.bind("<Leave>", self.btn_on_leave)
                    self.btn.bind('<ButtonRelease-2>', lambda event,x=el[0]: self.on_middle(event, x))
                    # add to self.list_id
                    self.list_id.append([el[0], self.btn, el[2]])
                    self.i += 1
                    #
                    num_btn = len(self.list_id)
                    #
                    if num_btn * self.btn.winfo_width() > frame_size:
                        # needed to shorten the buttons when all of them fit the frame
                        for i in range(40):
                            self.win_btns_frame.columnconfigure(i, weight=1)
            #
            # if other desktop create a button and add to list_id
            else:
                # if not in list
                if el[0] not in tmp_list:
                    # not in the frame
                    self.btn = ttk.Button(self.win_btns_frame, style="Color.TButton", text=el2[1][0:10]+"...", command=lambda x=el2[0]: self.fwinbtn(x))
                    # add to self.list_id
                    self.list_id.append([el[0], self.btn, el[2]])
        #
        # remove a button
        elif action_type == "remove":
            #
            tmp_list = []
            for el1 in list_normal_win:
                tmp_list.append(el1[0])
            #
            for el2 in self.list_id:
                #
                if el2[0] not in tmp_list:
                    el2[1].destroy()
                    # 
                    self.i -= 1
                    # remove from the list
                    self.list_id.remove(el2)
        # the window change the desktop
        elif action_type == "change":
            # the window id
            window_id = el[0]
            #### 
            # remove el from the list_id
            for el2 in self.list_id:
                if el2[0] == window_id:
                    el2[1].grid_forget()
                    # 
                    self.i -= 1
                    # remove from the list
                    self.list_id.remove(el2)
                    # add the button to list again with a different desktop
                    newData = (el2[0], el2[1], el[2])
                    self.list_id.append(newData)
    
    # activate or minimize the selected window from the frame
    def fwinbtn(self, wid):
        # sct: tuple: b'name' and wid type int
        # the current active window
        active_window = right_hex(hex(sct[1]))
        # if active window minimize it
        if active_window == wid:
            prog = "wmctrl -ir {} -b toggle,hidden".format(wid)
            subprocess.run([prog], shell=True)
        # if not active window
        else:
            prog = "wmctrl -ia {}".format(wid)
            subprocess.run([prog], shell=True)

    # the current active window var
    def callback(self, *args):
        # make the changes into the window button frame
        self.flist_desktop_windows(sct)

    # the number of virtual desktops
    def fvirt_desk(self, *args):
        # modify the number of virtual desktop buttons
        self.fnumber_virtual_desktops(args[0].get())
    
    # add or remove a virtual desktop button
    def fnumber_virtual_desktops(self, num_virt_desk):
       global virtual_desktops
       if num_virt_desk > virtual_desktops:
           self.vd_btn = ttk.Button(self.vdframe, style="vd_btn_style.TButton", text=str(virtual_desktops+1), width=-1, command=lambda x=virtual_desktops:self.fvd(x))
           self.vd_btn_list.append(self.vd_btn)
           self.vd_btn.grid(row=0, column=virtual_desktops, ipady=vd_btn_pady, sticky="ns")
           # update the number of virtual desktops
           virtual_desktops += 1
       elif num_virt_desk < virtual_desktops:
           # update the number of virtual desktops
           virtual_desktops -= 1
           # remove the button 
           vd_btn = self.vd_btn_list.pop()
           vd_btn.grid_forget()
           del vd_btn
   
    # 
    def create_widgets(self):
        ##### styles
        # the style for all widgets
        # label
        self.style.configure("Color.TLabel", borderwidth=0, foreground="white", background="#222c3d")
        # button
        self.style.configure("Color.TButton", borderwidth=0, foreground="white", background="#222c3d")
        # dinamic aspect
        self.style.map("Color.TButton",
                        foreground=[('pressed', '#ffffff'), ('active', '#ffffff')],
                        background=[('pressed', '!disabled', '#1f1f1f'), ('active', '#122645')]
                        )
        # frame
        self.style.configure("Color.TFrame", borderwidth=0, foreground="white", background="#222c3d")
        
        self.rowconfigure(0, weight=1)
        
        self.columnconfigure(0, weight=0)
        self.columnconfigure(1, weight=0)
        self.columnconfigure(2, weight=0)
        self.columnconfigure(3, weight=0)
        self.columnconfigure(4, weight=0)
        self.columnconfigure(5, weight=0)
        self.columnconfigure(6, weight=1)
        self.columnconfigure(7, weight=0)
        self.columnconfigure(8, weight=0)
        self.columnconfigure(9, weight=0)
        self.columnconfigure(10, weight=0)
        #
        #### the menu button
        self.menu_img = tk.PhotoImage(file="icons/menu.png")
        self.menu_btn = ttk.Button(self, style="Color.TButton", image=self.menu_img, command=self.fmenu_btn)
        self.menu_btn.grid(row=0, column=0, sticky="nwse", padx=2)
        #
        #### the virtual desktop buttons
        # the list of the buttons
        self.vd_btn_list = []
        # track the change of the number of virtual desktops
        self.virt_desk_var = tk.IntVar()
        global virt_desk
        virt_desk = self.virt_desk_var
        #
        self.virt_desk_var.trace("w", lambda *args:self.fvirt_desk(virt_desk))
        
        # the virtual desktops buttons
        self.vdframe = ttk.Frame(self)
        self.vdframe.grid(row=0, column=1, padx=2)
        
        #for i in range(10):
        #    self.vdframe.columnconfigure(i, minsize=1)#, uniform=0)
        
        self.vd_btn_style = ttk.Style()
        self.vd_btn_style.configure("vd_btn_style.TButton", borderwidth=0, font=("", font_size, "bold"), background="#222c3d", foreground="white")
        self.vd_btn_style.map('vd_btn_style.TButton', background = [("pressed", "#000000"),("active", "#222c3d")]) 
        
        for nvd in range(virtual_desktops):
            self.vd_btn = ttk.Button(self.vdframe, style="vd_btn_style.TButton", text=str(nvd+1), width=-1, command=lambda x=nvd:self.fvd(x))
            self.vd_btn_list.append(self.vd_btn)
            self.vd_btn.grid(row=0, column=nvd, ipady=vd_btn_pady, sticky="ns")

        # set the button state of the active desktop
        self.vd_btn_list[active_virtual_desktop].state(["pressed"])
        # 
        #### the "showing the desktop" mode button
        self.show_desk_img = tk.PhotoImage(file="icons/show_desktop.png")
        self.show_desk_btn = ttk.Button(self, style="Color.TButton", image=self.show_desk_img, width=-1, command=self.fshow_desk)
        self.show_desk_btn.grid(row=0, column=2, sticky="ns", padx=2)
        #
        
        # frame for f_addon
        try:
            self.l_addon_frame = ttk.Frame(self)
            self.l_addon_frame.config(style='Color.TFrame')
            self.l_addon_frame.grid(row=0, column=3, sticky="nwse", padx=2)
            l_addon = left_frame.leftWidgets(self.l_addon_frame)
        except:
            pass
        
        #### the windows buttons
        
        # control the current active window
        global sctVar
        self.sct_var = tk.StringVar()
        sctVar = self.sct_var
        #
        self.sct_var.trace("w", lambda *args:self.callback(sctVar))
        
        self.win_btns_frame = ttk.Frame(self)
        self.win_btns_frame.config(style='Color.TFrame')
        self.win_btns_frame.grid(row=0, column=5, sticky="nwse", padx=2)

        # label as separator - expand
        self.sep_lbl = ttk.Label(self, text="")
        self.sep_lbl.config(style='Color.TLabel')
        self.sep_lbl.grid(row=0, column=6, sticky="nwse")

        #
        # frame for r_addon
        try:
            self.r_addon_frame = ttk.Frame(self)
            self.r_addon_frame.config(style='Color.TFrame')
            self.r_addon_frame.grid(row=0, column=10, sticky="nwse", padx=2)
            r_addon = right_frame.rightWidgets(self.r_addon_frame)
        except:
            pass
        
        #### run the threads
        # window opened or closed or active 
        self.cd = CDThread(self)
        self.cd.start()
        
        self.master.update_idletasks()
        
        ## set the size of the frame depending on the size of the label
        self.win_btns_frame.grid_propagate(0)
        butt_sep_size = self.sep_lbl.winfo_width()
        self.win_btns_frame.configure(width=butt_sep_size)
        
        # starts the function that populats the frame
        # first I need to know the active window
        self.flist_desktop_windows2()
    
    # hide or show the menu
    def fmenu_btn(self):
        # close the menu
        if self.mw_isopen:
            self.fcmenuWindow()
        else:
            # open the menu
            self.fmenuWindow()
    
    # virtual desktops switcher
    # nvd is the virtual desktop associated to the button
    def fvd(self, nvd):
        #*fvdn 0 or 1 etc.
        global active_virtual_desktop
        ### find the previous virtual desktop
        ##previous_virtual_desktop = self.factual_virtual_desktop()
        # find the previous virtual desktop
        previous_virtual_desktop = active_virtual_desktop
        try:
            # change virtual desktop
            prog = "wmctrl -s {}".format(nvd)
            subprocess.run([prog], shell=True)
        except:
            # error message
            return
        ## find the actual virtual desktop
        #
        # set the current virtual desktop
        active_virtual_desktop = nvd
        # the widgets
        self.fsvd(previous_virtual_desktop)
        
    # make the change in the related widgets as the current virtual desktop change
    def fsvd(self, previous_virtual_desktop):
        # modify the style of the virtual desktop buttons
        for i in range(len(self.vd_btn_list)):
            if i == active_virtual_desktop:
                self.vd_btn_list[i].state(["pressed"])
            else:
                self.vd_btn_list[i].state(["!pressed"])
        #
        #### THE WINDOW OF THE DESKTOP
        # remove all the widget
        for el in self.list_id:
            if el[2] == previous_virtual_desktop:
                el[1].grid_forget()
        # reset the counter
        self.i = 0
        # add the buttons of the switched desktop
        for el in self.list_id:
            if el[2] == active_virtual_desktop:
                el[1].grid(row=0, column=self.i, ipady=vd_btn_pady, sticky="ns")
                self.i += 1
    
    # the show_the_desktop_switcher action
    def fshow_desk(self):
        try:
            if self.desk_switcher == "off":
                self.desk_switcher = "on"
            else:
                self.desk_switcher = "off"
            prog = "wmctrl -k {}".format(self.desk_switcher)
            subprocess.run([prog], shell=True)
        except:
            pass

############## THE MENU WINDOW ##############

    # the menu window
    def fmenuWindow(self):
        # the menu
        self.menuWindow = tk.Toplevel(self.master)
        self.menuWindow.overrideredirect(True)
        self.menuWindow.attributes("-topmost", True)
        self.menuWindow.title("main_menu")
        # the color
        self.menuWindow.configure(background="#222c3d")
        # populate the menu
        # list of list: category - name - exec - icon
        self.menus = pop_menu.getMenu().retList()
        
        # style
        self.style.configure("Color2.TLabel", background="#122645", foreground="white")
        
        # track the last label highlighted to close the related submenu
        self.last_lbl = None
        
        i = 0
        # the list of the categories found
        self.l_cat = []
        # the list of the labels of the menu
        self.list_mlbl = []
        for el in self.menus[0]:
            # [item.name, item.path, idx, item.name.lower(), pexec, icon]
            cat = el[2]
            if cat not in self.l_cat:
                if cat == "Missed":
                    continue
                self.lbl = ttk.Label(self.menuWindow, text=cat, style="Color.TLabel")
                self.lbl.grid(row=i, column=0, sticky="we", padx=10, pady=5)
                self.list_mlbl.append(self.lbl)
                ### 
                self.lbl.bind("<Enter>", self.on_enter)
                self.lbl.bind("<Leave>", self.on_leave)
                self.l_cat.append(cat)
                i += 1
        # needed to get the size of the menu
        self.master.update_idletasks()
        # the height of each label
        if self.list_mlbl:
            self.mlabel_height = self.list_mlbl[0].winfo_height()
        # the bind
        self.menuWindow.bind("<Motion>", self.on_menuwin_motion)
        # positioning
        self.menu_width = self.menuWindow.winfo_width()
        self.menu_height = self.menuWindow.winfo_height()
        x = 1
        y = screen_height - prog_height - self.menu_height
        self.menuWindow.geometry('+{}+{}'.format(x, y))
        # track this window
        self.mw_isopen = 1
        # track the submenu window
        self.smw_isopen = 0

    # the poiter moves about the main menu
    def on_menuwin_motion(self, event):
        x,y = self.master.winfo_pointerxy()
        # the widget 
        label_widget = self.master.winfo_containing(x,y)
        # get the type of widget
        if isinstance(label_widget, ttk.Label):
            label_text = label_widget.cget("text")
            # the label is a menu category
            if label_text in self.l_cat:
                ### the pointer position is from x and y
                # create a submenu after a little delay
                self.master.after(50, None)
                self.fsmenuWindow(label_widget)
                # track the submenu
                self.smw_isopen = 1

    # close the menuWindow
    def fcmenuWindow(self):
        if self.mw_isopen:
            if self.smw_isopen:
                # close the submenu
                self.smenuWindow.destroy()
                # reset
                self.smw_isopen = 0
            # reset
            self.mw_isopen = 0
            self.menuWindow.destroy()

    # the pointer over a menu entry
    def on_enter(self, event):
        # change the style of the label
        event.widget.configure(style="Color2.TLabel")
        
        if self.last_lbl:
            # when the label looses the focus style to default
            self.last_lbl.configure(style="Color.TLabel")
            # remove the submenu
            if self.smw_isopen:
                self.smenuWindow.destroy()
                self.smw_isopen = 0
            # reset
            self.last_lbl = None 

    # the pointer leaves a menu entry
    def on_leave(self, event):
        # change the style of the label to the default one
        event.widget.configure(style="Color.TLabel")
        # memorize the last menu entry highlighted
        self.last_lbl = event.widget

    # the submenu window
    def fsmenuWindow(self, label_widget):
        # if already open do nothing
        if self.smw_isopen:
            return
        # the label text
        label_widget_text = label_widget.cget("text")
        
        self.smenuWindow = tk.Toplevel(self.master)
        self.smenuWindow.overrideredirect(True)
        self.smenuWindow.attributes("-topmost", True)
        # the color
        self.smenuWindow.configure(background="#222c3d")
        
        ###########
        # the list of the category found
        self.l_cat2 = []
        # the list of the labels
        self.list_entries = []
        for el in self.menus[0]:
            ## [item.name, item.path, idx, item.name.lower(), pexec, icon]
            cat = el[2]
            if cat == label_widget_text:
                # added to the list
                self.list_entries.append(el)
        #
        ## populate 
        # list of labels
        self.list_smlbl = []
        #### the height of the submenu lesser than the screen height
        # number of entries
        num_list_entries = len(self.list_entries)
        # total height of the submenu given the height of each label
        total_height = num_list_entries * (self.mlabel_height+10)
        # max number of entries before splitting the submenu
        num_of_entries = num_list_entries
        if total_height > (screen_height * 0.75):
            n_s_h = int(screen_height * 0.75)
            num_of_entries = int(n_s_h / (self.mlabel_height+10))
         
        # row index
        row_idx = 0
        # column index
        col_idx = 0
        
        # [item.name, item.path, idx, item.name.lower(), pexec, icon]
        for item in self.list_entries:
            name = item[0]
            pexec = item[4]
            ##icon = item[5]
            
            self.lbl = ttk.Label(self.smenuWindow, text=name, style="Color.TLabel")
            self.lbl.grid(row=row_idx, column=col_idx, sticky="we", padx=10, pady=5)
            self.list_smlbl.append(self.lbl)
            #### 
            self.lbl.bind("<Button-1>", lambda event,x=pexec:self.execProg(event, x))
            self.lbl.bind("<Enter>", self.on_senter)
            self.lbl.bind("<Leave>", self.on_sleave)
            self.l_cat2.append(cat)
            # split the submenu if the desired height is reached
            if len(self.list_smlbl) == num_of_entries * (col_idx + 1):
                col_idx += 1
                row_idx = 0
            else:
                row_idx += 1
        
        ## need to find the height of the submenu windows
        # number of entries in the submenu
        num_entries = num_of_entries #len(self.list_smlbl)
        sm_height = num_entries * (self.mlabel_height+10)
        #
        ppad = 0
        # if the submenu height is larger than the menu height add a pad
        if sm_height > self.menu_height:
            ppad = sm_height - self.menu_height
        # try to center the submenu to the highlighted entry
        else:
            # label_widget(_text) index of self.list_mlbl
            lbl_idx = self.list_mlbl.index(label_widget)
            # the height of all the entries up to the highlighted one
            aaa = lbl_idx * (self.mlabel_height+10)
            ppad = -int(aaa)
            if num_entries > (len(self.list_mlbl) - lbl_idx):
                entries_diff = num_entries - (len(self.list_mlbl) - lbl_idx)
                ppad += entries_diff * (self.mlabel_height+10)

        sx = 1 + self.menu_width
        sy = screen_height - prog_height - self.menu_height - ppad
        self.smenuWindow.geometry('+{}+{}'.format(sx, sy))

    # the mouse on the menu entry
    def on_senter(self, event):
        # change the style of the label
        event.widget.configure(style="Color2.TLabel")
    
    # the mouse leave the menu entry
    def on_sleave(self, event):
        # restore the style of the label
        event.widget.configure(style="Color.TLabel")

    # exec the program
    def execProg(self, event, prog):
        subprocess.Popen([prog], shell=True)
        # close the submenu
        self.smenuWindow.destroy()
        # close the menu
        self.fcmenuWindow()

#######################################    

def windowExit():
    global cd_event
    cd_event.set()
    global stopCD
    stopCD = 1
    root.destroy()
    #sys.exit()
        
root = tk.Tk()
root.protocol('WM_DELETE_WINDOW', windowExit)
root.overrideredirect(True)
root.wm_attributes("-type", "dock")

# the name of this program
root.title("tk-panel")

# if the folder is readable and writable
if not os.access(working_dir, os.W_OK | os.R_OK):
    messagebox.showinfo("ERROR", "the folder is not readable or writable")
    root.destroy()
    sys.exit()

# the measures of the screen
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

###### the program in a window
root.update_idletasks()
prog_width = screen_width
#prog_height = 50
wposx = 0
wposy = screen_height - prog_height
root.geometry('{}x{}+{}+{}'.format(prog_width, prog_height, wposx, wposy))
######
# the theme
s=ttk.Style()
if "clam" in s.theme_names():
    s.theme_use("clam")

app = Application(master=root)

######

app.mainloop()
