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
        
        #start menu
        menu = Menu(self.master)
        master.config(menu=menu)

        #begin file menu
        filemenu = Menu(menu)
        menu.add_cascade(label="File", menu=filemenu)
        filemenu.add_command(label="Preferences", command=self.callback)
        filemenu.add_separator()
        filemenu.add_command(label="Exit", command=askclose)
        #end file menu
        
        #begin view menu
        viewmenu = Menu(menu)
        menu.add_cascade(label="View", menu=viewmenu)
        viewmenu.add_command(label="Console", command=self.callback)
        #end view menu

        #start help menu
        helpmenu = Menu(menu)
        menu.add_cascade(label="Help", menu=helpmenu)
        helpmenu.add_command(label="About", command=self.callback)
        helpmenu.add_command(label="FAQ", command=self.callback)
        helpmenu.add_command(label="WikiEvidens homepage", command=lambda: webbrowser.open_new_tab(HOMEPAGE))
        #end help menu
        
        #end menu
        
        self.label1 = ttk.Label(self.master)
        self.label1.grid(row=0, column=0)
        
        #start main tabs
        self.notebook = ttk.Notebook(self.master)
        self.notebook.grid(row=1, column=0, columnspan=1, sticky=W+E+N+S)
        self.framedownload = ttk.Frame(self.master)
        self.notebook.add(self.framedownload, text='(1) Download')
        self.framepreprocess = ttk.Frame(self.master)
        self.notebook.add(self.framepreprocess, text='(2) Preprocess')
        self.frameanalysis = ttk.Frame(self.master)
        self.notebook.add(self.frameanalysis, text='(3) Analysis')
        self.frameexport = ttk.Frame(self.master)
        self.notebook.add(self.frameexport, text='(4) Export')
        #end main tabs
        
        #start download tabs
        self.notebookdownloadlabel1 = Label(self.framedownload, text="The first step is to download a dataset.\n", anchor='center', font=self.font)
        self.notebookdownloadlabel1.grid(row=0, column=0, sticky=W)
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
        self.notebookanalysislabel1 = Label(self.frameanalysis, text="No preprocessed dump has been loaded yet.", anchor='center', font=self.font)
        self.notebookanalysislabel1.grid(row=0, column=0, sticky=W)
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
        self.status = Label(self.master, text="Welcome to %s. What do you want to do today?" % (NAME), bd=1, justify=LEFT, relief=SUNKEN, width=127, background='grey')
        self.status.grid(row=2, column=0, columnspan=1, sticky=W+E)
        
        #start download wikis tab
        self.framedownloadwikislabel1 = Label(self.framedownloadwikis, text="Choose a wiki dump to download.", anchor='center', font=self.font)
        self.framedownloadwikislabel1.grid(row=0, column=0, sticky=W)
        self.framedownloadwikistreescrollbar = Scrollbar(self.framedownloadwikis)
        self.framedownloadwikistreescrollbar.grid(row=1, column=1, sticky=W+E+N+S)
        framedownloadwikiscolumns = ('dump', 'wikifarm', 'size', 'date', 'mirror', 'status')
        self.framedownloadwikistree = ttk.Treeview(self.framedownloadwikis, height=29, columns=framedownloadwikiscolumns, show='headings', yscrollcommand=self.framedownloadwikistreescrollbar.set)
        self.framedownloadwikistreescrollbar.config(command=self.framedownloadwikistree.yview)
        self.framedownloadwikistree.column('dump', width=460, minwidth=460, anchor='center')
        self.framedownloadwikistree.heading('dump', text='Dump')
        self.framedownloadwikistree.column('wikifarm', width=100, minwidth=100, anchor='center')
        self.framedownloadwikistree.heading('wikifarm', text='Wikifarm')
        self.framedownloadwikistree.column('size', width=100, minwidth=100, anchor='center')
        self.framedownloadwikistree.heading('size', text='Size')
        self.framedownloadwikistree.column('date', width=100, minwidth=100, anchor='center')
        self.framedownloadwikistree.heading('date', text='Date')
        self.framedownloadwikistree.column('mirror', width=120, minwidth=120, anchor='center')
        self.framedownloadwikistree.heading('mirror', text='Mirror')
        self.framedownloadwikistree.column('status', width=120, minwidth=120, anchor='center')
        self.framedownloadwikistree.heading('status', text='Status')
        self.framedownloadwikistree.grid(row=1, column=0, columnspan=1, sticky=W+E+N+S)
        #[self.framedownloadwikistree.heading(column, text=column, command=lambda: self.treeSortColumn(column=column, reverse=False)) for column in columns]        
        #self.tree.bind("<Double-1>", (lambda: thread.start_new_thread(self.downloadDump, ())))
        self.framedownloadwikistree.tag_configure('downloaded', background='lightgreen')
        self.framedownloadwikistree.tag_configure('nodownloaded', background='white')
        #end download wikis tab
    
    def callback(self):
        self.msg("Feature not implemented for the moment. Contributions are welcome.", level='info')
    
    def msg(self, msg='', level=''):
        levels = { 'info': 'lightgreen', 'warning': 'yellow', 'error': 'red' }
        if levels.has_key(level.lower()):
            print '%s: %s' % (level.upper(), msg)
            self.status.config(text='%s: %s' % (level.upper(), msg), background=levels[level.lower()])
            if level.lower() == 'info':
                tkMessageBox.showinfo("Info", msg)
            elif level.lower() == 'warning':
                tkMessageBox.showwarning("Warning", msg)
            elif level.lower() == 'error':
                tkMessageBox.showerror("Error", msg)
        else:
            print msg
            self.status.config(text=msg, background='grey')

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

