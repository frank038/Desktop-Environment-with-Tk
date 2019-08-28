#!/usr/bin/env python3

import tkinter as tk
import tkinter.ttk as ttk
import tkinter.font as tkf
import time

class rightWidgets:
    def __init__(rw, master_frame):
        #print("*class rightWidgets*")
        rw.mf = master_frame
        
        ## label
        rw.mf.time_var = tk.StringVar()
        rw.time_lbl = ttk.Label(rw.mf, textvariable=rw.mf.time_var)
        rw.time_lbl.config(style='Color.TLabel')
        # to do for each widget
        rw.mf.rowconfigure(0, weight=1)
        rw.time_lbl.grid(row=0, column=0, sticky="ns")
        
        # set the time
        rw.lblTime()
        
    # 
    def lblTime(rw):
        #now = time.strftime("%H:%M:%S")
        now = time.strftime("%H:%M")
        rw.mf.time_var.set(now)
        # every 30 seconds
        rw.mf.after(30000, rw.lblTime)

