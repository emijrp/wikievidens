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

import re
import sqlite3
import zlib

import nltk

def mostUsedWords(cursor=None, ignoreStopWords=True):
    result = cursor.execute("SELECT page_id, page_text FROM page WHERE 1")
    
    words_r = re.compile(ur"(\w+(?:'\w+)?)")
    words = {}
    for page_id, page_text_blob in result:
        page_text = zlib.decompress(page_text_blob)
        for word in re.findall(words_r, page_text.lower()):
            if ignoreStopWords and word in nltk.corpus.stopwords.words('english'):
                continue
            words[word] = words.get(word, 0) + 1
    
    l = [[times, word] for word, times in words.items()]
    l.sort()
    
    print '\n'.join(['%s, %s' % (word, times) for times, word in l[-100:]])
