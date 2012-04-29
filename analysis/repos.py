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

import gzip
import random
import re
import time
import sys

repositories = {
    #EU
    u"Europeana": { 'regexp': ur"(?im)(https?://(?:[^/\s]+\.)?europeana\.eu/[^\|\]\s\<]+/record/|https?://(?:[^/\s]+\.)?europeanaregia\.eu)" }, 
    u"Portal Europeo de Archivos": { 'regexp': ur"(?im)(https?://(?:[^/\s]+\.)?archivesportaleurope\.eu)" }, 
    u"The European Library": { 'regexp': ur"(?im)(https?://(?:[^/\s]+\.)?theeuropeanlibrary\.org)" }, 
    
    #ES
    u"Biblioteca Digital Hispánica y Hemeroteca Histórica BNE": { 'regexp': ur"(?im)(https?://(?:[^/\s]+\.)?(?:bdh|bibliotecadigitalhispanica|hemerotecadigital)\.bne\.es)" }, 
    u"Biblioteca Virtual de Prensa Histórica": { 'regexp': ur"(?im)(https?://(?:[^/\s]+\.)?prensahistorica\.mcu\.es)" }, 
    u"Biblioteca Virtual del Patrimonio Bibliográfico": { 'regexp': ur"(?im)(https?://(?:[^/\s]+\.)?bvpb\.mcu\.es)" }, 
    u"CERES. Red Digital de Colecciones de Museos de España": { 'regexp': ur"(?im)(https?://(?:[^/\s]+\.)?ceres\.mcu\.es)" }, 
    u"Pares. Portal Archivos": { 'regexp': ur"(?im)(https?://(?:[^/\s]+\.)?pares\.mcu\.es[^\|\]\s\<]+(?:nid|txt_id_desc_ud)\=)" },
    u"Fototeca Patrimonio Histórico": { 'regexp': ur"(?im)(https?://(?:[^/\s]+\.)?(?:mcu\.es/fototeca_patrimonio/|ipce\.mcu\.es/documentacion/fototeca/))" },
    u"Recolector Hispana": { 'regexp': ur"(?im)(https?://(?:[^/\s]+\.)?roai\.mcu\.es)" },
    
    #REG
    u"Biblioteca Digital de la Región de Murcia": { 'regexp': ur"(?im)(https?://(?:[^/\s]+\.)?bibliotecadigital\.carm\.es)" },
    u"Biblioteca Virtual de Andalucía": { 'regexp': ur"(?im)(https?://(?:[^/\s]+\.)?bibliotecavirtualdeandalucia\.es)" }, 
    u"Biblioteca Virtual de Aragón": { 'regexp': ur"(?im)(https?://(?:[^/\s]+\.)?bibliotecavirtual\.aragon\.es)" }, 
    u"Fondo Histórico Cortes de Aragón": { 'regexp': ur"(?im)(https?://(?:[^/\s]+\.)?cortesaragon\.es)" }, 
    u"Biblioteca Digital de Castilla y León": { 'regexp': ur"(?im)(https?://(?:[^/\s]+\.)?bibliotecadigital\.jcyl\.es)" }, 
    u"Archivo de la imagen de Castilla-La Mancha": { 'regexp': ur"(?im)(https?://(?:[^/\s]+\.)?clip\.jccm\.es/archivo_de_la_imagen)" }, 
    u"Biblioteca Digital de Castilla-La Mancha": { 'regexp': ur"(?im)(https?://(?:[^/\s]+\.)?clip\.jccm\.es/bidicam/)" }, 
    u"Biblioteca Digital de la Comunidad Madrid": { 'regexp': ur"(?im)(https?://(?:[^/\s]+\.)?bibliotecavirtualmadrid\.org)" }, 
    u"Memoria Digital Catalunya": { 'regexp': ur"(?im)(https?://(?:[^/\s]+\.)?mdc\.cbuc\.cat)" }, 
    u"ARCA. Arxiu de Revistes Catalanes Antigues": { 'regexp': ur"(?im)(https?://(?:[^/\s]+\.)?mdc2\.cbuc\.cat)" }, 
    u"BiValdi. Biblioteca Digital Valenciana": { 'regexp': ur"(?im)(https?://(?:[^/\s]+\.)?bv2\.gva\.es)" }, 
    u"BINADI. Biblioteca Digital de Navarra": { 'regexp': ur"(?im)(https?://(?:[^/\s]+\.)?(?:administracionelectronica\.navarra\.es/binadi/|navarra\.es/appsext/bnd/))" }, 
    u"Biblioteca Digital Vasca": { 'regexp': ur"(?im)(https?://(?:[^/\s]+\.)?liburuklik\.euskadi\.net)" }, 
    u"Memoria Digital Vasca": { 'regexp': ur"(?im)(https?://(?:[^/\s]+\.)?memoriadigitalvasca\.es)" }, 
    u"Galiciana. Biblioteca Digital de Galicia": { 'regexp': ur"(?im)(https?://(?:[^/\s]+\.)?galiciana\.bibliotecadegalicia\.xunta\.es)" }, 
    u"Biblioteca Dixital de Galicia (Cidade de Cultura Galega)": { 'regexp': ur"(?im)(https?://(?:[^/\s]+\.)?(?:csbg\.org/bibliotecadixital/|csbg\.org/prensagalega|cmg\.xunta\.es/visor/prensa/|cmg\.xunta\.es/mediateca/hemeroteca/|bvg\.centromultimedia\.net|cmg\.xunta\.es/mediateca/cartografia/))" }, 
    u"Memoria Digital de Canarias": { 'regexp': ur"(?im)(https?://(?:[^/\s]+\.)?mdc\.ulpgc\.es)" }, 
    u"Proyecto Carmesí Región de Murcia": { 'regexp': ur"(?im)(https?://(?:[^/\s]+\.)?regmurcia\.com/[^\|\]\s\<]+&sit\=c,373)" }, 
    u"Biblioteca Virtual de Asturias": { 'regexp': ur"(?im)(https?://(?:[^/\s]+\.)?bibliotecavirtual\.asturias\.es)" }, 
    u"Biblioteca Virtual de La Rioja": { 'regexp': ur"(?im)(https?://(?:[^/\s]+\.)?bibliotecavirtual\.larioja\.org)" }, 
    u"ANC. Arxiu Nacional Catalunya": { 'regexp': ur"(?im)(https?://(?:[^/\s]+\.)?cultura\.gencat\.net/anc/)" }, 
    u"Documentos y Archivos de Aragón": { 'regexp': ur"(?im)(https?://(?:[^/\s]+\.)?sipca\.es/dara/)" }, 
    
    #LOC
    u"Biblioteca Virtual Diputación de Zaragoza": { 'regexp': ur"(?im)(https?://(?:[^/\s]+\.)?bivizar\.es)" },
    u"Biblioteca Digital Ayuntamiento Murcia": { 'regexp': ur"(?im)(https?://(?:[^/\s]+\.)?murcia\.es/bibliotecadigitaldemurcia/)" },
    u"Biblioteca Digital Leonesa": { 'regexp': ur"(?im)(https?://(?:[^/\s]+\.)?saber\.es)" },
    u"Memoria de Madrid": { 'regexp': ur"(?im)(https?://(?:[^/\s]+\.)?memoriademadrid\.es)" }, 
    u"Biblioteca Digital de Bizkaia": { 'regexp': ur"(?im)(https?://(?:[^/\s]+\.)?bibliotecaforal\.bizkaia\.net)" }, 
    
    #UNI
    u"Fondo Antiguo Universidad Zaragoza": { 'regexp': ur"(?im)(https?://(?:[^/\s]+\.)?zaguan\.unizar\.es)" }, 
    u"Digitum. Fondo Antiguo Universidad de Murcia": { 'regexp': ur"(?im)(https?://(?:[^/\s]+\.)?(?:digitum\.um\.es|hdl\.handle\.net/10201/))" }, 
    u"Somni. Fondo Histórico Universidad de Valencia": { 'regexp': ur"(?im)(https?://(?:[^/\s]+\.)?(?:roderic\.uv\.es|hdl\.handle\.net/10550/)" }, 
    u"Fondo Antiguo Universidad de Granada": { 'regexp': ur"(?im)(https?://(?:[^/\s]+\.)?(?:digibug\.ugr\.es|hdl\.handle\.net/10481/))" }, 
    u"Gredos. Colecciones patrimoniales Universidad Salamanca": { 'regexp': ur"(?im)(https?://(?:[^/\s]+\.)?(?:gredos\.usal\.es|hdl\.handle\.net/10366/))" }, 
    
    
    
    
    
    
    
    
    #INS
    u"Biblioteca Virtual de Derecho Aragones": { 'regexp': ur"(?im)(https?://(?:[^/\s]+\.)?derechoaragones\.es)" }, 
    u"Portal teatro Siglo de Oro": { 'regexp': ur"(?im)(https?://(?:[^/\s]+\.)?teatrosiglodeoro\.bne\.es)" }, 
    u"Biblioteca Virtual Miguel de Cervantes": { 'regexp': ur"(?im)(https?://(?:[^/\s]+\.)?cervantesvirtual\.com)" }, 
    u"Fondo antiguo Universidad Sevilla": { 'regexp': ur"(?im)(https?://(?:[^/\s]+\.)?fondosdigitales\.us\.es/fondos/)" }, 
    u"Colecciones digitales Univ. Barcelona": { 'regexp': ur"(?im)(https?://(?:[^/\s]+\.)?bib\.ub\.edu/recursos-informacio/colleccions/)" }, 
    u"Biblioteca Digital Complutense": { 'regexp': ur"(?im)(https?://(?:[^/\s]+\.)?alfama\.sim\.ucm\.es)" }, 
    u"BD Ateneo Madrid": { 'regexp': ur"(?im)(https?://(?:[^/\s]+\.)?ateneodemadrid\.com/biblioteca_digital/)" }, 
    u"BD Jardín Botánico": { 'regexp': ur"(?im)(https?://(?:[^/\s]+\.)?bibdigital\.rjb\.csic\.es)" }, 
    u"Archivo Ateneo Madrid": { 'regexp': ur"(?im)(https?://(?:[^/\s]+\.)?archivo\.ateneodemadrid\.es)" }, 
    u"Biblioteca Virtual Larramendi": { 'regexp': ur"(?im)(https?://(?:[^/\s]+\.)?arramendi\.es/i18n/)" }, 
    u"Fondo fotográfico siglo XX Universidad de Navarra": { 'regexp': ur"(?im)(https?://(?:[^/\s]+\.)?coleccionfff\.unav\.es/bvunav)" }, 
    u"Cartoteca Digital i Col·leccions d'imatges del Institut Cartografic de Catalunya": { 'regexp': ur"(?im)(https?://(?:[^/\s]+\.)?cartotecadigital\.icc\.cat)" }, 
    u"Almirall, portal del pensamiento del Segle XIX": { 'regexp': ur"(?im)(https?://(?:[^/\s]+\.)?194\.224\.194\.201\:9080/Almirall/)" }, 
    u"Disposit Digital UAB": { 'regexp': ur"(?im)(https?://(?:[^/\s]+\.)?ddd\.uab\.cat)" }, 
    
    #TEST
    u"Archivo ABC": { 'regexp': ur"(?im)(https?://(?:[^/\s]+\.)?hemeroteca\.abc\.es)" }, 
    u"Hemeroteca La Vanguardia": { 'regexp': ur"(?im)(https?://(?:[^/\s]+\.)?hemeroteca\.lavanguardia\.es)" },
    u"LOC": { 'regexp': ur"(?im)(https?://(?:[^/\s]+\.)?loc\.gov)" },
    
}

