#!/usr/bin/env python3

# V. 08-26-2019 A

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

import Xlib
import Xlib.display

disp = Xlib.display.Display()
rootx = disp.screen().root

rootx.change_attributes(event_mask=Xlib.X.PropertyChangeMask|Xlib.X.SubstructureNotifyMask)

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

#### list of normal windows
## tuple id, name, desktop
list_normal_win = []

##### populate the list
winid_list = rootx.get_full_property(NET_CLIENT_LIST_ATOM, Xlib.X.AnyPropertyType).value
for winid in winid_list:
    window = disp.create_resource_object('window', winid)

    ppp = getProp(disp,window,'DESKTOP')
    on_desktop = ppp.tolist()[0]
    
    prop = window.get_full_property(NET_CLIENT_LIST_ATOM_T, Xlib.X.AnyPropertyType)
    if prop:
        if prop.value.tolist()[0] == NET_CLIENT_LIST_ATOM_N:
            # add to list
            list_normal_win.append((hex(window.id), window.get_wm_name(), on_desktop))

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

# hex function bug - add the leading 0
# h class string
def right_hex(h):
    c = h.strip("0x")
    if len(c) == 7:
        return "0x0"+c
    else:
        return h

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

# track a created or closed window or a changed active window
class CDThread(threading.Thread):
    
    def __init__(self3):
        threading.Thread.__init__(self3)
        self3.event = threading.Event()
        global cd_event
        cd_event = self3.event
    
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
                    sct = [self3.get_window_name(win), win]
                    # set the related var with univocal data
                    sctVar.set(win)
                ########## END ACTIVE WINDOW
                
                
                def handle_event(event):
                    # a new window is created
                    if (event.type == Xlib.X.CreateNotify):
                        window = disp.create_resource_object('window', event.window)

                        is_type = None
                        # some window are NoneType
                        try:
                            winName = getProp(disp, event.window, 'NAME')
                            winPid = getProp(disp, event.window, 'PID')[0]
                            is_type = getProp(disp, event.window,'WINDOW_TYPE')[0]
                        except:
                            pass
                        
                        # if it is a normal type
                        if is_type and disp.get_atom_name(is_type) == "_NET_WM_WINDOW_TYPE_NORMAL":
                            if winName and winPid:
                                prop = window.get_full_property(NET_CLIENT_LIST_ATOM_T, Xlib.X.AnyPropertyType)
                                if prop:
                                    # on which desktop
                                    on_desktop = None
                                    while on_desktop == None:
                                        on_desktop = get_win_desktop(event.window.id)
                                    
                                    win_hex = right_hex(hex(event.window.id))
                                    newData = (win_hex, winName.decode(), on_desktop)
                                    if not newData in list_normal_win:
                                        list_normal_win.append(newData)
                    ##
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
                                    #the index of the closed window
                                    idx = list_normal_win.index(el)
                                    # remove el
                                    list_normal_win.remove(el)
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
        
        # list of window id and button id
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
    
    # add or remove a button for an opened window at startup
    def flist_desktop_windows2(self):
        # all the normal windows
        wl_data = subprocess.check_output(["wmctrl", "-l"])
        wl = wl_data.decode()
        aa = wl.splitlines()
        # needed for removing the button of closed applications from the frame
        #self.list_desktop_windows_temp = []
        self.list_desktop_windows_temp = self.list_desktop_windows
        # reset
        self.list_desktop_windows = []
        
        for el in aa:
            ind = el[11:13]
            if ind == " 0":
                bb = el.split()
                
                # join the member of the list into a string
                win_title = " ".join(bb[3:])
                self.list_desktop_windows.append([bb[0],win_title])
        
        # populate bbb
        bbb = []
        for el in self.list_desktop_windows_temp:
            bbb.append([el[0],el[1]])
        
        # add a button to the frame if a window has been found
        for el in self.list_desktop_windows:
            if el not in bbb:
                self.btn = ttk.Button(self.win_btns_frame, style="Color.TButton", text=el[1][0:10]+"...", command=lambda x=el[0]: self.fwinbtn(x))
                self.list_id.append([el[0], self.btn])
                self.btn.grid(row=0, column=self.i, ipady=vd_btn_pady, sticky="ns")
                self.i += 1

        ######### highlight the current window button
        #
        for el in self.list_id:

            # sct tuple: b'name' wid
            if el[0] == right_hex(hex(sct[1])):
                # set its state
                el[1].state(["pressed"])
            else:
                # set the state of the other buttons
                el[1].state(["!pressed"])

    # activate or minimize the selected window from the frame
    def fwinbtn(self, wid):
        # sct: tuple: b'name' and wid type int
        # the current active window
        active_window = right_hex(hex(sct[1]))
        # if active window minimize it
        if active_window == wid:
            os.system("wmctrl -ir {} -b toggle,hidden".format(wid))
        # if not active window
        else:
            os.system("wmctrl -ia {}".format(wid))

    # the current active window var
    def callback(self, *args):

        # make the changes into the window button frame
        self.flist_desktop_windows(sct)
   
    # related to the window buttons after a window has been closed
    def callback2(self, *args):
        print("new value 2", args)
   
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
        
        self.columnconfigure(0, weight=0)
        self.columnconfigure(1, weight=0)
        self.columnconfigure(2, weight=0)
        self.columnconfigure(3, weight=0)
        self.columnconfigure(4, weight=0)
        self.columnconfigure(5, weight=0)
        self.columnconfigure(6, weight=1)
        self.columnconfigure(7, weight=0)
        
        #
        #### the menu button
        self.menu_img = tk.PhotoImage(file="icons/menu.png")
        self.menu_btn = ttk.Button(self, style="Color.TButton", image=self.menu_img, command=self.fmenu_btn)
        self.menu_btn.grid(row=0, column=0, sticky="nwse", padx=2)
        #
        #### the virtual desktop buttons
        # the list of the buttons
        self.vd_btn_list = []
        # the virtual desktops buttons
        self.vdframe = ttk.Frame(self)
        self.vdframe.grid(row=0, column=1, padx=2)

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
        #### the windows buttons
        
        # control the current active window
        global sctVar
        self.sct_var = tk.StringVar()
        sctVar = self.sct_var
        #
        self.sct_var.trace("w", lambda *args:self.callback(sctVar))
        #
        
        self.win_btns_frame = ttk.Frame(self)
        self.win_btns_frame.config(style='Color.TFrame')
        self.win_btns_frame.grid(row=0, column=5, sticky="nwse", padx=2)
        # starts the function that populats the frame
        self.flist_desktop_windows2()
        #
        #
        self.master.update_idletasks()
        
        # label as separator - expand
        self.sep_lbl = ttk.Label(self, text="")
        self.sep_lbl.config(style='Color.TLabel')
        self.sep_lbl.grid(row=0, column=6, sticky="nwse")

        # label
        self.sep2_lbl = ttk.Label(self, text="Time")
        self.sep2_lbl.config(style='Color.TLabel')
        self.sep2_lbl.grid(row=0, column=10, sticky="nwse")
        
        #### run the thread
        
        # window opened or closed or active 
        self.cd = CDThread()
        self.cd.start()
        
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
    def fvd(self, nvd):
        try:
            # change virtual desktop
            os.system("wmctrl -s {}".format(nvd))
            ################# 
            active_virtual_desktop_data = subprocess.check_output(["wmctrl", "-d"])
            list_active_virtual_desktop_data_decoded = active_virtual_desktop_data.decode().splitlines()
            #
            list_active_virtual_desktop_data = []
            for el in list_active_virtual_desktop_data_decoded:
                list_active_virtual_desktop_data.append(el.replace("  "," ").split(" "))
            # find the current active desktop
            for el in list_active_virtual_desktop_data:
                if el[1] == "*":
                    active_virtual_desktop = int(el[0])
                    break
            #############
            for i in range(len(self.vd_btn_list)):
                if i == active_virtual_desktop:
                    self.vd_btn_list[i].state(["pressed"])
                else:
                    self.vd_btn_list[i].state(["!pressed"])
        except:
            pass
        
    # the show the desktop switcher
    def fshow_desk(self):
        try:
            if self.desk_switcher == "off":
                self.desk_switcher = "on"
            else:
                self.desk_switcher = "off"
            os.system("wmctrl -k {}".format(self.desk_switcher))
        except:
            pass

    # the menu window
    def fmenuWindow(self):

        self.menuWindow = tk.Toplevel(self.master)
        self.menuWindow.overrideredirect(True)
        self.menuWindow.attributes("-topmost", True)
        self.menuWindow.configure(background="#222c3d")
        #
        # populate the menu
        # list of list: category - name - exec - icon
        self.menus = pop_menu.getMenu().retList()
        
        # style
        ttk.Style().configure("Color2.TLabel", background="#122645", foreground="white")
        
        i = 0
        # the list of the category found
        self.l_cat = []
        # the list of the labels of the menu
        self.list_mlbl = []
        for el in self.menus[0]:
            # [item.name, item.path, idx, item.name.lower(), pexec, icon]
            cat = el[2]
            if cat not in self.l_cat:
                if cat == "Missed":
                    continue
                lbl = ttk.Label(self.menuWindow, text=cat, style="Color.TLabel")
                lbl.grid(row=i, column=0, sticky="we", padx=10, pady=5)
                self.list_mlbl.append(lbl)
                ### 
                lbl.bind("<Enter>", self.on_enter)
                lbl.bind("<Leave>", self.on_leave)
                self.l_cat.append(cat)
                i += 1
        #
        self.menuWindow.update_idletasks()
        width = self.menuWindow.winfo_width() + 50
        height = self.menuWindow.winfo_height()

        x = 1
        y = screen_height - prog_height - height -100 
        self.menuWindow.geometry('+{}+{}'.format(x, y))
        #
        self.mw_isopen = 1
        # the last menu label highlighted
        self.last_lbl = None 

    # the mouse on the menu entry
    def on_enter(self, event):
        
        if self.last_lbl:
            self.last_lbl.configure(style="Color.TLabel")
            # remove the submenu
            self.smenuWindow.destroy()
            # reset
            self.last_lbl = None 
        
        event.widget.configure(style="Color2.TLabel")
        
        parent = event.widget.winfo_toplevel()
        #
        ## calculate the height of each cell
        parent_width = parent.winfo_width()
        parent_height = parent.winfo_height()
        # the pad added vertically
        pad_y = 5
        # how many categories
        num_cat = len(self.l_cat)
        # the height of each entries in the menu
        entry_height = (parent_height / num_cat)
        # the position of the pointer in the menu
        y_pos = parent.winfo_pointery() - parent.winfo_rooty()
        # the position in the menu
        n_pos = math.ceil(y_pos / entry_height)
        # the label of the highlighted label
        hi_lbl = self.list_mlbl[n_pos-1].cget("text")
        # create a new subwindow: category - window width
        self.fsmenuWindow(hi_lbl, parent_width, parent_height)
    
    # the mouse leaves the menu entry
    def on_leave(self, event):
        self.last_lbl = event.widget
    
    # the submenu window
    def fsmenuWindow(self, hi_lbl, parent_width, parent_height):
        
        self.smenuWindow = tk.Toplevel(self.master)
        self.smenuWindow.overrideredirect(True)
        self.smenuWindow.attributes("-topmost", True)
        # the color
        self.smenuWindow.configure(background="#222c3d")
        
        ## style
        ##########
        # the list of the category found
        self.l_cat2 = []
        # the list of the labels
        self.list_entries = []
        for el in self.menus[0]:
            # [item.name, item.path, idx, item.name.lower(), pexec, icon]
            cat = el[2]
            if cat == hi_lbl:
                # added to the list
                self.list_entries.append(el)
        #
        # populate 
        i = 0
        # list of labels
        self.list_smlbl = []
        # [item.name, item.path, idx, item.name.lower(), pexec, icon]
        for item in self.list_entries:
            name = item[0]
            pexec = item[4]
            ##icon = item[5]
            
            lbl = ttk.Label(self.smenuWindow, text=name, style="Color.TLabel")
            lbl.grid(row=i, column=0, sticky="we", padx=10, pady=5)
            self.list_smlbl.append(lbl)
            ### 
            lbl.bind("<Button-1>", lambda event,x=pexec:self.execProg(event,x))
            lbl.bind("<Enter>", self.on_senter)
            lbl.bind("<Leave>", self.on_sleave)
            self.l_cat2.append(cat)
            i += 1
        
        if len(self.list_entries) <= len(self.l_cat):
            ppad = len(self.l_cat) * (self.linespace + 5)
        else:
            ppad = len(self.list_entries) * (self.linespace + 5)
        
        x = 1 + parent_width
        y = screen_height - prog_height - ppad - 150
        self.smenuWindow.geometry('+{}+{}'.format(x, y))
        #
        self.smw_isopen = 1
    
    # the mouse on the menu entry
    def on_senter(self, event):
        event.widget.configure(style="Color2.TLabel")
    
    # the mouse leave the menu entry
    def on_sleave(self, event):
        event.widget.configure(style="Color.TLabel")
    
    # exec the program
    def execProg(self, event, prog):
        subprocess.Popen([prog], shell=True)
        # close the submenu
        self.smenuWindow.destroy()
        # close the menu
        self.fcmenuWindow()
    
    # the menu closes after three seconds
    # related to the below function
    def menuClose(self):
        # no submenu open
        if self.smw_isopen == 0:
            # reset
            self.mw_isopen = 0
            self.menuWindow.destroy()
    
    # the mouse leaves the menu
    def on_wleave(self, event):
        self.master.after(3, self.menuClose)
    
    # close the menuWindow
    def fcmenuWindow(self):
        if self.mw_isopen:
            # close the submenu
            self.smenuWindow.destroy()
            # reset
            self.mw_isopen = 0
            self.menuWindow.destroy()

def windowExit():
    global cd_event
    cd_event.set()
    global stopCD
    stopCD = 1
    root.destroy()
        
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
wposy = screen_height - prog_height -100
root.geometry('{}x{}+{}+{}'.format(prog_width, prog_height, wposx, wposy))
######
# the theme
s=ttk.Style()
if "clam" in s.theme_names():
    s.theme_use("clam")

app = Application(master=root)

######

app.mainloop()
