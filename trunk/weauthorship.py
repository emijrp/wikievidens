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

import datetime
import random
import sqlite3
import tkMessageBox

#documentation about Text widget http://infohost.nmt.edu/tcc/help/pubs/tkinter/text.html

def authorship(cursor=None, page_title=None):
    result = cursor.execute("SELECT rev_user_text, rev_text FROM revision WHERE rev_title=?", (page_title,))
    revs = []
    for rev_user_text, rev_text in result:
        revs.append([rev_user_text, rev_text])
    
    output = revs[-1][1]
    
    
    frame = Tk()
    frame.title('Authorship')
    width, height = 900, 600
    # calculate position x, y
    x = (frame.winfo_screenwidth()/2) - (width/2) 
    y = (frame.winfo_screenheight()/2) - (height/2)
    frame.geometry('%dx%d+%d+%d' % (width, height, x, y))
    #frame.minsize(width=width, height=height)
    #frame.maxsize(width=width, height=height)
    
    scrollbar = Scrollbar(frame)
    scrollbar.grid(row=0, column=1, sticky=W+E+N+S)
    #fix: con un label sería mejor?
    text = Text(frame, wrap=WORD, width=120, height=36, yscrollcommand=scrollbar.set)
    text.insert(INSERT, output)
    text.config(state=NORMAL) #si lo pongo en solo lectura (DISABLED), no deja copiar/pegar con ctrl-c
    text.grid(row=0, column=0)
    
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
                    print user, start, end, c, part[:50]
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
