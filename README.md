# Desktop-Environment-with-Tk
A DE made with python3/tk. Just for fun.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY. Anyone can use and modified it for any purpose.

Tk-Desktop
V. 08-22-2019 A

Required: Python3/Tkinter - Pyinotify - (the included TkinterDnD2).

At the moment the only component is the desktop. The next is a panel. It starts as a window, but has the code tu run it as a desktop (background application): just comment and decomment the right lines at the bottom of the file tkdesktop.py. Tkdesktop manages all the events but do not change nothing by itself, exept its config file: icon can be placed everywhere (except the recycle bin, its position is fixed and reserved), an icon appears if a new file or folder is created in the DATA sample folder and the item disappears if the related file or folder is deleted. The position of each item is momorized in a file. The drag and drop is supported with limitations. The image used as background must be a gif image.

Tk-Panel
v. 08-26-2019 A

Required: Python3/Tkinter - wmctrl - the python3 xdg module - the python3 Xlib module.

The panel implement almost everything: a menu, a virtual desktops switcher, a button to minimize/restore all the windows, a window list. The image is self explained. The menu is full working and can launch applications. The bar is not positioned really at the bottom, just to make sure that it not cover other panels (the position can be changed easily).


![My image](https://github.com/frank038/Desktop-Environment-with-Tk/blob/master/img1.jpg)

![My image](https://github.com/frank038/Desktop-Environment-with-Tk/blob/master/img2.jpg)