for repository, props in repositories.items():
    repositories[repository]['compiled'] = re.compile(props['regexp'])
    repositories[repository]['links'] = []
    repositories[repository]['totallinks'] = 0
    repositories[repository]['articles'] = {}

if not 'page' in sys.argv[1] or not 'external' in sys.argv[2]:
    print 'param 1 = pages dump, param 2 = externallinks dump'
    sys.exit()

#load page ids for namespace = 0 non-redirects
page_r = re.compile(ur"\((\d+?),(\d+?),'(.*?)','(.*?)',(\d+?),(\d+?),(\d+?),([\.\d]+?),'(.*?)',(\d+?),(\d+?),(\d+?)\)")
f = gzip.open(sys.argv[1], 'r')
page_ids = {}
for l in f:
    for page in re.findall(page_r, l):
        page_id = int(page[0])
        namespace = int(page[1])
        page_is_redirect = int(page[5])
        if namespace == 0 and \
            page_is_redirect == 0:
            page_ids[page_id] = ''
f.close()
print 'Loaded', len(page_ids.keys()), 'page ids'

#load external links
cpages = len(page_ids.keys())
pageswithrepolinks = {}
cpageswithrepolinks = 0
clinks = 0
crepolinks = 0

externallink_r = re.compile(ur"\((\d+?),'(.*?)','(.*?)'\)")
f = gzip.open(sys.argv[2], 'r')
breakk = False
for l in f:
    l = unicode(l, 'utf-8')
    if breakk:
        break
    for externallink in re.findall(externallink_r, l):
        if breakk:
            break
        el_from = int(externallink[0])
        el_to = externallink[1]
        if not page_ids.has_key(el_from): #not from an article? skip
            continue
        
        clinks += 1
        for repository, props in repositories.items():
            if re.search(props['compiled'], el_to):
                crepolinks += 1
                repositories[repository]['links'].append(el_to)
                repositories[repository]['totallinks'] += 1
                if not pageswithrepolinks.has_key(el_from):
                    pageswithrepolinks[el_from] = ''
                if not repositories[repository]['articles'].has_key(el_from):
                    repositories[repository]['articles'][el_from] = ''
                break
        
        if clinks and clinks % 10000 == 0:
            print 'Analysed', clinks, 'external links'
            #breakk = True
f.close()

cpageswithrepolinks = len(pageswithrepolinks.keys())

print u"== Links =="
for repository, props in repositories.items():
    output = u"\n=== %s ===" % (repository)
    print output.encode('utf-8')
    output = u'\n'.join(props["links"])
    print output.encode('utf-8')

ranking = []
for repository, props in repositories.items():
    if props['totallinks'] > 0:
        ranking.append([props['totallinks'], "%s;%d;%d" % (repository, props['totallinks'], len(props['articles']))])
ranking.sort(reverse=True)

print u"\n== Ranking =="
output = u'\n'.join([j for i, j in ranking])
print output.encode('utf-8')
print u"\nTotal articles analysed: %d. Total articles with links to repositories: %d (%.2f%%)." % (cpages, cpageswithrepolinks, cpageswithrepolinks/(cpages/100.0))
print u"Total links: %d. Total links to repositories: %d (%.2f%%)." % (clinks, crepolinks, crepolinks/(clinks/100.0))
