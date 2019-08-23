#!/usr/bin/env python3

import tkinter as tk
import tkinter.ttk as ttk
import tkinter.font as tkf
from tkinter import messagebox
import os
import sys
import math
from pathlib import Path
import subprocess
import time
import threading
from user_modules import pop_menu

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
vd_btn_pady = (prog_height - menu_icon_size) / 2
 
### font sizes
font_size = 20
font_size2 = 20
font_size3 = 20

# the programs to get some X info
wnck = "wmctrl"
xdotool = "xdotool"
xwininfo = "xwininfo"
stalonetray = "stalonetray"

######### number of virtual desktop
#### using xdotool
virtual_desktops_data = subprocess.check_output([xdotool, "get_num_desktops"])
virtual_desktops = int(virtual_desktops_data.decode())
## the active virtual desktop - 0 is 1 etc.
active_virtual_desktop_data = subprocess.check_output([xdotool, "get_desktop"])
active_virtual_desktop = int(active_virtual_desktop_data.decode())

#
tt = object

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
    
    # add or remove a button for an opened window
    def flist_desktop_windows(self):
        tt = threading.Timer(1, self.flist_desktop_windows)
        tt.start()
        wl_data = subprocess.check_output([wnck, "-l"])
        wl = wl_data.decode()
        aa = wl.splitlines()

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
        
        # remove the button of closed applications from the frame
        for el in self.list_desktop_windows_temp[:]:
            if el not in self.list_desktop_windows:

                for ell in self.list_id:
                    if ell[0] == el[0]:
                        ell[1].grid_forget()

        bbb = []
        for el in self.list_desktop_windows_temp:
            bbb.append([el[0],el[1]])
        
        for el in self.list_desktop_windows:
            if el not in bbb:
                self.btn = ttk.Button(self.win_btns_frame, style="Color.TButton", text=el[1][0:10]+"...", command=lambda x=el[0]: self.fwinbtn(x))
                self.list_id.append([el[0], self.btn])
                self.btn.grid(row=0, column=self.i, ipady=vd_btn_pady, sticky="ns")
                self.i += 1
        
        # highlight the current window button
        curr_win_int = subprocess.check_output(["xdotool", "getactivewindow"]).decode()
        # from string to int
        curr_win = int(curr_win_int)
        #
        for el in self.list_id:
            if int(el[0], 16) == curr_win:
                # set its state
                el[1].state(["pressed"])
            else:
                # set the state of the other buttons
                el[1].state(["!pressed"])

    # activate and minimize or to front the selected window
    def fwinbtn(self, wid):
        try:
            # get the window state
            win_state_data_all = subprocess.check_output(["xwininfo", "-wm", "-id", wid])#, "|", "grep", "Hidden"])
            win_state_all = win_state_data_all.decode()
            if "Hidden" in win_state_all:
                os.system("xdotool windowactivate {}".format(int(wid, 16)))
            else:
                # if not hidden but it is only not the active window
                curr_win_int = subprocess.check_output(["xdotool", "getactivewindow"]).decode()
                # from int to hex
                curr_id = int(curr_win_int)
                # if not the active
                if int(wid, 16) != curr_id:
                    # bring it in front
                    os.system("xdotool windowactivate {}".format(int(wid, 16)))
                # it it is the active
                else:
                    os.system("xdotool windowminimize {}".format(int(wid, 16)))
        except:
            pass

    # 
    def create_widgets(self):
        ##### styles
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
        self.show_desk_btn.grid(row=0, column=2, sticky="nwse", padx=2)
        #
        #### the windows buttons
        self.win_btns_frame = ttk.Frame(self)
        self.win_btns_frame.config(style='Color.TFrame')
        self.win_btns_frame.grid(row=0, column=5, sticky="nwse", padx=2)
        # starts the function that populats the frame
        self.flist_desktop_windows()
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
            os.system("wmctrl -s {}".format(nvd))
            # set the state of the buttons
            active_virtual_desktop_data = subprocess.check_output([xdotool, "get_desktop"])
            active_virtual_desktop = int(active_virtual_desktop_data.decode())
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
        # the color
        self.menuWindow.configure(background="#222c3d")

        # populate the menu
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
        y = screen_height - prog_height - height -100 #-100 da togliere
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
        
        # the toplevel window - no winfo_parent()
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
        
    
    # close the menuWindow
    def fcmenuWindow(self):
        if self.mw_isopen:
            # close the submenu
            self.smenuWindow.destroy()
            # reset
            self.mw_isopen = 0
            self.menuWindow.destroy()
    
        
root = tk.Tk()
root.overrideredirect(True)
root.wm_attributes("-type", "dock")

# the name of this program
root.title("tk-panel")

def windowExit():
    root.destroy()

# if the folder is readable and writable
if not os.access(working_dir, os.W_OK | os.R_OK):
    messagebox.showinfo("ERROR", "the folder is not readable or writable")
    root.destroy()
    sys.exit()

root.protocol('WM_DELETE_WINDOW', windowExit)

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
