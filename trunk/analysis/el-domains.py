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

"""
404 errors
  Unable to find http://www.europeana.eu/portal/record/90101/B9C0A4DA0B3A368FA7997054BE1199821FC01549.html
                 http://www.europeana.eu/portal/record/03903/B4A820896C4F5484FFB52435D760DBA411559778.html
  Llevan a portada http://www.europeana.eu/ark:/12148/bpt6k109477z
                   http://www.europeana.eu/ark:/12148/bpt6k1096855.r=
  han expirado http://www.bibliotecavirtualdeandalucia.es/catalogo/consulta/resultados_busqueda.cmd?id=1691&posicion=7&forma=ficha
"""

repositories = {
    u"Europeana": { 'regexp': ur"(?im)https?://([^/\s]+\.)?europeana\.eu/[^\|\]\s]+/record/" }, 
    u"Biblioteca Virtual de Prensa Histórica": { 'regexp': ur"(?im)https?://prensahistorica\.mcu\.es" }, 
    u"Biblioteca Digital de la Región de Murcia": { 'regexp': ur"(?im)https?://bibliotecadigital\.carm\.es" }, 
    u"BV Andalucía": { 'regexp': ur"(?im)https?://([^/\s]+\.)?bibliotecavirtualdeandalucia\.es" }, 
    u"BD Cataluña": { 'regexp': ur"(?im)https?://([^/\s]+\.)?bnc\.cat" }, 
    u"Pares. Portal Archivos": { 'regexp': ur"(?im)https?://([^/\s]+\.)?pares\.mcu\.es[^\|\]\s]+(nid|txt_id_desc_ud)\=" }, 
}
for k, v in repositories.items():
    repositories[k]['compiled'] = re.compile(k)
    repositories[k]['totallinks'] = 0
    repositories[k]['totalarticles'] = 0

ee_r = re.compile(ur"(?im)(Enlaces?\s*externos?|Bibliograf[íi]a)")

def convert(text):
    text = text.replace('&gt;', '>')
    text = text.replace('&lt;', '<')
    text = text.replace('&quot;', '"')
    text = text.replace('&amp;', '&')
    return text

def getEEBiblio(text):
    ee = ""
    splits = text.split('==')
    c = 0
    while c < len(splits)-1:
        if re.search(ee_r, splits[c]):
            ee = splits[c+1]
            break
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
                #print text
                search = [len(re.findall(props['compiled'], text)) for repository, props in repositories.items()]
                sumsearch = sum(search)
                if sumsearch > 0:
                    #print text
                    print '-'*72
                    print '%07d) %s [%d bytes] http://es.wikipedia.org/wiki/%s' % (c, title, len(text), re.sub(' ', '_', title))
                    print '         Categories: %s' % (' | '.join(re.findall(ur"(?im)\[\[\s*(?:Category|Categoría)\s*:\s*([^\|\n\]]+)\s*[\|\]]", text)))
                    print '         [%d URLs matched / %d URLs in this page]' % (sumsearch, len(re.findall(http_r, text)))
                    for repository, props in repositories.items():
                        sumsearch2 = len(re.findall(props['compiled'], text))
                        if sumsearch2 > 0:
                            #updating stats for this repository
                            repositories[repository]['totallinks'] += sumsearch2
                            repositories[repository]['totalarticles'] += 1
                            #details
                            inrefs = sum([len(re.findall(props['compiled'], ref)) for ref in re.findall(ref_r, text)])
                            inee = len(re.findall(props['compiled'], getEEBiblio(text)))
                            other = sumsearch2 - (inrefs + inee)
                            print '         %s: <ref> (%d), == EE/Biblio == (%d), Other (%d)' % (repository, inrefs, inee, other)
            #reset for the new page
            title = re.findall(title_r, l)[0]
            text = ""
            c += 1
            if c > 100000:
                break
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
    
    print '== Ranking =='
    ranking = [[props['totallinks'], props['totalarticles'], repository] for repository, props in repositories.items()]
    ranking.sort(reverse=True)
    for totallinks, totalarticles, repository in ranking:
        print '%s [%d links in %d articles]' % (repository, totallinks, totalarticles)

if __name__ == "__main__":
    main()
