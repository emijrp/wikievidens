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
        self.block = False #semaphore
        self.font = ("Arial", 10)
        
        self.label1 = ttk.Label(self.master)
        self.label1.grid(row=0, column=0)
        
        #start main tabs
        self.notebook = ttk.Notebook(self.master)
        self.notebook.grid(row=1, column=0, columnspan=1, sticky=W+E+N+S)
        self.framedownload = ttk.Frame(self.master)
        self.notebook.add(self.framedownload, text='Download')
        self.framepreprocess = ttk.Frame(self.master)
        self.notebook.add(self.framepreprocess, text='Preprocess')
        self.frameanalysis = ttk.Frame(self.master)
        self.notebook.add(self.frameanalysis, text='Analysis')
        self.frameexport = ttk.Frame(self.master)
        self.notebook.add(self.frameexport, text='Export')
        #end main tabs
        
        #start download tabs
        self.notebookdownloadlabel1 = Label(self.framedownload, text="The first step is to download a dataset.", anchor=W, font=self.font)
        self.notebookdownloadlabel1.grid(row=0, column=0)
        self.notebookdownload = ttk.Notebook(self.framedownload)
        self.notebookdownload.grid(row=1, column=0, columnspan=1, sticky=W+E+N+S)
        self.framedownloadwikis = ttk.Frame(self.framedownload)
        self.notebookdownload.add(self.framedownloadwikis, text='Wikis')
        self.framedownloadother = ttk.Frame(self.framedownload)
        self.notebookdownload.add(self.framedownloadother, text='Other')
        self.framedownloaddumpgenerator = ttk.Frame(self.framedownload)
        self.notebookdownload.add(self.framedownloaddumpgenerator, text='Dump generator')
        #end download tabs
        
        #preprocess
        
        #start analysis tabs
        self.notebookanalysislabel1 = Label(self.frameanalysis, text="No preprocessed dump has been loaded yet.", anchor=W, font=self.font)
        self.notebookanalysislabel1.grid(row=0, column=0)
        self.notebookanalysis = ttk.Notebook(self.frameanalysis)
        self.notebookanalysis.grid(row=1, column=0, columnspan=1, sticky=W+E+N+S)
        self.frameanalysisglobal = ttk.Frame(self.frameanalysis)
        self.notebookanalysis.add(self.frameanalysisglobal, text='Global')
        self.frameanalysispages = ttk.Frame(self.frameanalysis)
        self.notebookanalysis.add(self.frameanalysispages, text='Pages')
        self.frameanalysisusers = ttk.Frame(self.frameanalysis)
        self.notebookanalysis.add(self.frameanalysisusers, text='Users')
        self.frameanalysissamples = ttk.Frame(self.frameanalysis)
        self.notebookanalysis.add(self.frameanalysissamples, text='Samples')
        #end analysis tabs
        
        #export
        
        #statusbar
        self.status = Label(self.master, text="Welcome to %s. What do you want to do today?" % (NAME), bd=1, justify=LEFT, relief=SUNKEN, width=127)
        self.status.grid(row=2, column=0, columnspan=1, sticky=W+E)

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

