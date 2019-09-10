#!/usr/bin/env python3
## the following code has been extracted from pypanel

from Xlib import X, display, error, Xatom, Xutil
import Xlib.protocol.event
import sys

P_HEIGHT        = 50            # Panel height

TRAY_I_HEIGHT   = 48            # System tray icon height (usually 16 or 24)
TRAY_I_WIDTH    = 48            # System tray icon width  (usually 16 or 24)

TRAY            = 1             # System tray section

class Obj(object):
    """ Multi-purpose class """
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


class PyPanel(object):
    def __init__(self, parent_id):
        """ Initialize and display the panel """
        self.display = display.Display()         # Display obj
        self.screen  = self.display.screen()     # Screen obj
        self.root    = self.screen.root          # Display root
        self.parent_id = parent_id               # 
        self.error   = error.CatchError()        # Error Handler/Suppressor
        self.panel   = {"sections":[]}           # Panel data and layout
        
        global P_HEIGHT

        self.panel["sections"].append(TRAY)
        self.panel[TRAY] = Obj(id="tray", tasks={}, order=[])
        self.createTray(self.display, self.screen)
        
    """ Create the System Tray Selection Owner Window """
    def createTray(self, dsp, scr):
        self._OPCODE = dsp.intern_atom("_NET_SYSTEM_TRAY_OPCODE")
        manager      = dsp.intern_atom("MANAGER")
        selection    = dsp.intern_atom("_NET_SYSTEM_TRAY_S%d" % dsp.get_default_screen())
          
        # Selection owner window          
        self.selowin = scr.root.create_window(-1, -1, 50, 50, 0, self.screen.root_depth)
        self.selowin.set_selection_owner(selection, X.CurrentTime)
        self.sendEvent(self.root, manager,[X.CurrentTime, selection,
            self.selowin.id], (X.StructureNotifyMask))
        
        self.loop(self.display, self.root, self.selowin, self.panel)
        
    """ Send a ClientMessage event to the root """
    def sendEvent(self, win, ctype, data, mask=None):
        data = (data+[0]*(5-len(data)))[:5]
        ev = Xlib.protocol.event.ClientMessage(window=win, client_type=ctype, data=(32,(data)))

        if not mask:
            mask = (X.SubstructureRedirectMask|X.SubstructureNotifyMask)
        self.root.send_event(ev, event_mask=mask)
    
    
    """ Redraw the panel """
    def updatePanel(self, root, win, panel):
        curr_x   = 0
        tray     = None
            
        curr_x += 2
        tray = panel[TRAY]
        #
        if tray:
            for tid in tray.order:
                t = tid
                tx = curr_x
                twidth = 48
                theight = 48
                ty = int((P_HEIGHT-theight)/2)
                tobj = self.display.create_resource_object("window", t)
                tobj.configure(onerror=self.error, x=tx, y=ty, width=twidth, height=theight)
                tobj.map(onerror=self.error)
                curr_x += twidth

    """ Event loop - handle events as they occur until we're killed """ 
    def loop(self, dsp, root, win, panel):
        tray = panel[TRAY]
        while 1:
            e = dsp.next_event()
            if e.type == X.ConfigureNotify and TRAY:
                if e.window.id in tray.tasks:
                    task = tray.tasks[e.window.id]
                    task.obj.configure(onerror=self.error, width=task.width, height=task.height)                                            
            elif e.type == X.ClientMessage and TRAY:
                if e.window == self.selowin:
                    data = e.data[1][1] # opcode
                    task = e.data[1][2] # taskid
                    if e.client_type == self._OPCODE and data == 0:
                        obj = dsp.create_resource_object("window", task)
                        obj.reparent(int(self.parent_id), 0, 0)
                        obj.change_attributes(event_mask=(X.ExposureMask|X.StructureNotifyMask))
                        tray.tasks[task] = Obj(obj=obj, x=0, y=0, width=TRAY_I_WIDTH, height=TRAY_I_HEIGHT)
                        tray.order.append(task)                            
                        self.updatePanel(root, win, panel)
            ## an applet is been removed from the systray
            elif e.type == X.DestroyNotify:
                # delete the object from the list if it is a member
                if e.window.id in tray.order:
                    tray.order.remove(e.window.id)
                    # update
                    self.updatePanel(root, win, panel)
    
########## MAIN

if __name__ == "__main__":
    parent_id = sys.argv[1]
    PyPanel(parent_id)
