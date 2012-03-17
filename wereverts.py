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
import re
import sqlite3
import tkMessageBox

import wecore

#fix
#mirar como usa las fechas aquí http://matplotlib.sourceforge.net/examples/api/date_demo.html
#nube de puntos http://matplotlib.sourceforge.net/examples/api/unicode_minus.html
#dateranges http://matplotlib.sourceforge.net/examples/pylab_examples/date_demo_rrule.html

def revertsEvolution(cursor=None, title=''):
    #checks one revision with all the previous revision in the same page
    result = cursor.execute("SELECT rev_page, rev_id, rev_timestamp, rev_text_md5 FROM revision WHERE 1 ORDER BY rev_page, rev_timestamp ASC")
    page = []
    reverts = {}
    for row in result:
        rev_page = row[0]
        rev_id = row[1]
        rev_timestamp = row[2]
        rev_text_md5 = row[3]
        revision = [rev_page, rev_id, rev_timestamp, rev_text_md5]
        
        if page:
            if rev_page == page[0][0]: #new revision for this page?
                page.append(revision)
            else: #previous page finished, analyse
                c = 0
                for temprev in page:
                    if temprev[3] in [temprev2[3] for temprev2 in page[:c]]: #is a revert of a previous rev in this page?
                        temprevdate = wecore.str2date(temprev[2]).strftime('%Y-%m-%d')
                        if reverts.has_key(temprevdate):
                            reverts[temprevdate] += 1
                        else:
                            reverts[temprevdate] = 1
                    c += 1
                
                page.append(revision) #reset
        else:
            page.append(revision)
    
    #fix, no analiza la última página, habría que repetir el código del for temprev in page, llevar mejor a una función core y llamar?
    
    reverts_list = [[x, y] for x, y in reverts.items()]
    reverts_list.sort()
    
    startdate = reverts_list[0][0]
    enddate = reverts_list[-1:][0][0]
    delta = datetime.timedelta(days=1)
    reverts_list = [] #reset, adding all days between startdate and enddate
    d = startdate
    while d < enddate:
        if reverts.has_key(d):
            reverts_list.append([d, reverts[d]])
        else:
            reverts_list.append([d, 0])
        d += delta


    import pylab
    from matplotlib.dates import DateFormatter, rrulewrapper, RRuleLocator, drange

    loc = pylab.MonthLocator(bymonth=(1,6))
    formatter = DateFormatter('%Y-%m-%d')
    dates = drange(startdate, enddate, delta)

    fig = pylab.figure()
    ax = fig.add_subplot(1,1,1)
    ax.set_ylabel('Reverts')
    ax.set_xlabel('Date (YYYY-MM-DD)')
    print '#'*100
    print len(dates)
    print dates
    print '#'*100
    print len(pylab.array([y for x, y in reverts_list]))
    print pylab.array([y for x, y in reverts_list])
    print '#'*100
    pylab.plot_date(dates, pylab.array([y for x, y in reverts_list]), 'o', color='red')
    ax.xaxis.set_major_locator(loc)
    ax.xaxis.set_major_formatter(formatter)
    ax.set_title(title)
    ax.grid(True)
    ax.set_yscale('log')
    labels = ax.get_xticklabels()
    pylab.setp(labels, rotation=30, fontsize=10)

def revertedWords(cursor=None, title='', onlyAnon=True):
    #compare revision triplets A, B, C, if md5(A) == md5(C) then B has been reverted
    result = cursor.execute("SELECT rev_page, rev_id, rev_timestamp, rev_text, rev_text_md5, rev_is_ipedit FROM revision WHERE 1 ORDER BY rev_page, rev_timestamp ASC")
    page = []
    revertedwords = {}
    w_r = re.compile(ur'\w+')
    for row in result:
        rev_page = row[0]
        rev_id = row[1]
        rev_timestamp = row[2]
        rev_text = row[3]
        rev_text_md5 = row[4]
        rev_is_ipedit = int(row[5])
        revision = [rev_page, rev_id, rev_timestamp, rev_text, rev_text_md5, rev_is_ipedit]
        
        if page:
            if rev_page == page[0][0]: #new revision for this page?
                page.append(revision)
            else: #previous page finished, analyse
                c = 0
                for temprev in page:
                    if c>0 and c<len(page)-1 and page[c-1][4] == page[c+1][4]: #prev and next revs are equal? then this is a reverted revision
                        if onlyAnon and rev_is_ipedit == 1 or not onlyAnon:
                            for word in list(set(re.findall(w_r, page[c][3].lower())) - set(re.findall(w_r, page[c-1][3].lower()))):
                                revertedwords[word] = revertedwords.get(word, 0) + 1
                    c += 1
                page = [revision] #reset
        else:
            page.append(revision)
    
    l = [[times, word] for word, times in revertedwords.items()]
    l.sort()
    
    print '\n'.join(['%s, %s' % (times, word) for times, word in l[-100:]])
