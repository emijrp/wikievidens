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
import random
import re
import sqlite3
import thread
import urllib
import webbrowser

#tkinter modules
from Tkinter import *
import ttk
import tkMessageBox
import tkSimpleDialog
import tkFileDialog

wikifarms = {
    'gentoo_wikicom': 'Gentoo Wiki',
    'opensuseorg': 'OpenSuSE',
    'referatacom': 'Referata',
    'shoutwikicom': 'ShoutWiki',
    'Unknown': 'Unknown',
    'wikanda': 'Wikanda',
    'wikifur': 'WikiFur',
    'wikimedia': 'Wikimedia',
    'wikitravelorg': 'WikiTravel',
    'wikkii': 'Wikkii',
}

NAME = 'WikiEvidens'
VERSION = '0.0.1'
HOMEPAGE = 'http://code.google.com/p/wikievidens/'
LINUX = platform.system().lower() == 'linux'
PATH = os.path.dirname(__file__)
if PATH: os.chdir(PATH)

class WikiEvidens:
    def __init__(self, master):
        self.master = master
        self.dumps = []
        self.downloadpath = 'downloads'
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
        
        #start preprocess tab
        self.notebookpreprocesslabel1 = Label(self.framepreprocess, text="TODO...\n", anchor='center', font=self.font)
        self.notebookpreprocesslabel1.grid(row=0, column=0, sticky=W)
        #end preprocess tab
        
        #start analysis tabs
        self.notebookanalysislabel1 = Label(self.frameanalysis, text="No preprocessed dump has been loaded yet.\n", anchor='center', font=self.font)
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
        
        #start export tab
        self.notebookexportlabel1 = Label(self.frameexport, text="TODO...\n", anchor='center', font=self.font)
        self.notebookexportlabel1.grid(row=0, column=0, sticky=W)
        #end export tab
        
        #statusbar
        self.status = Label(self.master, text="Welcome to %s. What do you want to do today?" % (NAME), bd=1, justify=LEFT, relief=SUNKEN, width=127, background='grey')
        self.status.grid(row=2, column=0, columnspan=1, sticky=W+E)
        
        #start download wikis tab
        self.framedownloadwikislabel1 = Label(self.framedownloadwikis, text="Choose a wiki dump to download.", anchor='center', font=self.font)
        self.framedownloadwikislabel1.grid(row=0, column=0, columnspan=3, sticky=W)
        self.framedownloadwikistreescrollbar = Scrollbar(self.framedownloadwikis)
        self.framedownloadwikistreescrollbar.grid(row=1, column=3, sticky=W+E+N+S)
        framedownloadwikiscolumns = ('dump', 'wikifarm', 'size', 'date', 'mirror', 'status')
        self.framedownloadwikistree = ttk.Treeview(self.framedownloadwikis, height=27, columns=framedownloadwikiscolumns, show='headings', yscrollcommand=self.framedownloadwikistreescrollbar.set)
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
        self.framedownloadwikistree.grid(row=1, column=0, columnspan=3, sticky=W+E+N+S)
        #[self.framedownloadwikistree.heading(column, text=column, command=lambda: self.treeSortColumn(column=column, reverse=False)) for column in columns]        
        #self.framedownloadwikistree.bind("<Double-1>", (lambda: thread.start_new_thread(self.downloadDump, ())))
        self.framedownloadwikistree.tag_configure('downloaded', background='lightgreen')
        self.framedownloadwikistree.tag_configure('nodownloaded', background='white')
        self.framedownloadwikisbutton21 = Button(self.framedownloadwikis, text="Load available dumps", command=lambda: thread.start_new_thread(self.loadAvailableDumps, ()), width=15)
        self.framedownloadwikisbutton21.grid(row=2, column=0)
        self.framedownloadwikisbutton23 = Button(self.framedownloadwikis, text="Download selection", command=lambda: thread.start_new_thread(self.downloadDump, ()), width=15)
        self.framedownloadwikisbutton23.grid(row=2, column=1)
        self.framedownloadwikisbutton22 = Button(self.framedownloadwikis, text="Clear list", command=self.deleteAvailableDumps, width=10)
        self.framedownloadwikisbutton22.grid(row=2, column=2)
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
    
    def blocked(self):
        self.msg(msg='There is a task in progress. Please, wait.', level='error')
    
    def downloadProgress(self, block_count, block_size, total_size):
        try:
            total_mb = total_size/1024/1024.0
            downloaded = block_count *(block_size/1024/1024.0)
            percent = downloaded/(total_mb/100.0)
            if not random.randint(0,10):
                msg = "%.1f MB of %.1f MB downloaded (%.1f%%)" % (downloaded, total_mb, percent <= 100 and percent or 100)
                self.msg(msg)
            #sys.stdout.write("%.1f MB of %.1f MB downloaded (%.2f%%)" %(downloaded, total_mb, percent))
            #sys.stdout.flush()
        except:
            pass
    
    def downloadDump(self, event=None):
        if self.block:
            self.blocked()
            return
        else:
            self.block = True
        items = self.framedownloadwikistree.selection()
        if items:
            if not os.path.exists(self.downloadpath):
                os.makedirs(self.downloadpath)
            c = 0
            d = 0
            for item in items:
                filepath = self.downloadpath and self.downloadpath + '/' + self.dumps[int(item)][0] or self.dumps[int(item)][0]
                if os.path.exists(filepath):
                    self.msg('That dump was downloaded before', level='ok')
                    d += 1
                else:
                    self.msg("[%d of %d] Downloading %s from %s" % (c+1, len(items), self.framedownloadwikistree.item(item,"text"), self.dumps[int(item)][5]))
                    f = urllib.urlretrieve(self.dumps[int(item)][5], filepath, reporthook=self.downloadProgress)
                    msg='%s size is %s bytes large. Download successful!' % (self.dumps[int(item)][0], os.path.getsize(filepath))
                    self.msg(msg=msg, level='ok')
                    c += 1
                self.dumps[int(item)] = self.dumps[int(item)][:6] + ['True']
            if c + d == len(items):
                self.msg('Downloaded %d of %d%s.' % (c, len(items), d and ' (and %d were previously downloaded)' % (d) or ''), level='ok')
            else:
                self.msg('Problems in %d dumps. Downloaded %d of %d (and %d were previously downloaded).' % (len(items)-(c+d), c, len(items), d), level='error')
        else:
            tkMessageBox.showerror("Error", "You have to select some dumps to download.")
        self.clearAvailableDumps()
        self.showAvailableDumps()
        #self.filterAvailableDumps()
        self.block = False
    
    def deleteAvailableDumps(self):
        #really delete dump list and clear tree
        self.clearAvailableDumps()
        self.dumps = [] #reset list
    
    def clearAvailableDumps(self):
        #clear tree
        for i in range(len(self.dumps)):
            self.framedownloadwikistree.delete(str(i))
    
    def showAvailableDumps(self):
        c = 0
        for filename, wikifarm, size, date, mirror, url, downloaded in self.dumps:
            self.framedownloadwikistree.insert('', 'end', str(c), text=filename, values=(filename, wikifarm, size, date, mirror, downloaded and 'Downloaded' or 'Not downloaded'), tags=(downloaded and 'downloaded' or 'nodownloaded',))
            c += 1
    
    def isDumpDownloaded(self, filename):
        #improve, size check or md5sum?
        if filename:
            filepath = self.downloadpath and self.downloadpath + '/' + filename or filename
            if os.path.exists(filepath):
                return True
        
        """estsize = os.path.getsize(filepath)
                c = 0
                while int(estsize) >= 1024:
                    estsize = estsize/1024.0
                    c += 1
                estsize = '%.1f %s' % (estsize, ['', 'KB', 'MB', 'GB', 'TB'][c])"""
        
        return False
    
    def loadAvailableDumps(self):
        if self.block:
            self.blocked()
            return
        else:
            self.block = True
        if self.dumps:
            self.deleteAvailableDumps()
        iaregexp = ur'/download/[^/]+/(?P<filename>[^>]+\.7z)">\s*(?P<size>[\d\.]+ (?:KB|MB|GB|TB))\s*</a>'
        self.urls = [
            ['Google Code', 'https://code.google.com/p/wikiteam/downloads/list?num=5000&start=0', ur'(?im)detail\?name=(?P<filename>[^&]+\.7z)&amp;can=2&amp;q=" style="white-space:nowrap">\s*(?P<size>[\d\.]+ (?:KB|MB|GB|TB))\s*</a></td>'],
            #['Internet Archive', 'http://www.archive.org/details/referata.com-20111204', iaregexp],
            #['Internet Archive', 'http://www.archive.org/details/WikiTeamMirror', iaregexp],
            #['ScottDB', 'http://mirrors.sdboyd56.com/WikiTeam/', ur'<a href="(?P<filename>[^>]+\.7z)">(?P<size>[\d\.]+ (?:KB|MB|GB|TB))</a>'],
            #['Wikimedia', 'http://dumps.wikimedia.org/backup-index.html', ur'(?P<size>)<a href="(?P<filename>[^>]+)">[^>]+</a>: <span class=\'done\'>Dump complete</span></li>']
        ]
        wikifarms_r = re.compile(ur"(%s)" % ('|'.join(wikifarms.keys())))
        c = 0
        for mirror, url, regexp in self.urls:
            print 'Loading data from', mirror, url
            self.msg(msg='Please wait... Loading data from %s %s' % (mirror, url))
            f = urllib.urlopen(url)
            m = re.compile(regexp).finditer(f.read())
            for i in m:
                filename = i.group('filename')
                if mirror == 'Wikimedia':
                    filename = '%s-pages-meta-history.xml.7z' % (re.sub('/', '-', filename))
                wikifarm = 'Unknown'
                if re.search(wikifarms_r, filename):
                    wikifarm = re.findall(wikifarms_r, filename)[0]
                wikifarm = wikifarms[wikifarm]
                size = i.group('size')
                if not size:
                    size = 'Unknown'
                date = 'Unknown'
                if re.search(ur"\-(\d{8})[\.-]", filename):
                    date = re.findall(ur"\-(\d{4})(\d{2})(\d{2})[\.-]", filename)[0]
                    date = '%s-%s-%s' % (date[0], date[1], date[2])
                elif re.search(ur"\-(\d{4}\-\d{2}\-\d{2})[\.-]", filename):
                    date = re.findall(ur"\-(\d{4}\-\d{2}\-\d{2})[\.-]", filename)[0]
                downloadurl = ''
                if mirror == 'Google Code':
                    downloadurl = 'https://wikiteam.googlecode.com/files/' + filename
                elif mirror == 'Internet Archive':
                    downloadurl = re.sub(ur'/details/', ur'/download/', url) + '/' + filename
                elif mirror == 'ScottDB':
                    downloadurl = url + '/' + filename
                elif mirror == 'Wikimedia':
                    downloadurl = 'http://dumps.wikimedia.org/' + filename.split('-')[0] + '/' + re.sub('-', '', date) + '/' + filename
                downloaded = self.isDumpDownloaded(filename)
                self.dumps.append([filename, wikifarm, size, date, mirror, downloadurl, downloaded])
        self.dumps.sort()
        self.showAvailableDumps()
        #self.filterAvailableDumps()
        self.msg(msg='Loaded %d available dumps!' % (len(self.dumps)), level='info')
        self.block = False
    
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

