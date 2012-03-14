#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2012 WikiEvidens <http://code.google.com/p/wikievidens/>
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os
import platform
import sqlite3
import thread
import webbrowser

#tkinter modules
from Tkinter import *
import ttk
import tkMessageBox
import tkSimpleDialog
import tkFileDialog

NAME = 'WikiEvidens'
VERSION = '0.0.1'
HOMEPAGE = 'http://code.google.com/p/wikievidens/'
LINUX = platform.system().lower() == 'linux'
PATH = os.path.dirname(__file__)
if PATH: os.chdir(PATH)

class WikiEvidens:
    def __init__(self, master):
        self.master = master

def askclose():
    if tkMessageBox.askokcancel("Quit", "Do you really wish to exit?"):
        root.destroy()

if __name__ == "__main__":
    root = Tk()
    width, height = 1024, 768
    # calculate position x, y
    x = (root.winfo_screenwidth()/2) - (width/2) 
    y = (root.winfo_screenheight()/2) - (height/2)
    root.geometry('%dx%d+%d+%d' % (width, height, x, y))
    root.minsize(width=width, height=height)
    root.maxsize(width=width, height=height)
    root.title('%s %s' % (NAME, VERSION))
    root.protocol("WM_DELETE_WINDOW", askclose)
    we = WikiEvidens(root)
    root.mainloop()

