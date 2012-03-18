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

import datetime
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
import wecore

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
VERSION = '0.0.5'
HOMEPAGE = 'http://code.google.com/p/wikievidens/'
LINUX = platform.system().lower() == 'linux'
PATH = os.path.dirname(__file__)
if PATH: os.chdir(PATH)

# Dependences:
# linux: python, python-tk, python-matplotlib, python-sqlite
#        optional: graphviz
# windows: 
# mac: 
#
# meter el xmlreader.py y el dumpgenerator.py usando svn externals?

# TODO:
#
# el nltk.downloader() usa tkinter y tiene una abuena interfaz con barra de progreso, pestañas y todo, mirar cómo está hecho
#
# indicar % progreso al parsear el dump, en función de una estimación por el tamaño del fichero (depende si es 7z, bzip, etc [leer tamaño del .xml comprimido directamente si es posible])
# almacenar sesiones o algo parecido para evitar tener que darle a preprocessing para que coja el proyecto, cada vez que arranca el programa
## pero al final tienes que cargar la sesión/workplace que te interese, estamos en las mismas
# capturar parámetros por si se quiere ejecutar sin gui desde consola: wegui.py --module=summary invalida la gui y muestra los datos por consola
# cargar los proyectos de wikimedia y wikia (almacenar en una tabla en un sqlite propia? y actualizar cada poco?) http://download.wikimedia.org/backup-index.html http://community.wikia.com/wiki/Hub:Big_wikis http://community.wikia.com/index.php?title=Special:Newwikis&dir=prev&limit=500&showall=0 http://www.mediawiki.org/wiki/Sites_using_MediaWiki
# Citizendium (interesantes gráficas http://en.citizendium.org/wiki/CZ:Statistics) no publican el historial completo, solo el current http://en.citizendium.org/wiki/CZ:Downloads
# permitir descargar solo el historial de una página (special:Export tiene la pega de que solo muestra las últimas 1000 ediciones), con la Api te traes todo en bloques de 500 pero hay que hacer una función que llame a la API (en vez de utilizar pywikipediabot para no añadir una dependencia más)
# hay otros dumps a parte de los 7z que tienen información útil, por ejemplo los images.sql con metadatos de las fotos, aunque solo los publica wikipedia
# usar getopt para capturar parámetros desde consola
# i18n http://www.learningpython.com/2006/12/03/translating-your-pythonpygtk-application/
# write documentation

#diferenciar entre activity (edits) y newpages

