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

import calendar
import sqlite3
import time
import xmlreader
import sys
import numpy
import pylab
import thread

#cada script .py es un analisis (usuarios ordenados por ediciones por ejemplo) y permiten ser llamados desde otro modulo (mediante llamada a función) o desde consola y con salida por pantalla, csv, svg ,png eps si corresponde, etc

def activity(cursor=None, range='', entity='', title='', subtitle='', color='', xlabel='', timesplit=''):
    if not cursor:
        print "ERROR, NO CURSOR"
        return
    
    t1=time.time()
    
    fig = pylab.figure()
    
    subfig = fig.add_subplot(1,1,1)
    subfig.set_title(title)
    result = []
    if range == 'global':
        result = cursor.execute("SELECT STRFTIME(?, rev_timestamp) AS timesplit, COUNT(*) AS count FROM revision WHERE 1 GROUP BY timesplit ORDER BY timesplit ASC", (timesplit, ))
    elif range == 'user':
        result = cursor.execute("SELECT STRFTIME(?, rev_timestamp) AS timesplit, COUNT(*) AS count FROM revision WHERE rev_user_text=? GROUP BY timesplit ORDER BY timesplit ASC", (timesplit, entity))
    elif range == 'page':
        result = cursor.execute("SELECT STRFTIME(?, rev_timestamp) AS timesplit, COUNT(*) AS count FROM revision WHERE rev_title=? GROUP BY timesplit ORDER BY timesplit ASC", (timesplit, entity))
    
    x, y = [], []
    for timesplit, count in result:
        print timesplit, count
        x.append(int(timesplit))
        y.append(int(count))
    
    rects = subfig.bar(numpy.arange(len(x)), y, color=color, align='center')
    subfig.legend()
    subfig.set_title(subtitle)
    subfig.set_xlabel(xlabel)
    subfig.set_xticks(numpy.arange(len(x)))
    subfig.set_xticklabels([str(i) for i in x])
    subfig.set_ylabel('Edits')
    
    maxheight = max([rect.get_height() for rect in rects])
    for rect in rects:
        height = rect.get_height()
        subfig.text(rect.get_x()+rect.get_width()/2., height+(maxheight/50), str(height), ha='center', va='bottom')
    
    print title, 'generated in', time.time()-t1, 'secs'

def activityyearly(cursor=None, range='', entity='', title=''):
    activity(cursor=cursor, range=range, entity=entity, title=title, subtitle='Activity by year', color='#88aa33', xlabel='Year', timesplit='%Y')

def activitymonthly(cursor=None, range='', entity='', title=''):
    activity(cursor=cursor, range=range, entity=entity, title=title, subtitle='Activity by month', color='#aa3388', xlabel='Month', timesplit='%m')

def activitydow(cursor=None, range='', entity='', title=''):
    activity(cursor=cursor, range=range, entity=entity, title=title, subtitle='Activity by day of week', color='#3388aa', xlabel='Day of week', timesplit='%w')

def activityhourly(cursor=None, range='', entity='', title=''):
    activity(cursor=cursor, range=range, entity=entity, title=title, subtitle='Activity by hour', color='#1177bb', xlabel='Hour', timesplit='%H')

def activityall(cursor=None, range='', entity='', title=''):
    activityyearly(cursor=cursor, range=range, entity=entity, title=title)
    activitymonthly(cursor=cursor, range=range, entity=entity, title=title)
    activitydow(cursor=cursor, range=range, entity=entity, title=title)
    activityhourly(cursor=cursor, range=range, entity=entity, title=title)

def regsvsanons(cursor=None):
    result = cursor.execute("SELECT STRFTIME('%Y-%m', rev_timestamp) AS timesplit, COUNT(*) AS count FROM revision WHERE 1 GROUP BY timesplit ORDER BY timesplit ASC")
    revs = {}
    for timesplit, count in result:
        if not revs.has_key(timesplit):
            revs[timesplit] = {'alledits': 0, 'anonsedits': 0}
        revs[timesplit]['alledits'] = count
    
    result = cursor.execute("SELECT STRFTIME('%Y-%m', rev_timestamp) AS timesplit, COUNT(*) AS count FROM revision WHERE rev_is_ipedit=1 GROUP BY timesplit ORDER BY timesplit ASC")
    for timesplit, count in result:
        if not revs.has_key(timesplit):
            revs[timesplit] = {'alledits': 0, 'anonsedits': 0}
        revs[timesplit]['anonsedits'] = count
    
    l = [[k, v['alledits'], v['alledits']-v['anonsedits'], v['anonsedits']] for k, v in revs.items()]
    l.sort()
    print '\n'.join(['%s, %s, %s, %s' % (k, v1, v2, v3) for k, v1, v2, v3 in l])
    
    fig = pylab.figure()
    subfig = fig.add_subplot(1,1,1)
    subfig.set_title('Edits percent by user class evolution')
    ind = numpy.arange(len(l))
    anonedits = [v3/(v1/100.0) for k, v1, v2, v3 in l]
    regedits = [v2/(v1/100.0) for k, v1, v2, v3 in l]
    alledits = [100]*len(l)
    pylab.plot(ind, alledits)
    pylab.plot(ind, regedits)
    pylab.fill_between(ind, alledits, regedits, color='cyan') 
    pylab.fill_between(ind, regedits, 0, color='magenta') 
    #p1 = subfig.plot(numpy.arange(len(l)), alledits, color='g', align='center')
    #p2 = subfig.plot(numpy.arange(len(l)), anonedits, bottom=alledits, color='y', align='center')
    subfig.legend()
    #subfig.set_title(subtitle)
    subfig.set_xlabel('Date (YYYY-MM)')
    subfig.set_xticks(numpy.arange(len(l)))
    subfig.set_xticklabels([k for k, v1, v2, v3 in l])
    subfig.set_ylabel('Percent edits')
    labels = subfig.get_xticklabels()
    pylab.setp(labels, rotation=30, fontsize=10)
