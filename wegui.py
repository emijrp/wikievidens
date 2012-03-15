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

#stats modules
import matplotlib
matplotlib.use('TkAgg')
from numpy import arange, sin, pi
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.figure import Figure
import pylab

#wikievidens modules
import weparser

#globals
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

#start the fun
class WikiEvidens:
    def __init__(self, master):
        self.master = master
        self.availabledumps = []
        self.downloadeddumps = []
        self.activedb = ''
        self.wiki = ''
        self.downloadpath = 'download'
        self.preprocesspath = 'preprocess'
        self.exportpath = 'export'
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
        self.notebookpreprocesslabel1 = Label(self.framepreprocess, text="The second step is to preprocess a downloaded dataset or to load a preprocessed one.\n", anchor='center', font=self.font)
        self.notebookpreprocesslabel1.grid(row=0, column=0, columnspan=4, sticky=W)
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
        self.notebookexportlabel1 = Label(self.frameexport, text="You can export data from datasets.\n", anchor='center', font=self.font)
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
        self.framedownloadwikisbutton21 = Button(self.framedownloadwikis, text="Scan available dumps", command=lambda: thread.start_new_thread(self.loadAvailableDumps, ()), width=15)
        self.framedownloadwikisbutton21.grid(row=2, column=0)
        self.framedownloadwikisbutton23 = Button(self.framedownloadwikis, text="Download selection", command=lambda: thread.start_new_thread(self.downloadDump, ()), width=15)
        self.framedownloadwikisbutton23.grid(row=2, column=1)
        self.framedownloadwikisbutton22 = Button(self.framedownloadwikis, text="Clear list", command=self.deleteAvailableDumps, width=10)
        self.framedownloadwikisbutton22.grid(row=2, column=2)
        #end download wikis tab
        
        #start download other tab
        self.framedownloadotherlabel1 = Label(self.framedownloadother, text="Choose a dataset to download.", anchor='center', font=self.font)
        self.framedownloadotherlabel1.grid(row=0, column=0, columnspan=3, sticky=W)
        #end download other tab
        
        #start download dumpgenerator tab
        self.framedownloaddumpgeneratorlabel1 = Label(self.framedownloaddumpgenerator, text="You can download a wiki using API or index.php methods.", anchor='center', font=self.font)
        self.framedownloaddumpgeneratorlabel1.grid(row=0, column=0, columnspan=3, sticky=W)
        #end download dumpgenerator tab
        
        #start preprocess tab
        self.framepreprocesstreescrollbar = Scrollbar(self.framepreprocess)
        self.framepreprocesstreescrollbar.grid(row=1, column=4, sticky=W+E+N+S)
        framepreprocesscolumns = ('dump', 'wikifarm', 'size', 'date', 'status')
        self.framepreprocesstree = ttk.Treeview(self.framepreprocess, height=27, columns=framepreprocesscolumns, show='headings', yscrollcommand=self.framepreprocesstreescrollbar.set)
        self.framepreprocesstreescrollbar.config(command=self.framepreprocesstree.yview)
        self.framepreprocesstree.column('dump', width=460, minwidth=460, anchor='center')
        self.framepreprocesstree.heading('dump', text='Dump')
        self.framepreprocesstree.column('wikifarm', width=100, minwidth=100, anchor='center')
        self.framepreprocesstree.heading('wikifarm', text='Wikifarm')
        self.framepreprocesstree.column('size', width=100, minwidth=100, anchor='center')
        self.framepreprocesstree.heading('size', text='Size')
        self.framepreprocesstree.column('date', width=100, minwidth=100, anchor='center')
        self.framepreprocesstree.heading('date', text='Date')
        self.framepreprocesstree.column('status', width=240, minwidth=240, anchor='center')
        self.framepreprocesstree.heading('status', text='Status')
        self.framepreprocesstree.grid(row=1, column=0, columnspan=4, sticky=W+E+N+S)
        #[self.framepreprocesstree.heading(column, text=column, command=lambda: self.treeSortColumn(column=column, reverse=False)) for column in columns]        
        #self.framepreprocesstree.bind("<Double-1>", (lambda: thread.start_new_thread(self.downloadDump, ())))
        self.framepreprocesstree.tag_configure('preprocessed', background='lightgreen')
        self.framepreprocesstree.tag_configure('nopreprocessed', background='white')
        self.framepreprocessbutton23 = Button(self.framepreprocess, text="Scan downloaded dumps", command=lambda: thread.start_new_thread(self.loadDownloadedDumps, ()), width=20)
        self.framepreprocessbutton23.grid(row=2, column=0)
        self.framepreprocessbutton23 = Button(self.framepreprocess, text="Preprocess selection", command=lambda: thread.start_new_thread(self.preprocessDump, ()), width=15)
        self.framepreprocessbutton23.grid(row=2, column=1)
        self.framepreprocessbutton23 = Button(self.framepreprocess, text="Load", command=lambda: thread.start_new_thread(self.activePreprocessedDump, ()), width=15)
        self.framepreprocessbutton23.grid(row=2, column=2)
        self.framepreprocessbutton22 = Button(self.framepreprocess, text="Clear list", command=self.deleteDownloadedDumps, width=10)
        self.framepreprocessbutton22.grid(row=2, column=3)
        #end preprocess tab
        
        #start analysis global tab
        f = Figure(figsize=(8,5), dpi=100)
        a = f.add_subplot(111)
        t = arange(0.0,3.0,0.01)
        s = sin(20*pi*t)
        a.plot(t,s)
        canvas = FigureCanvasTkAgg(f, master=self.frameanalysisglobal)
        canvas.show()
        canvas.get_tk_widget().pack(side=TOP, fill=BOTH, expand=1)
        toolbar = NavigationToolbar2TkAgg( canvas, self.frameanalysisglobal )
        toolbar.update()
        canvas._tkcanvas.pack(side=TOP, fill=BOTH, expand=1)
        
        button1 = Button(self.frameanalysisglobal, text='Yearly graph', command=lambda: self.analysis('global-activity-yearly'), width=10)
        button1.pack(side=TOP, fill=BOTH, expand=1)
        #end analysis global tab
    
    def activePreprocessedDump(self):
        items = self.framepreprocesstree.selection()
        if len(items) == 1:
            filepath = self.preprocesspath and self.preprocesspath + '/' + self.downloadeddumps[int(items[0])][0] + '.db' or self.downloadeddumps[int(items[0])][0] + '.db'
            if os.path.exists(filepath):
                self.activedb = filepath
                self.notebookanalysislabel1.config(text='You are analysing "%s".\n' % (self.activedb))
                self.msg(msg="Loaded succesfull. Now, you can analyse.", level="info")
            else:
                self.msg(msg="That preprocessed dump doesn't exist.", level="error")
        else:
            self.msg(msg="You only can load a preprocessed dump a time.", level="error")
            return
    
    def analysis(self, analysis):
        if not self.activedb:
            self.msg(msg="You must load a preprocessed dump first", level="error")
            return
        
        conn = sqlite3.connect(self.activedb)
        cursor = conn.cursor()

        #global
        if analysis.startswith('global'):
            if analysis == 'global-summary':
                import wesummary
                wesummary.summary(cursor=cursor)
            elif analysis.startswith('global-activity'):
                import weactivity
                if analysis == 'global-activity-all':
                    weactivity.activityall(cursor=cursor, range='global', title=self.wiki)
                elif analysis == 'global-activity-yearly':
                    weactivity.activityyearly(cursor=cursor, range='global', title=self.wiki)
                elif analysis == 'global-activity-monthly':
                    weactivity.activitymonthly(cursor=cursor, range='global', title=self.wiki)
                elif analysis == 'global-activity-dow':
                    weactivity.activitydow(cursor=cursor, range='global', title=self.wiki)
                elif analysis == 'global-activity-hourly':
                    weactivity.activityhourly(cursor=cursor, range='global', title=self.wiki)
                pylab.show()
        
        cursor.close()
        conn.close()
    
    def callback(self):
        self.msg("Feature not implemented for the moment. Contributions are welcome.", level='info')
    
    def msg(self, msg='', level=''):
        levels = { 'info': 'lightgreen', 'warning': 'yellow', 'error': 'pink' }
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
                filepath = self.downloadpath and self.downloadpath + '/' + self.availabledumps[int(item)][0] or self.availabledumps[int(item)][0]
                if os.path.exists(filepath):
                    self.msg('That dump was downloaded before', level='info')
                    d += 1
                else:
                    self.msg("[%d of %d] Downloading %s from %s" % (c+1, len(items), self.framedownloadwikistree.item(item,"text"), self.availabledumps[int(item)][5]))
                    f = urllib.urlretrieve(self.availabledumps[int(item)][5], filepath, reporthook=self.downloadProgress)
                    msg='%s size is %s bytes large. Download successful!' % (self.availabledumps[int(item)][0], os.path.getsize(filepath))
                    self.msg(msg=msg, level='info')
                    c += 1
                self.availabledumps[int(item)] = self.availabledumps[int(item)][:6] + ['True']
            if c + d == len(items):
                self.msg('Downloaded %d of %d%s.' % (c, len(items), d and ' (and %d were previously downloaded)' % (d) or ''), level='ok')
            else:
                self.msg('Problems in %d dumps. Downloaded %d of %d (and %d were previously downloaded).' % (len(items)-(c+d), c, len(items), d), level='error')
        else:
            self.msg(msg="You have to select some dumps to download.", level="error")
        self.clearAvailableDumps()
        self.showAvailableDumps()
        #self.filterAvailableDumps()
        self.block = False
    
    def deleteAvailableDumps(self):
        #really delete dump list and clear tree
        self.clearAvailableDumps()
        self.availabledumps = [] #reset list
    
    def deleteDownloadedDumps(self):
        #really delete downloaded dump list and clear tree
        self.clearDownloadedDumps()
        self.downloadeddumps = [] #reset list
    
    def clearAvailableDumps(self):
        #clear tree
        for i in range(len(self.availabledumps)):
            self.framedownloadwikistree.delete(str(i))
    
    def clearDownloadedDumps(self):
        #clear tree
        for i in range(len(self.downloadeddumps)):
            self.framepreprocesstree.delete(str(i))
    
    def showAvailableDumps(self):
        c = 0
        for filename, wikifarm, size, date, mirror, url, downloaded in self.availabledumps:
            self.framedownloadwikistree.insert('', 'end', str(c), text=filename, values=(filename, wikifarm, size, date, mirror, downloaded and 'Downloaded' or 'Not downloaded'), tags=(downloaded and 'downloaded' or 'nodownloaded',))
            c += 1
    
    def showDownloadedDumps(self):
        c = 0
        for filename, wikifarm, size, date, preprocessed in self.downloadeddumps:
            self.framepreprocesstree.insert('', 'end', str(c), text=filename, values=(filename, wikifarm, size, date, preprocessed and 'Preprocessed' or 'Not preprocessed'), tags=(preprocessed and 'preprocessed' or 'nopreprocessed',))
            c += 1
    
    def isDumpDownloaded(self, filename=''):
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
    
    def isDumpPreprocessed(self, filename=''):
        #improve?
        if filename:
            filepath = self.preprocesspath and self.preprocesspath + '/' + filename +'.db' or filename + '.db'
            if os.path.exists(filepath):
                return True
        return False
    
    def getDateFromFilename(self, filename=''):
        date = 'Unknown'
        if re.search(ur"\-(\d{8})[\.-]", filename):
            date = re.findall(ur"\-(\d{4})(\d{2})(\d{2})[\.-]", filename)[0]
            date = '%s-%s-%s' % (date[0], date[1], date[2])
        elif re.search(ur"\-(\d{4}\-\d{2}\-\d{2})[\.-]", filename):
            date = re.findall(ur"\-(\d{4}\-\d{2}\-\d{2})[\.-]", filename)[0]
        return date
    
    def getWikifarmFromFilename(self, filename=''):
        wikifarms_r = re.compile(ur"(%s)" % ('|'.join(wikifarms.keys())))
        wikifarm = 'Unknown'
        if re.search(wikifarms_r, filename):
            wikifarm = re.findall(wikifarms_r, filename)[0]
        wikifarm = wikifarms[wikifarm]
        return wikifarm
    
    def loadAvailableDumps(self):
        if self.block:
            self.blocked()
            return
        else:
            self.block = True
        if self.availabledumps:
            self.deleteAvailableDumps()
        iaregexp = ur'/download/[^/]+/(?P<filename>[^>]+\.7z)">\s*(?P<size>[\d\.]+ (?:KB|MB|GB|TB))\s*</a>'
        self.urls = [
            ['Google Code', 'https://code.google.com/p/wikiteam/downloads/list?num=5000&start=0', ur'(?im)detail\?name=(?P<filename>[^&]+\.7z)&amp;can=2&amp;q=" style="white-space:nowrap">\s*(?P<size>[\d\.]+ (?:KB|MB|GB|TB))\s*</a></td>'],
            #['Internet Archive', 'http://www.archive.org/details/referata.com-20111204', iaregexp],
            #['Internet Archive', 'http://www.archive.org/details/WikiTeamMirror', iaregexp],
            #['ScottDB', 'http://mirrors.sdboyd56.com/WikiTeam/', ur'<a href="(?P<filename>[^>]+\.7z)">(?P<size>[\d\.]+ (?:KB|MB|GB|TB))</a>'],
            #['Wikimedia', 'http://dumps.wikimedia.org/backup-index.html', ur'(?P<size>)<a href="(?P<filename>[^>]+)">[^>]+</a>: <span class=\'done\'>Dump complete</span></li>']
        ]
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
                wikifarm = self.getWikifarmFromFilename(filename)
                size = i.group('size')
                if not size:
                    size = 'Unknown'
                date = self.getDateFromFilename(filename)
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
                self.availabledumps.append([filename, wikifarm, size, date, mirror, downloadurl, downloaded])
        self.availabledumps.sort()
        self.showAvailableDumps()
        #self.filterAvailableDumps()
        self.msg(msg='Loaded %d available dumps!' % (len(self.availabledumps)), level='info')
        self.block = False
    
    def loadDownloadedDumps(self):
        if self.block:
            self.blocked()
            return
        else:
            self.block = True
        if self.downloadeddumps:
            self.deleteDownloadedDumps()
        
        for filename in os.listdir(self.downloadpath):
            wikifarm = self.getWikifarmFromFilename(filename)
            size = os.path.getsize('%s/%s' % (self.downloadpath, filename))
            date = self.getDateFromFilename(filename)
            preprocessed = self.isDumpPreprocessed(filename)
            self.downloadeddumps.append([filename, wikifarm, size, date, preprocessed])
        
        self.downloadeddumps.sort()
        self.showDownloadedDumps()
        #self.filterDownloadedDumps()
        #self.msg(msg='Loaded %d downloaded dumps!' % (len(self.downloadeddumps)), level='info')
        self.block = False
    
    def preprocessDump(self):
        if self.block:
            self.blocked()
            return
        else:
            self.block = True
        items = self.framepreprocesstree.selection()
        if items:
            if not os.path.exists(self.preprocesspath):
                os.makedirs(self.preprocesspath)
            c = 0
            d = 0
            for item in items:
                filepath = self.preprocesspath and self.preprocesspath + '/' + self.downloadeddumps[int(item)][0] + '.db' or self.downloadeddumps[int(item)][0] + '.db'
                if os.path.exists(filepath):
                    self.msg('That dump was preprocessed before', level='info')
                    d += 1
                else:
                    self.msg("[%d of %d] Preprocessing %s" % (c+1, len(items), self.framepreprocesstree.item(item,"text")))
                    dumppath = self.downloadpath + '/' + self.downloadeddumps[int(item)][0]
                    weparser.parseMediaWikiXMLDump(dumpfilename=dumppath, dbfilename=filepath)
                    msg='%s size is %s bytes large. Preprocess successful!' % (self.downloadeddumps[int(item)][0] + '.db', os.path.getsize(filepath))
                    self.msg(msg=msg)
                    c += 1
                self.downloadeddumps[int(item)] = self.downloadeddumps[int(item)][:4] + ['True']
            if c:
                if c + d == len(items):
                    self.msg('Preprocessed %d of %d%s.' % (c, len(items), d and ' (and %d were previously preprocessed)' % (d) or ''), level='info')
                else:
                    self.msg('Problems in %d dumps. Preprocessed %d of %d (and %d were previously preprocessed).' % (len(items)-(c+d), c, len(items), d), level='error')
        else:
            tkMessageBox.showerror("Error", "You have to select some dumps to preprocess.")
        self.clearDownloadedDumps()
        self.showDownloadedDumps()
        #self.filterDownloadedDumps()
        self.block = False
    
def askclose():
    if tkMessageBox.askokcancel("Quit", "Do you really wish to exit?"):
        root.destroy()

if __name__ == "__main__":
    root = Tk()
    width, height = 1024, 758
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

