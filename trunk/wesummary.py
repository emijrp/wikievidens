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
import sqlite3
import tkMessageBox

#TODO: que meta los numeros en un diccionario?

#ideas para el resumen: total links, media ediciones/pag, total size (last page edits), total visits, total files, user with most edits, 

def totalEdits(cursor=None, page_title=None, user_name=None):
    if page_title:
        result = cursor.execute("SELECT COUNT(rev_id) AS count FROM revision WHERE rev_is_ipedit=? AND rev_title=?", (0, page_title))
    elif user_name:
        result = cursor.execute("SELECT COUNT(rev_id) AS count FROM revision WHERE rev_is_ipedit=? AND rev_user_text=?", (0, user_name))
    else:
        result = cursor.execute("SELECT COUNT(rev_id) AS count FROM revision WHERE rev_is_ipedit=?", (0,))
    edits_by_reg = 0
    for row in result:
        edits_by_reg = row[0]
    
    if page_title:
        result = cursor.execute("SELECT COUNT(rev_id) AS count FROM revision WHERE rev_is_ipedit=? AND rev_title=?", (1, page_title))
    elif user_name:
        result = cursor.execute("SELECT COUNT(rev_id) AS count FROM revision WHERE rev_is_ipedit=? AND rev_user_text=?", (1, user_name))
    else:
        result = cursor.execute("SELECT COUNT(rev_id) AS count FROM revision WHERE rev_is_ipedit=?", (1,))
    edits_by_unreg = 0
    for row in result:
        edits_by_unreg = row[0]
    return edits_by_reg, edits_by_unreg

def totalPages(cursor=None, page_title=None, user_name=None):
    if page_title:
        #fix, return 1 ?
        result = cursor.execute("SELECT COUNT(DISTINCT rev_page) AS count FROM page WHERE rev_title=?", (page_title,))
    elif user_name:
        result = cursor.execute("SELECT COUNT(DISTINCT rev_page) AS count FROM revision WHERE rev_user_text=?", (user_name,))
    else:
        result = cursor.execute("SELECT COUNT(DISTINCT rev_page) AS count FROM revision WHERE 1")
    for row in result:
        return row[0]
    return 0

def totalUsers(cursor=None, page_title=None, user_name=None):
    if page_title:
        result = cursor.execute("SELECT COUNT(DISTINCT rev_user_text) AS count FROM revision WHERE rev_is_ipedit=? AND rev_title=?", (0, page_title))
    elif user_name:
        result = cursor.execute("SELECT COUNT(DISTINCT rev_user_text) AS count FROM revision WHERE rev_is_ipedit=? AND rev_user_text=?", (0, user_name))
    else:
        result = cursor.execute("SELECT COUNT(DISTINCT rev_user_text) AS count FROM revision WHERE rev_is_ipedit=?", (0,))
    registered_users = 0
    for row in result:
        registered_users = row[0]
        
    if page_title:
        result = cursor.execute("SELECT COUNT(DISTINCT rev_user_text) AS count FROM revision WHERE rev_is_ipedit=? AND rev_title=?", (1, page_title))
    elif user_name:
        result = cursor.execute("SELECT COUNT(DISTINCT rev_user_text) AS count FROM revision WHERE rev_is_ipedit=? AND rev_user_text=?", (1, user_name))
    else:
        result = cursor.execute("SELECT COUNT(DISTINCT rev_user_text) AS count FROM revision WHERE rev_is_ipedit=?", (1,))
    unregistered_users = 0
    for row in result:
        unregistered_users = row[0]
    return registered_users, unregistered_users

def firstEdit(cursor=None, page_title=None, user_name=None):
    if page_title:
        result = cursor.execute("SELECT rev_timestamp, rev_user_text FROM revision WHERE rev_title=? ORDER BY rev_timestamp ASC LIMIT 1", (page_title,))
    elif user_name:
        result = cursor.execute("SELECT rev_timestamp, rev_user_text FROM revision WHERE rev_user_text=? ORDER BY rev_timestamp ASC LIMIT 1", (user_name,))
    else:
        result = cursor.execute("SELECT rev_timestamp, rev_user_text FROM revision WHERE 1 ORDER BY rev_timestamp ASC LIMIT 1")
    for row in result:
        return row[0], row[1]
    return '', ''

