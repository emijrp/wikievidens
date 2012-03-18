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

from Tkinter import *
import ttk

import datetime
import random
import sqlite3
import tkMessageBox

#documentation about Text widget http://infohost.nmt.edu/tcc/help/pubs/tkinter/text.html

def authorship(cursor=None, page_title=None):
    #fix improve colors using different ones
    
    result = cursor.execute("SELECT rev_user_text, rev_text FROM revision WHERE rev_title=?", (page_title,))
    revs = []
    for rev_user_text, rev_text in result:
        revs.append([rev_user_text, rev_text])
    
    output = revs[-1][1]
    
    
    frame = Tk()
    frame.title('Authorship')
    width, height = 855, 700
    # calculate position x, y
    x = (frame.winfo_screenwidth()/2) - (width/2) 
    y = (frame.winfo_screenheight()/2) - (height/2)
    frame.geometry('%dx%d+%d+%d' % (width, height, x, y))
    frame.minsize(width=width, height=height)
    frame.maxsize(width=width, height=height)
    
    label1 = Label(frame, text='\nAuthorship of "%s" last revision:' % (page_title))
    label1.grid(row=0, column=0, columnspan=2, sticky=W)
    scrollbar = Scrollbar(frame)
    scrollbar.grid(row=1, column=1, sticky=W+E+N+S)
    #fix: con un label sería mejor?
    text = Text(frame, wrap=WORD, width=120, height=32, yscrollcommand=scrollbar.set)
    text.insert(INSERT, output)
    text.config(state=NORMAL) #si lo pongo en solo lectura (DISABLED), no deja copiar/pegar con ctrl-c
    text.grid(row=1, column=0)
    
    #authorship detector
    parts = output.splitlines()
    c = 0
    users = []
    for part in parts:
        c += 1
        part=part.strip()
        if part:
            for user, rev in revs:
                if part in rev:
                    start = text.search(part, 1.0)
                    end = text.search(part, 1.0).split('.')[0]+'.'+str(len(part))
                    print user, start, end, part[:50]
                    text.tag_add(user, start, end)
                    if user not in users:
                        users.append(user)
                    break
    
    #tags
    colors = {}
    for user in users:
        background = '#%s' % (random.randint(222,999))
        colors[user] = background
        text.tag_config(user, background=background)
    print colors.items()

    #legend, treeview
    label2 = Label(frame, text="\nLegend:")
    label2.grid(row=2, column=0, columnspan=2, sticky=W)
    treescrollbar = Scrollbar(frame)
    treescrollbar.grid(row=3, column=1, sticky=W+E+N+S)
    treecolumns = ('user name', 'chars')
    tree = ttk.Treeview(frame, height=6, columns=treecolumns, show='headings', yscrollcommand=treescrollbar.set)
    treescrollbar.config(command=tree.yview)
    tree.column('user name', width=460, minwidth=460, anchor='center')
    tree.heading('user name', text='User name', )
    tree.column('chars', width=100, minwidth=100, anchor='center')
    tree.heading('chars', text='Chars', )
    tree.grid(row=3, column=0, columnspan=1, sticky=W+E+N+S)
    c = 0
    for user in users:
        tree.insert('', 'end', str(c), text=user, values=(user, colors[user]))
        c += 1