# Ideas para análisis de wikis:
# * reverts rate: ratio de reversiones (como de eficiente es la comunidad)
# * ip geolocation: http://software77.net/geo-ip/?license
# * análisis que permita buscar ciertas palabras en los comentarios de las ediciones
# * mensajes entre usuarios (ediciones de usuarios en user talk:)
# * calcular autoría por páginas (colorear el texto actual?)
# * red/blue links progress
# * http://meta.wikimedia.org/wiki/Research:Wikimedia_Summer_of_Research_2011/Summary_of_Findings
#
# Ideas para otros análisis que no usan dumps pero relacionados con wikis o wikipedia:
# * el feed de donaciones
# * log de visitas de domas?
# * conectarse a irc y poder hacer estadisticas en vivo? o con la api dejando una ventana de unos segundos?
#
# otras ideas:
# * mirar http://stats.wikimedia.org/reportcard/RC_2011_04_columns.html http://stats.wikimedia.org/reportcard/
# * exporter: ventana que marcando los items (registros de la bbdd) que te interesa, los exporta desde la bbdd hacia un CSV u otros formatos, exportar un rango de fechas de revisiones http://en.wikipedia.org/w/index.php?title=User_talk:Emijrp/Wikipedia_Archive&oldid=399534070#How_can_i_get_all_the_revisions_of_a_language_for_a_duration_.3F
# * necesidades de los investigadores http://www.mediawiki.org/wiki/Research_Data_Proposals
# * external links analysis: http://linkypedia.inkdroid.org/websites/9/users/
# que es más seguro hacer las cursor.execute, con ? o con %s ?
# 
# flipadas:
# * ampliar la información de un punto haciendo clic en él: http://matplotlib.sourceforge.net/examples/event_handling/data_browser.py
# * videos con matplotlib http://matplotlib.sourceforge.net/examples/animation/movie_demo.py
# * más ejemplos de matplotlib http://matplotlib.sourceforge.net/examples/index.html
# * mapas con R muy buenos http://flowingdata.com/2011/05/11/how-to-map-connections-with-great-circles/ http://www.webcitation.org/5zuFPrssa
#
# dispenser coord dumps: http://toolserver.org/~dispenser/dumps/

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
        self.outputpath = 'output'
        self.block = False #semaphore
        self.users = []
        self.pages = []
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
        self.framedownloadlive = ttk.Frame(self.framedownload)
        self.notebookdownload.add(self.framedownloadlive, text='Live!')
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
        self.notebookexportlabel1 = Label(self.frameexport, text="You can export data from datasets.\n\nTODO: date ranges, namespaces,...", anchor='center', font=self.font)
        self.notebookexportlabel1.grid(row=0, column=0, sticky=W)
        #end export tab
        
        #statusbar
        self.status = Label(self.master, text="Welcome to %s. What do you want to do today?" % (NAME), bd=1, justify=LEFT, relief=SUNKEN, width=127, background='grey')
        self.status.grid(row=2, column=0, columnspan=1, sticky=W+E)
        
        #start download wikis tab
        self.framedownloadwikislabel1 = Label(self.framedownloadwikis, text="Choose a wiki dump to download.", anchor='center', font=self.font)
        self.framedownloadwikislabel1.grid(row=0, column=0, columnspan=4, sticky=W)
        self.framedownloadwikistreescrollbar = Scrollbar(self.framedownloadwikis)
        self.framedownloadwikistreescrollbar.grid(row=1, column=3, sticky=W+E+N+S)
        framedownloadwikiscolumns = ('dump', 'wikifarm', 'size', 'date', 'mirror', 'status')
        self.framedownloadwikistree = ttk.Treeview(self.framedownloadwikis, height=24, columns=framedownloadwikiscolumns, show='headings', yscrollcommand=self.framedownloadwikistreescrollbar.set)
        self.framedownloadwikistreescrollbar.config(command=self.framedownloadwikistree.yview)
        self.framedownloadwikistree.column('dump', width=460, minwidth=460, anchor='center')
        self.framedownloadwikistree.heading('dump', text='Dump', command=lambda: self.treeSortColumn(tree='framedownloadwikistree', column='dump', reverse=False))
        self.framedownloadwikistree.column('wikifarm', width=100, minwidth=100, anchor='center')
        self.framedownloadwikistree.heading('wikifarm', text='Wikifarm', command=lambda: self.treeSortColumn(tree='framedownloadwikistree', column='wikifarm', reverse=False))
        self.framedownloadwikistree.column('size', width=100, minwidth=100, anchor='center')
        self.framedownloadwikistree.heading('size', text='Size', command=lambda: self.treeSortColumn(tree='framedownloadwikistree', column='size', reverse=False))
        self.framedownloadwikistree.column('date', width=100, minwidth=100, anchor='center')
        self.framedownloadwikistree.heading('date', text='Date', command=lambda: self.treeSortColumn(tree='framedownloadwikistree', column='date', reverse=False))
        self.framedownloadwikistree.column('mirror', width=120, minwidth=120, anchor='center')
        self.framedownloadwikistree.heading('mirror', text='Mirror', command=lambda: self.treeSortColumn(tree='framedownloadwikistree', column='mirror', reverse=False))
        self.framedownloadwikistree.column('status', width=120, minwidth=120, anchor='center')
        self.framedownloadwikistree.heading('status', text='Status', command=lambda: self.treeSortColumn(tree='framedownloadwikistree', column='status', reverse=False))
        self.framedownloadwikistree.grid(row=1, column=0, columnspan=3, sticky=W+E+N+S)
        #[self.framedownloadwikistree.heading(column, text=column, command=lambda: self.treeSortColumn(column=column, reverse=False)) for column in columns]        
        #self.framedownloadwikistree.bind("<Double-1>", (lambda: thread.start_new_thread(self.downloadDump, ())))
        self.framedownloadwikistree.tag_configure('downloaded', background='lightgreen')
        self.framedownloadwikistree.tag_configure('nodownloaded', background='white')
        #filters
        self.framedownloadwikislabelframe1 = LabelFrame(self.framedownloadwikis, text="Filter options")
        self.framedownloadwikislabelframe1.grid(row=2, column=1, rowspan=2, pady=5)
        self.framedownloadwikislabelframe1label1 = Label(self.framedownloadwikislabelframe1, text="Wikifarm:")
        self.framedownloadwikislabelframe1label1.grid(row=0, column=0, sticky=E)
        self.framedownloadwikislabelframe1optionmenu1var = StringVar(self.framedownloadwikislabelframe1)
        self.framedownloadwikislabelframe1optionmenu1var.set("all")
        self.framedownloadwikislabelframe1optionmenu1 = OptionMenu(self.framedownloadwikislabelframe1, self.framedownloadwikislabelframe1optionmenu1var, self.framedownloadwikislabelframe1optionmenu1var.get(), "Gentoo Wiki", "OpenSuSE", "Referata", "ShoutWiki", "Unknown", "Wikanda", "WikiFur", "Wikimedia", "WikiTravel", "Wikkii")
        self.framedownloadwikislabelframe1optionmenu1.grid(row=0, column=1)
        
        self.framedownloadwikislabelframe1label2 = Label(self.framedownloadwikislabelframe1, text="Size:")
        self.framedownloadwikislabelframe1label2.grid(row=1, column=0, sticky=E)
        self.framedownloadwikislabelframe1optionmenu2var = StringVar(self.framedownloadwikislabelframe1)
        self.framedownloadwikislabelframe1optionmenu2var.set("all")
        self.framedownloadwikislabelframe1optionmenu2 = OptionMenu(self.framedownloadwikislabelframe1, self.framedownloadwikislabelframe1optionmenu2var, self.framedownloadwikislabelframe1optionmenu2var.get(), "KB", "MB", "GB", "TB")
        self.framedownloadwikislabelframe1optionmenu2.grid(row=1, column=1)
        
        self.framedownloadwikislabelframe1label3 = Label(self.framedownloadwikislabelframe1, text="Date:")
        self.framedownloadwikislabelframe1label3.grid(row=0, column=2, sticky=E)
        self.framedownloadwikislabelframe1optionmenu3var = StringVar(self.framedownloadwikislabelframe1)
        self.framedownloadwikislabelframe1optionmenu3var.set("all")
        self.framedownloadwikislabelframe1optionmenu3 = OptionMenu(self.framedownloadwikislabelframe1, self.framedownloadwikislabelframe1optionmenu3var, self.framedownloadwikislabelframe1optionmenu3var.get(), "2005", "2006", "2007", "2008", "2009", "2010", "2011", "2012")
        self.framedownloadwikislabelframe1optionmenu3.grid(row=0, column=3)
        
        self.framedownloadwikislabelframe1label4 = Label(self.framedownloadwikislabelframe1, text="Mirror:")
        self.framedownloadwikislabelframe1label4.grid(row=1, column=2, sticky=E)
        self.framedownloadwikislabelframe1optionmenu4var = StringVar(self.framedownloadwikislabelframe1)
        self.framedownloadwikislabelframe1optionmenu4var.set("all")
        self.framedownloadwikislabelframe1optionmenu4 = OptionMenu(self.framedownloadwikislabelframe1, self.framedownloadwikislabelframe1optionmenu4var, self.framedownloadwikislabelframe1optionmenu4var.get(), "Google Code", "Internet Archive", "ScottDB")
        self.framedownloadwikislabelframe1optionmenu4.grid(row=1, column=3)
        #buttons
        self.framedownloadwikisbutton1 = Button(self.framedownloadwikis, text="Scan available dumps", command=lambda: thread.start_new_thread(self.loadAvailableDumps, ()), width=15)
        self.framedownloadwikisbutton1.grid(row=2, column=0)
        self.framedownloadwikisbutton4 = Button(self.framedownloadwikis, text="Apply filters", command=self.filterAvailableDumps, width=15)
        self.framedownloadwikisbutton4.grid(row=3, column=0)
        self.framedownloadwikisbutton3 = Button(self.framedownloadwikis, text="Download selection", command=lambda: thread.start_new_thread(self.downloadDump, ()), width=15, anchor=E)
        self.framedownloadwikisbutton3.grid(row=2, column=2)
        self.framedownloadwikisbutton2 = Button(self.framedownloadwikis, text="Clear list", command=self.deleteAvailableDumps, width=15)
        self.framedownloadwikisbutton2.grid(row=3, column=2)
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
        self.framepreprocesstreescrollbar.grid(row=1, column=3, sticky=W+E+N+S)
        framepreprocesscolumns = ('dump', 'wikifarm', 'size', 'date', 'status')
        self.framepreprocesstree = ttk.Treeview(self.framepreprocess, height=27, columns=framepreprocesscolumns, show='headings', yscrollcommand=self.framepreprocesstreescrollbar.set)
        self.framepreprocesstreescrollbar.config(command=self.framepreprocesstree.yview)
        self.framepreprocesstree.column('dump', width=460, minwidth=460, anchor='center')
        self.framepreprocesstree.heading('dump', text='Dump', command=lambda: self.treeSortColumn(tree='framepreprocesstree', column='dump', reverse=False))
        self.framepreprocesstree.column('wikifarm', width=100, minwidth=100, anchor='center')
        self.framepreprocesstree.heading('wikifarm', text='Wikifarm', command=lambda: self.treeSortColumn(tree='framepreprocesstree', column='wikifarm', reverse=False))
        self.framepreprocesstree.column('size', width=100, minwidth=100, anchor='center')
        self.framepreprocesstree.heading('size', text='Size', command=lambda: self.treeSortColumn(tree='framepreprocesstree', column='size', reverse=False))
        self.framepreprocesstree.column('date', width=100, minwidth=100, anchor='center')
        self.framepreprocesstree.heading('date', text='Date', command=lambda: self.treeSortColumn(tree='framepreprocesstree', column='date', reverse=False))
        self.framepreprocesstree.column('status', width=240, minwidth=240, anchor='center')
        self.framepreprocesstree.heading('status', text='Status', command=lambda: self.treeSortColumn(tree='framepreprocesstree', column='status', reverse=False))
        self.framepreprocesstree.grid(row=1, column=0, columnspan=3, sticky=W+E+N+S)
        #[self.framepreprocesstree.heading(column, text=column, command=lambda: self.treeSortColumn(column=column, reverse=False)) for column in columns]        
        #self.framepreprocesstree.bind("<Double-1>", (lambda: thread.start_new_thread(self.downloadDump, ())))
        self.framepreprocesstree.tag_configure('preprocessed', background='lightgreen')
        self.framepreprocesstree.tag_configure('nopreprocessed', background='white')
        #options
        self.framepreprocesslabelframe1 = LabelFrame(self.framepreprocess, text="Preprocess options")
        self.framepreprocesslabelframe1.grid(row=2, column=1, rowspan=2, pady=5)
        self.framepreprocesslabelframe1label1 = Label(self.framepreprocesslabelframe1, text="Revision limit:")
        self.framepreprocesslabelframe1label1.grid(row=0, column=0, sticky=E)
        self.framepreprocesslabelframe1entry1var = StringVar(self.framepreprocess)
        self.framepreprocesslabelframe1entry1var.set("None")
        self.framepreprocesslabelframe1entry1 = Entry(self.framepreprocesslabelframe1, textvariable=self.framepreprocesslabelframe1entry1var, width=10)
        self.framepreprocesslabelframe1entry1.grid(row=0, column=1)
        self.framepreprocesslabelframe1label2 = Label(self.framepreprocesslabelframe1, text="Page limit:")
        self.framepreprocesslabelframe1label2.grid(row=1, column=0, sticky=E)
        self.framepreprocesslabelframe1entry2var = StringVar(self.framepreprocess)
        self.framepreprocesslabelframe1entry2var.set("None")
        self.framepreprocesslabelframe1entry2 = Entry(self.framepreprocesslabelframe1, textvariable=self.framepreprocesslabelframe1entry2var, width=10)
        self.framepreprocesslabelframe1entry2.grid(row=1, column=1)
        #buttons
        self.framepreprocessbutton3 = Button(self.framepreprocess, text="Scan downloaded dumps", command=lambda: thread.start_new_thread(self.loadDownloadedDumps, ()), width=18)
        self.framepreprocessbutton3.grid(row=2, column=0)
        self.framepreprocessbutton3 = Button(self.framepreprocess, text="Preprocess selection", command=lambda: thread.start_new_thread(self.preprocessDump, ()), width=18)
        self.framepreprocessbutton3.grid(row=3, column=0)
        self.framepreprocessbutton3 = Button(self.framepreprocess, text="Load", command=lambda: thread.start_new_thread(self.activePreprocessedDump, ()), width=18)
        self.framepreprocessbutton3.grid(row=2, column=2)
        self.framepreprocessbutton2 = Button(self.framepreprocess, text="Clear list", command=self.deleteDownloadedDumps, width=18)
        self.framepreprocessbutton2.grid(row=3, column=2)
        #end preprocess tab
        
        #start analysis global tab
        self.frameanalysisgloballabel1 = Label(self.frameanalysisglobal, text="Choose an analysis:", width=15, anchor=W)
        self.frameanalysisgloballabel1.grid(row=0, column=0, sticky=W)
        self.frameanalysisglobaloptionmenu1var = StringVar(self.frameanalysisglobal)
        self.frameanalysisglobaloptionmenu1var.set("global-summary")
        self.frameanalysisglobaloptionmenu1 = OptionMenu(self.frameanalysisglobal, self.frameanalysisglobaloptionmenu1var, self.frameanalysisglobaloptionmenu1var.get(), "global-activity-yearly", "global-activity-monthly", "global-activity-dow", "global-activity-hourly", "global-activity-regs-vs-anons", "global-reverts-evolution", "global-reverted-words", "global-newpages", "global-newusers", "global-graph-user-messages", "global-graph-user-edits-network", "global-nlp-mostusedwords", )
        self.frameanalysisglobaloptionmenu1.grid(row=0, column=1, sticky=W)
        """
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
        """
        button1 = Button(self.frameanalysisglobal, text='Calculate', command=lambda: self.analysis(self.frameanalysisglobaloptionmenu1var.get()), width=10)
        button1.grid(row=0, column=2, sticky=W)
        #end analysis global tab
        
        #start analysis pages tab
        self.frameanalysispageslabel1 = Label(self.frameanalysispages, text="Choose a page and an analysis:", anchor='center', font=self.font)
        self.frameanalysispageslabel1.grid(row=0, column=0, columnspan=3, sticky=W)
        self.frameanalysispagestreescrollbar = Scrollbar(self.frameanalysispages)
        self.frameanalysispagestreescrollbar.grid(row=1, column=3, sticky=W+E+N+S)
        self.frameanalysispagescolumns = ('page name', 'first edit', 'last edit', 'age', 'edits')
        self.frameanalysispagestree = ttk.Treeview(self.frameanalysispages, height=27, columns=self.frameanalysispagescolumns, show='headings', yscrollcommand=self.frameanalysispagestreescrollbar.set)
        self.frameanalysispagestreescrollbar.config(command=self.frameanalysispagestree.yview)
        self.frameanalysispagestree.column('page name', width=370, minwidth=370, anchor='center')
        self.frameanalysispagestree.heading('page name', text='Page name', command=lambda: self.treeSortColumn(tree='frameanalysispagestree', column='page name', reverse=False))
        self.frameanalysispagestree.column('first edit', width=145, minwidth=145, anchor='center')
        self.frameanalysispagestree.heading('first edit', text='First edit', command=lambda: self.treeSortColumn(tree='frameanalysispagestree', column='first edit', reverse=False))
        self.frameanalysispagestree.column('last edit', width=145, minwidth=145, anchor='center')
        self.frameanalysispagestree.heading('last edit', text='Last edit', command=lambda: self.treeSortColumn(tree='frameanalysispagestree', column='last edit', reverse=False))
        self.frameanalysispagestree.column('age', width=100, minwidth=100, anchor='center')
        self.frameanalysispagestree.heading('age', text='Age in days', command=lambda: self.treeSortColumn(tree='frameanalysispagestree', column='age', reverse=False))
        self.frameanalysispagestree.column('edits', width=120, minwidth=120, anchor='center')
        self.frameanalysispagestree.heading('edits', text='Edits', command=lambda: self.treeSortColumn(tree='frameanalysispagestree', column='edits', reverse=False))
        self.frameanalysispagestree.grid(row=1, column=0, columnspan=3, sticky=W+E+N+S)
        #self.frameanalysispagestree.bind("<Double-1>", (lambda: thread.start_new_thread(self.downloadDump, ())))
        #end analysis pages tab
        
        #start analysis users tab
        self.frameanalysisuserslabel1 = Label(self.frameanalysisusers, text="Choose an user and an analysis:", anchor='center', font=self.font)
        self.frameanalysisuserslabel1.grid(row=0, column=0, columnspan=3, sticky=W)
        self.frameanalysisuserstreescrollbar = Scrollbar(self.frameanalysisusers)
        self.frameanalysisuserstreescrollbar.grid(row=1, column=3, sticky=W+E+N+S)
        frameanalysisuserscolumns = ('user name', 'first edit', 'last edit', 'age', 'edits')
        self.frameanalysisuserstree = ttk.Treeview(self.frameanalysisusers, height=27, columns=frameanalysisuserscolumns, show='headings', yscrollcommand=self.frameanalysisuserstreescrollbar.set)
        self.frameanalysisuserstreescrollbar.config(command=self.frameanalysisuserstree.yview)
        self.frameanalysisuserstree.column('user name', width=370, minwidth=370, anchor='center')
        self.frameanalysisuserstree.heading('user name', text='User name', command=lambda: self.treeSortColumn(tree='frameanalysisuserstree', column='user name', reverse=False))
        self.frameanalysisuserstree.column('first edit', width=145, minwidth=145, anchor='center')
        self.frameanalysisuserstree.heading('first edit', text='First edit', command=lambda: self.treeSortColumn(tree='frameanalysisuserstree', column='first edit', reverse=False))
        self.frameanalysisuserstree.column('last edit', width=145, minwidth=145, anchor='center')
        self.frameanalysisuserstree.heading('last edit', text='Last edit', command=lambda: self.treeSortColumn(tree='frameanalysisuserstree', column='last edit', reverse=False))
        self.frameanalysisuserstree.column('age', width=100, minwidth=100, anchor='center')
        self.frameanalysisuserstree.heading('age', text='Age in days', command=lambda: self.treeSortColumn(tree='frameanalysisuserstree', column='age', reverse=False))
        self.frameanalysisuserstree.column('edits', width=120, minwidth=120, anchor='center')
        self.frameanalysisuserstree.heading('edits', text='Edits', command=lambda: self.treeSortColumn(tree='frameanalysisuserstree', column='edits', reverse=False))
        self.frameanalysisuserstree.grid(row=1, column=0, columnspan=3, sticky=W+E+N+S)
        #self.frameanalysisuserstree.bind("<Double-1>", (lambda: thread.start_new_thread(self.downloadDump, ())))
        #end analysis users tab
        
        #start analysis samples tab
        #end analysis samples tab
    
    def filterAvailableDumps(self):
        self.clearAvailableDumps()
        self.showAvailableDumps()
        sizes = []
        downloadedsizes = []
        nodownloadedsizes = []
        for i in range(len(self.availabledumps)):
            if (self.framedownloadwikislabelframe1optionmenu1var.get() == 'all' and self.framedownloadwikislabelframe1optionmenu2var.get() == 'all' and self.framedownloadwikislabelframe1optionmenu3var.get() == 'all' and self.framedownloadwikislabelframe1optionmenu4var.get() == 'all'):
                sizes.append(self.availabledumps[i][2])
                if self.availabledumps[i][6]:
                    downloadedsizes.append(self.availabledumps[i][2])
                else:
                    nodownloadedsizes.append(self.availabledumps[i][2])
            elif (self.framedownloadwikislabelframe1optionmenu1var.get() != 'all' and not self.framedownloadwikislabelframe1optionmenu1var.get() == self.availabledumps[i][1]) or \
                (self.framedownloadwikislabelframe1optionmenu2var.get() != 'all' and not self.framedownloadwikislabelframe1optionmenu2var.get() in self.availabledumps[i][2]) or \
                (self.framedownloadwikislabelframe1optionmenu3var.get() != 'all' and not self.framedownloadwikislabelframe1optionmenu3var.get() in self.availabledumps[i][3]) or \
                (self.framedownloadwikislabelframe1optionmenu4var.get() != 'all' and not self.framedownloadwikislabelframe1optionmenu4var.get() in self.availabledumps[i][4]):
                self.framedownloadwikistree.detach(str(i)) #hide this item
                sizes.append(self.availabledumps[i][2])
                if self.availabledumps[i][6]:
                    downloadedsizes.append(self.availabledumps[i][2])
                else:
                    nodownloadedsizes.append(self.availabledumps[i][2])
        #self.label25var.set("Available dumps: %d (%.1f MB)" % (len(sizes), self.sumSizes(sizes)))
        #self.label26var.set("Downloaded: %d (%.1f MB)" % (len(downloadedsizes), self.sumSizes(downloadedsizes)))
        #self.label27var.set("Not downloaded: %d (%.1f MB)" % (len(nodownloadedsizes), self.sumSizes(nodownloadedsizes)))
    
    def treeSortColumn(self, tree=None, column=None, reverse=False):
        if tree == 'frameanalysispagestree': #lo hago asi pq los heading() se generan uno detrás de otro y no puedo pasar el tree como parámetro antes de q terminen todos
            tree = self.frameanalysispagestree
        elif tree == 'frameanalysisuserstree':
            tree = self.frameanalysisuserstree
        elif tree == 'framepreprocesstree':
            tree = self.framepreprocesstree
        elif tree == 'framedownloadwikistree':
            tree = self.framedownloadwikistree
        isDigit = True
        for k in tree.get_children(''):
            if not tree.set(k, column).isdigit():
                isDigit = False
                break
        isBytes = False
        if not isDigit:
            pass
        l = []
        if isDigit:
            l = [(int(tree.set(k, column)), k) for k in tree.get_children('')]
        else:
            l = [(tree.set(k, column), k) for k in tree.get_children('')]
        l.sort(reverse=reverse)

        for index, (val, k) in enumerate(l):
            tree.move(k, '', index)

        tree.heading(column, command=lambda: self.treeSortColumn(tree=tree, column=column, reverse=not reverse))
    
    def createCursor(self):
        if self.activedb:
            conn = sqlite3.connect(self.activedb)
            cursor = conn.cursor()
            return cursor
        else:
            print "Error, no cursor"
            sys.exit()
    
    def loadPages(self):
        for i in range(len(self.pages)):
            self.frameanalysispagestree.delete(str(i))
        self.pages = []
        cursor = self.createCursor()
        result = cursor.execute("SELECT page_title, page_creation_timestamp, page_last_timestamp, page_editcount FROM page WHERE 1 ORDER BY page_title")
        pages = [[page_title, page_creation_timestamp, page_last_timestamp, (wecore.str2date(page_last_timestamp)-wecore.str2date(page_creation_timestamp)).days, page_editcount] for page_title, page_creation_timestamp, page_last_timestamp, page_editcount in result]
        c = 0
        for page_title, firstedit, lastedit, age, edits in pages:
            self.frameanalysispagestree.insert('', 'end', str(c), text=page_title, values=(page_title, firstedit, lastedit, age, edits))
            self.pages.append(page_title)
            c += 1
        return
    
    def loadUsers(self):
        for i in range(len(self.users)):
            self.frameanalysisuserstree.delete(str(i))
        self.users = []
        cursor = self.createCursor()
        result = cursor.execute("SELECT user_name, user_editcount, user_first_timestamp, user_last_timestamp FROM user WHERE 1 ORDER BY user_name")
        users = [[user_name, user_first_timestamp, user_last_timestamp, (wecore.str2date(user_last_timestamp)-wecore.str2date(user_first_timestamp)).days, user_editcount] for user_name, user_editcount, user_first_timestamp, user_last_timestamp in result]
        c = 0
        for user_name, firstedit, lastedit, age, edits in users:
            self.frameanalysisuserstree.insert('', 'end', str(c), text=user_name, values=(user_name, firstedit, lastedit, age, edits))
            self.users.append(user_name)
            c += 1
    
    def activePreprocessedDump(self):
        if self.block:
            self.blocked()
            return
        else:
            self.block = True
        
        items = self.framepreprocesstree.selection()
        if len(items) == 1:
            filepath = self.preprocesspath and self.preprocesspath + '/' + self.downloadeddumps[int(items[0])][0] + '.db' or self.downloadeddumps[int(items[0])][0] + '.db'
            if os.path.exists(filepath):
                self.activedb = filepath
                self.wiki = self.downloadeddumps[int(items[0])][0].split('.')[0]
                self.notebookanalysislabel1.config(text='You are analysing "%s".\n' % (self.activedb))
                self.loadUsers()
                self.loadPages()
                self.msg(msg="Loaded %s succesfull. Now, you can analyse." % (self.activedb), level="info")
            else:
                self.msg(msg="That preprocessed dump doesn't exist.", level="error")
        else:
            self.msg(msg="You only can load a preprocessed dump a time.", level="error")
            self.block = False
            return
        
        self.block = False
    
    def analysis(self, analysis):
        if not self.activedb:
            self.msg(msg="You must load a preprocessed dump first", level="error")
            return
        
        if self.block:
            self.blocked()
            return
        else:
            self.block = True
        
        cursor = self.createCursor()
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
                elif analysis == 'global-activity-regs-vs-anons':
                    weactivity.regsvsanons(cursor=cursor)
            elif analysis == 'global-nlp-mostusedwords':
                import wenlp
                wenlp.mostUsedWords(cursor=cursor)
            elif analysis == 'global-reverts-evolution':
                import wereverts
                wereverts.revertsEvolution(cursor=cursor, title='Global reverts evolution @ %s' % (self.wiki))
            elif analysis == 'global-reverted-words':
                import wereverts
                wereverts.revertedWords(cursor=cursor, title='Global reverted words @ %s' % (self.wiki))
            elif analysis == 'global-newpages':
                import wenewpages
                wenewpages.newpagesEvolution(cursor=cursor, title='Global newpages evolution @ %s' % (self.wiki))
            elif analysis == 'global-newusers':
                import wenewusers
                wenewusers.newusersEvolution(cursor=cursor, title='Global newusers evolution @ %s' % (self.wiki))
            elif analysis == 'global-graph-user-messages':
                import wegraph
                wegraph.graphUserMessages(self=self, cursor=cursor)
            elif analysis == 'global-graph-user-edits-network':
                import wegraph
                wegraph.graphUserEditsNetwork(self=self, cursor=cursor)
        
        self.block = False
        pylab.show()
    
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
        self.filterAvailableDumps()
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
            ['Wikimedia', 'http://dumps.wikimedia.org/backup-index.html', ur'(?P<size>)<a href="(?P<filename>[^>]+)">[^>]+</a>: <span class=\'done\'>Dump complete</span></li>']
        ]
        c = 0
        for mirror, url, regexp in self.urls:
            print 'Loading data from', mirror, url
            self.msg(msg='Please wait... Loading data from %s %s' % (mirror, url))
            f = urllib.urlopen(url)
            m = re.compile(regexp).finditer(f.read())
            for i in m:
                filename = i.group('filename')
                wikifarm = self.getWikifarmFromFilename(filename)
                if mirror == 'Wikimedia':
                    filename = '%s-pages-meta-history.xml.7z' % (re.sub('/', '-', filename))
                    wikifarm = wikifarms['wikimedia']
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
        self.filterAvailableDumps()
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
                    revlimit = None
                    pagelimit = None
                    if self.framepreprocesslabelframe1entry1var.get().isdigit():
                        revlimit = int(self.framepreprocesslabelframe1entry1var.get())
                    if self.framepreprocesslabelframe1entry2var.get().isdigit():
                        pagelimit = int(self.framepreprocesslabelframe1entry2var.get())
                    import weparser
                    weparser.parseMediaWikiXMLDump(self=self, dumpfilename=dumppath, dbfilename=filepath, revlimit=revlimit, pagelimit=pagelimit)
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