def lastEdit(cursor=None, page_title=None, user_name=None):
    if page_title:
        result = cursor.execute("SELECT rev_timestamp, rev_user_text FROM revision WHERE rev_title=? ORDER BY rev_timestamp DESC LIMIT 1", (page_title,))
    elif user_name:
        result = cursor.execute("SELECT rev_timestamp, rev_user_text FROM revision WHERE rev_user_text=? ORDER BY rev_timestamp DESC LIMIT 1", (user_name,))
    else:
        result = cursor.execute("SELECT rev_timestamp, rev_user_text FROM revision WHERE 1 ORDER BY rev_timestamp DESC LIMIT 1")
    for row in result:
        return row[0], row[1]
    return '', ''

def lifespan(firstedit='', lastedit=''):
    if firstedit and lastedit:
        return (datetime.datetime.strptime(lastedit, '%Y-%m-%d %H:%M:%S') - datetime.datetime.strptime(firstedit, '%Y-%m-%d %H:%M:%S')).days
    return 'Unknown'

def editSummaryUsage(cursor=None, page_title=None, user_name=None):
    if page_title:
        result = cursor.execute("SELECT COUNT(rev_comment) FROM revision WHERE rev_comment <> '' AND rev_is_ipedit=? AND rev_title=?", (0, page_title))
    elif user_name:
        result = cursor.execute("SELECT COUNT(rev_comment) FROM revision WHERE rev_comment <> '' AND rev_is_ipedit=? AND rev_user_text=?", (0, user_name))
    else:
        result = cursor.execute("SELECT COUNT(rev_comment) FROM revision WHERE rev_comment <> '' AND rev_is_ipedit=?", (0,))
    edits_by_reg = 0
    for row in result:
        edits_by_reg = row[0]
    
    if page_title:
        result = cursor.execute("SELECT COUNT(rev_comment) FROM revision WHERE rev_comment <> '' AND rev_is_ipedit=? AND rev_title=?", (1, page_title))
    elif user_name:
        result = cursor.execute("SELECT COUNT(rev_comment) FROM revision WHERE rev_comment <> '' AND rev_is_ipedit=? AND rev_user_text=?", (1, user_name))
    else:
        result = cursor.execute("SELECT COUNT(rev_comment) FROM revision WHERE rev_comment <> '' AND rev_is_ipedit=?", (1,))
    edits_by_unreg = 0
    for row in result:
        edits_by_unreg = row[0]
    
    return edits_by_reg, edits_by_unreg

def totalLinks(cursor=None, page_title=None, user_name=None):
    #fix recorrer la última revisión de cada página
    if page_title:
        result = cursor.execute("SELECT SUM(page_internal_links), SUM(page_external_links), SUM(page_interwikis), SUM(page_templates) FROM page WHERE page_title=?", (page_title,))
    elif user_name:
        return 0, 0, 0, 0
    else:
        result = cursor.execute("SELECT SUM(page_internal_links), SUM(page_external_links), SUM(page_interwikis), SUM(page_templates) FROM page WHERE 1")
    for row in result:
        return row[0], row[1], row[2], row[3]
    return 0, 0, 0, 0

def totalSections(cursor=None, page_title=None, user_name=None):
    #fix recorrer la última revisión de cada página
    if page_title:
        result = cursor.execute("SELECT SUM(page_sections) FROM page WHERE page_title=?", (page_title,))
    elif user_name:
        return 0
    else:
        result = cursor.execute("SELECT SUM(page_sections) FROM page WHERE 1")
    for row in result:
        return row[0]
    return 0

