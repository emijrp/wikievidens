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
  a veces sin le das a F5 el error de sesión desaparece
"""

repositories = {
    #EU
    u"Europeana": { 'regexp': ur"(?im)(https?://(?:[^/\s]+\.)?europeana\.eu/[^\|\]\s\<]+/record/[^\|\]\s\<]*?)(?:[\|\]\s\<])" }, 
    u"Portal Europeo de Archivos": { 'regexp': ur"(?im)(https?://(?:[^/\s]+\.)?archivesportaleurope\.eu[^\|\]\s\<]*?)(?:[\|\]\s\<])" }, 
    u"The European Library": { 'regexp': ur"(?im)(https?://(?:[^/\s]+\.)?theeuropeanlibrary\.org[^\|\]\s\<]*?)(?:[\|\]\s\<])" }, 
    
    #ES
    u"Biblioteca Digital Hispánica": { 'regexp': ur"(?im)(https?://(?:[^/\s]+\.)?bdh\.bne\.es[^\|\]\s\<]*?)(?:[\|\]\s\<])" }, 
    u"Biblioteca Virtual de Prensa Histórica": { 'regexp': ur"(?im)(https?://(?:[^/\s]+\.)?prensahistorica\.mcu\.es[^\|\]\s\<]*?)(?:[\|\]\s\<])" }, 
    u"Biblioteca Virtual del Patrimonio Bibliográfico": { 'regexp': ur"(?im)(https?://(?:[^/\s]+\.)?bvpb\.mcu\.es[^\|\]\s\<]*?)(?:[\|\]\s\<])" }, 
    u"CERES": { 'regexp': ur"(?im)(https?://(?:[^/\s]+\.)?ceres\.mcu\.es[^\|\]\s\<]*?)(?:[\|\]\s\<])" }, 
    u"Pares. Portal Archivos": { 'regexp': ur"(?im)(https?://(?:[^/\s]+\.)?pares\.mcu\.es[^\|\]\s\<]+(?:nid|txt_id_desc_ud)\=[^\|\]\s\<]*?)(?:[\|\]\s\<])" },
    u"Fototeca Patrimonio Histórico": { 'regexp': ur"(?im)(https?://(?:[^/\s]+\.)?(?:mcu\.es/fototeca_patrimonio/|ipce\.mcu\.es/documentacion/fototeca/)[^\|\]\s\<]*?)(?:[\|\]\s\<])" },
    u"Recolector Hispana": { 'regexp': ur"(?im)(https?://(?:[^/\s]+\.)?roai\.mcu\.es[^\|\]\s\<]*?)(?:[\|\]\s\<])" },
    
    #REG
    u"Biblioteca Digital de la Región de Murcia": { 'regexp': ur"(?im)(https?://(?:[^/\s]+\.)?bibliotecadigital\.carm\.es[^\|\]\s\<]*?)(?:[\|\]\s\<])" },
    u"BV Andalucía": { 'regexp': ur"(?im)(https?://(?:[^/\s]+\.)?bibliotecavirtualdeandalucia\.es[^\|\]\s\<]*?)(?:[\|\]\s\<])" }, 
    u"Biblioteca Virtual de Aragón": { 'regexp': ur"(?im)(https?://(?:[^/\s]+\.)?bibliotecavirtual\.aragon\.es[^\|\]\s\<]*?)(?:[\|\]\s\<])" }, 
    u"Fondo Histórico Cortes de Aragón": { 'regexp': ur"(?im)(https?://(?:[^/\s]+\.)?cortesaragon\.es[^\|\]\s\<]*?)(?:[\|\]\s\<])" }, 
    u"Biblioteca Digital de Castilla y León": { 'regexp': ur"(?im)(https?://(?:[^/\s]+\.)?bibliotecadigital\.jcyl\.es[^\|\]\s\<]*?)(?:[\|\]\s\<])" }, 
    u"Archivo de la imagen de Castilla-La Mancha": { 'regexp': ur"(?im)(https?://(?:[^/\s]+\.)?clip\.jccm\.es/archivo_de_la_imagen[^\|\]\s\<]*?)(?:[\|\]\s\<])" }, 
    u"Biblioteca Digital de Castilla-La Mancha": { 'regexp': ur"(?im)(https?://(?:[^/\s]+\.)?clip\.jccm\.es/bidicam/[^\|\]\s\<]*?)(?:[\|\]\s\<])" }, 
    u"Biblioteca Digital de la Comunidad Madrid": { 'regexp': ur"(?im)(https?://(?:[^/\s]+\.)?bibliotecavirtualmadrid\.org[^\|\]\s\<]*?)(?:[\|\]\s\<])" }, 
    u"Memoria Digital Catalunya": { 'regexp': ur"(?im)(https?://(?:[^/\s]+\.)?mdc\.cbuc\.cat[^\|\]\s\<]*?)(?:[\|\]\s\<])" }, 
    u"ARCA Arxiu de Revistes Catalanes Antigues": { 'regexp': ur"(?im)(https?://(?:[^/\s]+\.)?mdc2\.cbuc\.cat[^\|\]\s\<]*?)(?:[\|\]\s\<])" }, 
    u"BD Valenciana": { 'regexp': ur"(?im)(https?://(?:[^/\s]+\.)?bv2\.gva\.es[^\|\]\s\<]*?)(?:[\|\]\s\<])" }, 
    u"BINADI Biblioteca Digital de Navarra": { 'regexp': ur"(?im)(https?://(?:[^/\s]+\.)?administracionelectronica\.navarra\.es/binadi/[^\|\]\s\<]*?)(?:[\|\]\s\<])" }, 
    u"BD Vasca": { 'regexp': ur"(?im)(https?://(?:[^/\s]+\.)?liburuklik\.euskadi\.net[^\|\]\s\<]*?)(?:[\|\]\s\<])" }, 
    u"Memoria Digital Vasca": { 'regexp': ur"(?im)(https?://(?:[^/\s]+\.)?memoriadigitalvasca\.es[^\|\]\s\<]*?)(?:[\|\]\s\<])" }, 
    u"BD Galicia": { 'regexp': ur"(?im)(https?://(?:[^/\s]+\.)?csbg\.org/bibliotecadixital/[^\|\]\s\<]*?)(?:[\|\]\s\<])" }, 
    u"Memoria Digital de Canarias": { 'regexp': ur"(?im)(https?://(?:[^/\s]+\.)?mdc\.ulpgc\.es/[^\|\]\s\<]*?)(?:[\|\]\s\<])" }, 
    u"Proyecto Carmesí Región de Murcia": { 'regexp': ur"(?im)(https?://(?:[^/\s]+\.)?regmurcia\.com/[^\|\]\s\<]+&sit\=c,373[^\|\]\s\<]*?)(?:[\|\]\s\<])" }, 
    u"Biblioteca Virtual de La Rioja": { 'regexp': ur"(?im)(https?://(?:[^/\s]+\.)?bibliotecavirtual\.larioja\.org[^\|\]\s\<]*?)(?:[\|\]\s\<])" }, 
    u"Arxiu Nacional Catalunya. ANC": { 'regexp': ur"(?im)(https?://(?:[^/\s]+\.)?cultura\.gencat\.net/anc/[^\|\]\s\<]*?)(?:[\|\]\s\<])" }, 
    
    #LOC
    u"Biblioteca Virtual Diputación de Zaragoza": { 'regexp': ur"(?im)(https?://(?:[^/\s]+\.)?bivizar\.es[^\|\]\s\<]*?)(?:[\|\]\s\<])" },
    u"Biblioteca Digital Ayuntamiento Murcia": { 'regexp': ur"(?im)(https?://(?:[^/\s]+\.)?murcia\.es/bibliotecadigitaldemurcia/[^\|\]\s\<]*?)(?:[\|\]\s\<])" },
    u"Biblioteca Digital Leonesa": { 'regexp': ur"(?im)(https?://(?:[^/\s]+\.)?saber\.es[^\|\]\s\<]*?)(?:[\|\]\s\<])" },
    u"Memoria de Madrid": { 'regexp': ur"(?im)(https?://(?:[^/\s]+\.)?memoriademadrid\.es/[^\|\]\s\<]*?)(?:[\|\]\s\<])" }, 
    u"Biblioteca Digital de Bizkaia": { 'regexp': ur"(?im)(https?://(?:[^/\s]+\.)?bibliotecaforal\.bizkaia\.net[^\|\]\s\<]*?)(?:[\|\]\s\<])" }, 
    
    #UNI
    u"Fondo Antiguo Universidad Zaragoza": { 'regexp': ur"(?im)(https?://(?:[^/\s]+\.)?zaguan\.unizar\.es/collection/[^\|\]\s\<]*?)(?:[\|\]\s\<])" }, 
    u"Digitum. Fondo Antiguo Universidad de Murcia": { 'regexp': ur"(?im)(https?://(?:[^/\s]+\.)?digitum\.um\.es/xmlui/handle/[^\|\]\s\<]*?)(?:[\|\]\s\<])" }, 
    u"Somin. Fondo Histórico Universidad de Valencia": { 'regexp': ur"(?im)(https?://(?:[^/\s]+\.)?roderic\.uv\.es[^\|\]\s\<]*?)(?:[\|\]\s\<])" }, 
    u"Fondo Antiguo Universidad de Granada": { 'regexp': ur"(?im)(https?://(?:[^/\s]+\.)?digibug\.ugr\.es/handle/[^\|\]\s\<]*?)(?:[\|\]\s\<])" }, 
    u"Colecciones patrimoniales Universidad Salamanca (Gredos)": { 'regexp': ur"(?im)(https?://(?:[^/\s]+\.)?gredos\.usal\.es/jspui/handle/[^\|\]\s\<]*?)(?:[\|\]\s\<])" }, 
    
    #INS
    u"Biblioteca Virtual de Derecho Aragones": { 'regexp': ur"(?im)(https?://(?:[^/\s]+\.)?derechoaragones\.es[^\|\]\s\<]*?)(?:[\|\]\s\<])" }, 
    u"Portal teatro Siglo de Oro": { 'regexp': ur"(?im)(https?://(?:[^/\s]+\.)?teatrosiglodeoro\.bne\.es[^\|\]\s\<]*?)(?:[\|\]\s\<])" }, 
    u"Biblioteca Virtual Miguel de Cervantes": { 'regexp': ur"(?im)(https?://(?:[^/\s]+\.)?cervantesvirtual\.com[^\|\]\s\<]*?)(?:[\|\]\s\<])" }, 
    u"Fondo antiguo Universidad Sevilla": { 'regexp': ur"(?im)(https?://(?:[^/\s]+\.)?fondosdigitales\.us\.es/fondos/[^\|\]\s\<]*?)(?:[\|\]\s\<])" }, 
    u"Colecciones digitales Univ. Barcelona": { 'regexp': ur"(?im)(https?://(?:[^/\s]+\.)?bib\.ub\.edu/recursos-informacio/colleccions/[^\|\]\s\<]*?)(?:[\|\]\s\<])" }, 
    u"Biblioteca Digital Complutense": { 'regexp': ur"(?im)(https?://(?:[^/\s]+\.)?alfama\.sim\.ucm\.es[^\|\]\s\<]*?)(?:[\|\]\s\<])" }, 
    u"BD Ateneo Madrid": { 'regexp': ur"(?im)(https?://(?:[^/\s]+\.)?ateneodemadrid\.com/biblioteca_digital/[^\|\]\s\<]*?)(?:[\|\]\s\<])" }, 
    u"BD Jardín Botánico": { 'regexp': ur"(?im)(https?://(?:[^/\s]+\.)?bibdigital\.rjb\.csic\.es[^\|\]\s\<]*?)(?:[\|\]\s\<])" }, 
    u"Archivo Ateneo Madrid": { 'regexp': ur"(?im)(https?://(?:[^/\s]+\.)?archivo\.ateneodemadrid\.es[^\|\]\s\<]*?)(?:[\|\]\s\<])" }, 
    u"Biblioteca Virtual Larramendi": { 'regexp': ur"(?im)(https?://(?:[^/\s]+\.)?arramendi\.es/i18n/[^\|\]\s\<]*?)(?:[\|\]\s\<])" }, 
    u"Fondo fotográfico siglo XX Universidad de Navarra": { 'regexp': ur"(?im)(https?://(?:[^/\s]+\.)?coleccionfff\.unav\.es/bvunav[^\|\]\s\<]*?)(?:[\|\]\s\<])" }, 
    u"Cartoteca Digital i Col·leccions d'imatges del Institut Cartografic de Catalunya": { 'regexp': ur"(?im)(https?://(?:[^/\s]+\.)?cartotecadigital\.icc\.cat[^\|\]\s\<]*?)(?:[\|\]\s\<])" }, 
    u"Almirall, portal del pensamiento del Segle XIX": { 'regexp': ur"(?im)(https?://(?:[^/\s]+\.)?194\.224\.194\.201\:9080/Almirall/[^\|\]\s\<]*?)(?:[\|\]\s\<])" }, 
    u"Disposit Digital UAB": { 'regexp': ur"(?im)(https?://(?:[^/\s]+\.)?ddd\.uab\.cat[^\|\]\s\<]*?)(?:[\|\]\s\<])" }, 
    
    #TEST
    u"Archivo ABC": { 'regexp': ur"(?im)(https?://(?:[^/\s]+\.)?hemeroteca\.abc\.es[^\|\]\s\<]*?)(?:[\|\]\s\<])" }, 
    u"Hemeroteca La Vanguardia": { 'regexp': ur"(?im)(https?://(?:[^/\s]+\.)?hemeroteca\.lavanguardia\.es[^\|\]\s\<]*?)(?:[\|\]\s\<])" },
    u"LOC": { 'regexp': ur"(?im)(https?://(?:[^/\s]+\.)?loc\.gov[^\|\]\s\<]*?)(?:[\|\]\s\<])" },
    
}

for repository, props in repositories.items():
    repositories[repository]['compiled'] = re.compile(props['regexp'])
    repositories[repository]['totallinks'] = 0
    repositories[repository]['totalarticles'] = 0

ee_r = re.compile(ur"(?im)(Enlaces?\s*externos?|Bibliograf[íi]a|Enllaços\s*externs)")
http_r = re.compile(ur"(?im)(https?://)")
redirect_r = re.compile(ur"(?im)^\s*#\s*(REDIRECT|REDIRECCI[ÓO]N)\s*\[\[")

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
            ee += splits[c+1] # += merge biblio and EE if both are available
        c += 1
    return ee

def main():    
    title_r = re.compile(ur"<title>([^<]+)</title>")
    text_start_r = re.compile(ur"<text xml:space=\"preserve\">")
    text_end_r = re.compile(ur"</text>")
    ref_r = re.compile(ur"(?im)(\<ref[^<]*?\</ref\>)")
    http_r = re.compile(ur"(?im)https?://")
    f = bz2.BZ2File(sys.argv[1], 'r')
    c = 0
    cpageswithrepolinks = 0
    clinks = 0
    crepolinks = 0
    cinrefs = 0
    cinee = 0
    cother = 0
    title = ""
    text = ""
    text_lock = False
    for l in f:
        if re.findall(title_r, l): #get title
            if title: #print previous page
                title = unicode(title, 'utf-8')
                text = convert(unicode(text, 'utf-8'))
                #skip other namespaces
                if title.startswith(u'Categoría:') or \
                   title.startswith(u'Categoria:') or \
                   title.startswith(u'Plantilla:') or \
                   title.startswith(u'Archivo:') or \
                   title.startswith(u'Fitxer:') or \
                   title.startswith(u'Wikipedia:') or \
                   title.startswith(u'Viquipèdia:') or \
                   title.startswith(u'Portal:') or \
                   title.startswith(u'Wikiproyecto:') or \
                   title.startswith(u'Viquiprojecte:') or \
                   title.startswith(u'MediaWiki:') or \
                   title.startswith(u'WP:') or \
                   title.startswith(u'PR:') or \
                   title.startswith(u'Ayuda:') or \
                   title.startswith(u'Ajuda:'):
                    pass
                elif not re.search(redirect_r, text): #no redirects
                    clinks += len(re.findall(http_r, text))
                    search = [len(re.findall(props['compiled'], text)) for repository, props in repositories.items()]
                    sumsearch = sum(search)
                    if sumsearch > 0:
                        cpageswithrepolinks += 1
                        crepolinks += sumsearch
                        #print text
                        output  = u'-'*72
                        output += u'\n%07d) [[%s]] (%d bytes) http://es.wikipedia.org/wiki/%s' % (c, title, len(text), re.sub(' ', '_', title))
                        output += u'\n         Categories: %s' % (' | '.join(re.findall(ur"(?im)\[\[\s*(?:Category|Categoría)\s*:\s*([^\|\]]+)\s*[\|\]]", text)))
                        output += u'\n         [%d URLs matched / %d URLs in this page]' % (sumsearch, len(re.findall(http_r, text)))
                        print output.encode('utf-8')
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
                                cinrefs += inrefs
                                cinee += inee
                                cother += other
                                output  = u'\n         %s: <ref> (%d), == EE/Biblio == (%d), Other (%d)' % (repository, inrefs, inee, other)
                                output += u'\n             %s' % ('\n             '.join(re.findall(props['compiled'], text)))
                                print output.encode('utf-8')
                    c += 1
                    #if c >= 1000:
                    #    break
            #reset for the new page
            title = re.findall(title_r, l)[0]
            text = ""
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
    
    print u'\n== Ranking =='
    ranking = [[props['totallinks'], props['totalarticles'], repository] for repository, props in repositories.items()]
    ranking.sort(reverse=True)
    for totallinks, totalarticles, repository in ranking:
        output = u'%s [%d links in %d articles]' % (repository, totallinks, totalarticles)
        print output.encode('utf-8')
    print u"\nTotal articles analysed: %d. Total articles with links to repositories: %d (%.2f%%).\nTotal http(s) links: %d. Total http(s) links to repositories: %d (%.2f%%).\nRepository links by location: <ref> (%d, %.2f%%), == EE/Biblio == (%d, %.2f%%), Other (%d, %.2f%%)" % (c, cpageswithrepolinks, cpageswithrepolinks/(c/100.0), clinks, crepolinks, crepolinks/(clinks/100.0), cinrefs, cinrefs/((cinrefs+cinee+cother)/100.0), cinee, cinee/((cinrefs+cinee+cother)/100.0), cother, cother/((cinrefs+cinee+cother)/100.0))

if __name__ == "__main__":
    main()
