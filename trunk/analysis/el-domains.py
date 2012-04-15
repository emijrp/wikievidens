#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (C) 2012 WikiEvidens
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

import bz2
import re
import sys

domains = {
    ur"(?im)https?://prensahistorica\.mcu\.es": None, 
    ur"(?im)https?://bibliotecadigital\.carm\.es": None,
    ur"(?im)https?://([^/]+\.)?bibliotecavirtualdeandalucia\.es": None,
    ur"(?im)https?://([^/]+\.)?bnc\.cat": None,
}
for k, v in domains.items():
    domains[k] = re.compile(k)

ee_r = re.compile(ur"(?im)(Enlaces?\s*externos?|Bibliograf[íi]a)")

def convert(text):
    text = re.sub(ur"&quot;", '"', text)
    text = re.sub(ur"&lt;", "<", text)
    text = re.sub(ur"&gt;", ">", text)
    return text

def getEEBiblio(text):
    ee = ""
    splits = text.split('==')
    c = 0
    while c < len(splits)-1:
        if re.search(ee_r, splits[c]):
            ee = splits[c+1]
        c += 1
    return ee    

def main():
    #todo: filtrar namespaces
    
    title_r = re.compile(ur"<title>([^<]+)</title>")
    text_start_r = re.compile(ur"<text xml:space=\"preserve\">")
    text_end_r = re.compile(ur"</text>")
    ref_r = re.compile(ur"(?im)(\<ref[^<]*?\</ref\>)")
    http_r = re.compile(ur"(?im)https?://")
    f = bz2.BZ2File(sys.argv[1], 'r')
    c = 0
    title = ""
    text = ""
    text_lock = False
    for l in f:
        if re.findall(title_r, l): #get title
            if title: #print previous page
                text = convert(text)
                search = [len(re.findall(compiled, text)) for regexp, compiled in domains.items()]
                sumsearch = sum(search)
                if sumsearch > 0:
                    #print text
                    print '-'*72
                    print '%07d) %s [%d bytes] http://es.wikipedia.org/wiki/%s' % (c, title, len(text), re.sub(' ', '_', title))
                    print '         [%d URLs matched / %d URLs in this page]' % (sumsearch, len(re.findall(http_r, text)))
                    for regexp, compiled in domains.items():
                        sumsearch2 = len(re.findall(compiled, text))
                        if sumsearch2:
                            print '         %s | <ref> (%d), == EE/Biblio == (%d)' % (regexp, sum([len(re.findall(compiled, ref)) for ref in re.findall(ref_r, text)]), len(re.findall(compiled, getEEBiblio(text)))) 
            #reset for the new page
            title = re.findall(title_r, l)[0]
            text = ""
            c += 1
        elif re.findall(text_start_r, l): #gets text start
            if re.findall(text_end_r, l):
                text = l.split('<text xml:space="preserve">')[1].split("</text>")[0]
            else:
                text = l.split('<text xml:space="preserve">')[1] #reset text with this first line
                text_lock = True
        elif re.findall(text_end_r, l): #ends text fetching
            text += l.split('</text>')[0]
            text_lock = False
        else: #saves more text
            if text_lock:
                text += l

    f.close()

if __name__ == "__main__":
    main()