def summary(cursor=None, page_title=None, user_name=None):
    #sugerencias: páginas por nm (y separando redirects de no redirects), log events? deletes, page moves
    
    pages = totalPages(cursor=cursor, page_title=page_title, user_name=user_name)
    edits_by_reg, edits_by_unreg = totalEdits(cursor=cursor, page_title=page_title, user_name=user_name)
    registered_users, unregistered_users = totalUsers(cursor=cursor, page_title=page_title, user_name=user_name)
    firstedit, fuser = firstEdit(cursor=cursor, page_title=page_title, user_name=user_name)
    lastedit, luser = lastEdit(cursor=cursor, page_title=page_title, user_name=user_name)
    age = lifespan(firstedit=firstedit, lastedit=lastedit)
    summaries_by_reg, summaries_by_unreg = editSummaryUsage(cursor=cursor, page_title=page_title, user_name=user_name)
    links, external_links, interwikis, template_transclusions = totalLinks(cursor=cursor, page_title=page_title, user_name=user_name)
    sections = totalSections(cursor=cursor, page_title=page_title, user_name=user_name)
    
    output = ''
    if page_title:
        output += '%s\nPage "%s" summary\n%s\n\n' % ('-'*60, page_title, '-'*60)
    elif user_name:
        output += '%s\nUser "%s" summary\n%s\n\n' % ('-'*60, user_name, '-'*60)
    else:
        output += '%s\nGlobal summary\n%s\n\n' % ('-'*60, '-'*60)
    output += 'Pages      = %d\n' % (pages)
    output += 'Revisions  = %d (total)\n' % (edits_by_reg+edits_by_unreg)
    output += '           = %d (by registered users)\n' % (edits_by_reg)
    output += '           = %d (by unregistered users)\n' % (edits_by_unreg)
    output += 'Revs/pag   = %.2f\n' % (float(edits_by_reg+edits_by_unreg)/pages)
    output += 'Users      = %d (registered users)\n' % (registered_users)
    output += '           = %d (unregistered users)\n' % (unregistered_users)
    output += 'Revs/user  = %.2f (by registered users)\n' % (float(edits_by_reg)/registered_users)
    output += '           = %.2f (by unregistered users)\n' % (edits_by_unreg and float(edits_by_unreg)/unregistered_users or 0)
    output += 'First edit = %s (User:%s)\n' % (firstedit, fuser)
    output += 'Last edit  = %s (User:%s)\n' % (lastedit, luser)
    output += 'Age        = %d days (%.2f years)\n' % (age, age/365.0)
    output += 'Links      = %d (internal links)\n' % (links)
    output += '             %d (external links)\n' % (external_links)
    output += '             %d (interwiki links)\n' % (interwikis)
    output += '             %d (template transclusions)\n' % (template_transclusions)
    output += 'Sections   = %d\n' % (sections)
    
    output += '\n\n%s\nOther\n%s\n\n' % ('-'*60, '-'*60)
    output += 'Edit summary usage  = %d (%.2f%%) by registered users\n' % (summaries_by_reg, edits_by_reg and summaries_by_reg/(edits_by_reg/100.0) or 0)
    output += '                    = %d (%.2f%%) by unregistered users\n' % (summaries_by_unreg, edits_by_unreg and summaries_by_unreg/(edits_by_unreg/100.0) or 0)
    output += '                    = %d (%.2f%%) by both\n' % (summaries_by_reg+summaries_by_unreg, (summaries_by_reg+summaries_by_unreg)/((edits_by_reg+edits_by_unreg)/100.0))
    
    print output
    #tkMessageBox.showinfo(title="Summary", message=output)

    frame = Tk()
    frame.title('Summary')
    width, height = 440, 500
    # calculate position x, y
    x = (frame.winfo_screenwidth()/2) - (width/2) 
    y = (frame.winfo_screenheight()/2) - (height/2)
    frame.geometry('%dx%d+%d+%d' % (width, height, x, y))
    frame.minsize(width=width, height=height)
    frame.maxsize(width=width, height=height)
    
    scrollbar = Scrollbar(frame)
    scrollbar.grid(row=0, column=1, sticky=W+E+N+S)
    #fix: con un label sería mejor?
    text = Text(frame, wrap=WORD, width=60, height=33, yscrollcommand=scrollbar.set)
    text.insert(INSERT, output)
    text.config(state=NORMAL) #si lo pongo en solo lectura (DISABLED), no deja copiar/pegar con ctrl-c
    text.grid(row=0, column=0)
    #scrollbar.config(command=text.yview)

def editsByRegisteredUsers(cursor=None, page_title=None):
    #fix esto debería estar en una tabla summary ya?
    if page_title:
        result = cursor.execute("SELECT COUNT(rev_id) AS count FROM revision WHERE rev_is_ipedit=? AND rev_title=?", (0, page_title))
    else:
        result = cursor.execute("SELECT COUNT(rev_id) AS count FROM revision WHERE rev_is_ipedit=?", (0,))
    for row in result:
        return row[0]
    return 0

def editsByAnonymousUsers(cursor=None, page_title=None):
    #fix esto debería estar en una tabla summary ya?
    if page_title:
        result = cursor.execute("SELECT COUNT(rev_id) AS count FROM revision WHERE rev_is_ipedit=? AND rev_title=?", (1, page_title))
    else:
        result = cursor.execute("SELECT COUNT(rev_id) AS count FROM revision WHERE rev_is_ipedit=?", (1,))
    for row in result:
        return row[0]
    return 0
