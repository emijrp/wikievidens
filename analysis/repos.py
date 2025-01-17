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
    u"Europeana": { 'regexp': ur"(?im)(https?://(?:[^/\s]+\.)?europeana\.eu/[^\|\]\s\<]+/record/|https?://(?:[^/\s]+\.)?europeanaregia\.eu)", 'type': 'EU' }, 
    u"Portal Europeo de Archivos": { 'regexp': ur"(?im)(https?://(?:[^/\s]+\.)?archivesportaleurope\.eu)", 'type': 'EU' }, 
    u"The European Library": { 'regexp': ur"(?im)(https?://(?:[^/\s]+\.)?theeuropeanlibrary\.org)", 'type': 'EU' }, 
    
    #ES
    u"Biblioteca Digital Hispánica y Hemeroteca Histórica BNE": { 'regexp': ur"(?im)(https?://(?:[^/\s]+\.)?(?:bdh|bibliotecadigitalhispanica|hemerotecadigital)\.bne\.es)", 'type': 'ES' }, 
    u"Biblioteca Virtual de Prensa Histórica": { 'regexp': ur"(?im)(https?://(?:[^/\s]+\.)?prensahistorica\.mcu\.es)", 'type': 'ES' }, 
    u"Biblioteca Virtual del Patrimonio Bibliográfico": { 'regexp': ur"(?im)(https?://(?:[^/\s]+\.)?bvpb\.mcu\.es)", 'type': 'ES' }, 
    u"CERES. Red Digital de Colecciones de Museos de España": { 'regexp': ur"(?im)(https?://(?:[^/\s]+\.)?ceres\.mcu\.es)", 'type': 'ES' }, 
    u"Pares. Portal Archivos": { 'regexp': ur"(?im)(https?://(?:[^/\s]+\.)?pares\.mcu\.es[^\|\]\s\<]+(?:nid|txt_id_desc_ud)\=)", 'type': 'ES' },
    u"Fototeca Patrimonio Histórico": { 'regexp': ur"(?im)(https?://(?:[^/\s]+\.)?(?:mcu\.es/fototeca_patrimonio/|ipce\.mcu\.es/documentacion/fototeca/))", 'type': 'ES' },
    u"Recolector Hispana": { 'regexp': ur"(?im)(https?://(?:[^/\s]+\.)?roai\.mcu\.es)", 'type': 'ES' },
    
    #REG
    u"Biblioteca Digital de la Región de Murcia": { 'regexp': ur"(?im)(https?://(?:[^/\s]+\.)?bibliotecadigital\.carm\.es)", 'type': 'REG' },
    u"Biblioteca Virtual de Andalucía": { 'regexp': ur"(?im)(https?://(?:[^/\s]+\.)?bibliotecavirtualdeandalucia\.es)", 'type': 'REG' }, 
    u"Biblioteca Virtual de Aragón": { 'regexp': ur"(?im)(https?://(?:[^/\s]+\.)?bibliotecavirtual\.aragon\.es)", 'type': 'REG' }, 
    u"Fondo Histórico Cortes de Aragón": { 'regexp': ur"(?im)(https?://(?:[^/\s]+\.)?cortesaragon\.es)", 'type': 'REG' }, 
    u"Biblioteca Digital de Castilla y León": { 'regexp': ur"(?im)(https?://(?:[^/\s]+\.)?bibliotecadigital\.jcyl\.es)", 'type': 'REG' }, 
    u"Archivo de la imagen de Castilla-La Mancha": { 'regexp': ur"(?im)(https?://(?:[^/\s]+\.)?clip\.jccm\.es/archivo_de_la_imagen)", 'type': 'REG' }, 
    u"Biblioteca Digital de Castilla-La Mancha": { 'regexp': ur"(?im)(https?://(?:[^/\s]+\.)?clip\.jccm\.es/bidicam/)", 'type': 'REG' }, 
    u"Biblioteca Digital de la Comunidad Madrid": { 'regexp': ur"(?im)(https?://(?:[^/\s]+\.)?bibliotecavirtualmadrid\.org)", 'type': 'REG' }, 
    u"Memoria Digital Catalunya": { 'regexp': ur"(?im)(https?://(?:[^/\s]+\.)?mdc\.cbuc\.cat)", 'type': 'REG' }, 
    u"ARCA. Arxiu de Revistes Catalanes Antigues": { 'regexp': ur"(?im)(https?://(?:[^/\s]+\.)?mdc2\.cbuc\.cat)", 'type': 'REG' }, 
    u"BiValdi. Biblioteca Digital Valenciana": { 'regexp': ur"(?im)(https?://(?:[^/\s]+\.)?bv2\.gva\.es)", 'type': 'REG' }, 
    u"BINADI. Biblioteca Digital de Navarra": { 'regexp': ur"(?im)(https?://(?:[^/\s]+\.)?(?:administracionelectronica\.navarra\.es/binadi/|navarra\.es/appsext/bnd/))", 'type': 'REG' }, 
    u"Biblioteca Digital Vasca": { 'regexp': ur"(?im)(https?://(?:[^/\s]+\.)?liburuklik\.euskadi\.net)", 'type': 'REG' }, 
    u"Memoria Digital Vasca": { 'regexp': ur"(?im)(https?://(?:[^/\s]+\.)?memoriadigitalvasca\.es)", 'type': 'REG' }, 
    u"Galiciana. Biblioteca Digital de Galicia": { 'regexp': ur"(?im)(https?://(?:[^/\s]+\.)?galiciana\.bibliotecadegalicia\.xunta\.es)", 'type': 'REG' }, 
    u"Biblioteca Dixital de Galicia (Cidade de Cultura Galega)": { 'regexp': ur"(?im)(https?://(?:[^/\s]+\.)?(?:csbg\.org/bibliotecadixital/|csbg\.org/prensagalega|cmg\.xunta\.es/visor/prensa/|cmg\.xunta\.es/mediateca/hemeroteca/|bvg\.centromultimedia\.net|cmg\.xunta\.es/mediateca/cartografia/))", 'type': 'REG' }, 
    u"Memoria Digital de Canarias": { 'regexp': ur"(?im)(https?://(?:[^/\s]+\.)?mdc\.ulpgc\.es)", 'type': 'REG' }, 
    u"Proyecto Carmesí Región de Murcia": { 'regexp': ur"(?im)(https?://(?:[^/\s]+\.)?regmurcia\.com/[^\|\]\s\<]+&sit\=c,373)", 'type': 'REG' }, 
    u"Biblioteca Virtual de Asturias": { 'regexp': ur"(?im)(https?://(?:[^/\s]+\.)?bibliotecavirtual\.asturias\.es)", 'type': 'REG' }, 
    u"Biblioteca Virtual de La Rioja": { 'regexp': ur"(?im)(https?://(?:[^/\s]+\.)?bibliotecavirtual\.larioja\.org)", 'type': 'REG' }, 
    u"ANC. Arxiu Nacional Catalunya": { 'regexp': ur"(?im)(https?://(?:[^/\s]+\.)?cultura\.gencat\.net/anc/)", 'type': 'REG' }, 
    u"Documentos y Archivos de Aragón": { 'regexp': ur"(?im)(https?://(?:[^/\s]+\.)?sipca\.es/dara/)", 'type': 'REG' }, 
    
    #LOC
    u"Biblioteca Virtual Diputación de Zaragoza": { 'regexp': ur"(?im)(https?://(?:[^/\s]+\.)?bivizar\.es)", 'type': 'LOC' },
    u"Biblioteca Digital Ayuntamiento Murcia": { 'regexp': ur"(?im)(https?://(?:[^/\s]+\.)?murcia\.es/bibliotecadigitaldemurcia/)", 'type': 'LOC' },
    u"Biblioteca Digital Leonesa": { 'regexp': ur"(?im)(https?://(?:[^/\s]+\.)?saber\.es)", 'type': 'LOC' },
    u"Memoria de Madrid": { 'regexp': ur"(?im)(https?://(?:[^/\s]+\.)?memoriademadrid\.es)", 'type': 'LOC' }, 
    u"Biblioteca Digital de Bizkaia": { 'regexp': ur"(?im)(https?://(?:[^/\s]+\.)?bibliotecaforal\.bizkaia\.net)", 'type': 'LOC' }, 
    
    #UNI
    u"Fondo Antiguo Universidad Zaragoza": { 'regexp': ur"(?im)(https?://(?:[^/\s]+\.)?zaguan\.unizar\.es)", 'type': 'UNI' }, 
    u"Digitum. Fondo Antiguo Universidad de Murcia": { 'regexp': ur"(?im)(https?://(?:[^/\s]+\.)?(?:digitum\.um\.es|hdl\.handle\.net/10201/))", 'type': 'UNI' }, 
    u"Somni. Fondo Histórico Universidad de Valencia": { 'regexp': ur"(?im)(https?://(?:[^/\s]+\.)?(?:roderic\.uv\.es|hdl\.handle\.net/10550/))", 'type': 'UNI' }, 
    u"Fondo Antiguo Universidad de Granada": { 'regexp': ur"(?im)(https?://(?:[^/\s]+\.)?(?:digibug\.ugr\.es|hdl\.handle\.net/10481/))", 'type': 'UNI' }, 
    u"Gredos. Colecciones patrimoniales Universidad Salamanca": { 'regexp': ur"(?im)(https?://(?:[^/\s]+\.)?(?:gredos\.usal\.es|hdl\.handle\.net/10366/))", 'type': 'UNI' }, 
    u"Fondo antiguo Universidad Sevilla": { 'regexp': ur"(?im)(https?://(?:[^/\s]+\.)?fondosdigitales\.us\.es/fondos/)", 'type': 'UNI' }, 
    u"Colecciones digitales Univ. Barcelona": { 'regexp': ur"(?im)(https?://(?:[^/\s]+\.)?bib\.ub\.edu/recursos\-informacio/colleccions/colleccions\-digitals/)", 'type': 'UNI' }, 
    u"Biblioteca Digital Complutense": { 'regexp': ur"(?im)(https?://(?:[^/\s]+\.)?alfama\.sim\.ucm\.es)", 'type': 'UNI' }, 
    u"Fondo fotográfico siglo XX Universidad de Navarra": { 'regexp': ur"(?im)(https?://(?:[^/\s]+\.)?coleccionfff\.unav\.es/bvunav)", 'type': 'UNI' }, 
    u"Disposit Digital UAB": { 'regexp': ur"(?im)(https?://(?:[^/\s]+\.)?ddd\.uab\.cat)", 'type': 'UNI' }, 
    u"Biblioteca Digital UIMP": { 'regexp': ur"(?im)(https?://(?:[^/\s]+\.)?bduimp\.es/archivo)", 'type': 'UNI' }, 
    u"DUGi Fons Especials": { 'regexp': ur"(?im)(https?://(?:[^/\s]+\.)?(?:dugifonsespecials\.udg\.edu|hdl\.handle\.net/10256\.2/))", 'type': 'UNI' }, 
    u"Fondo Antiguo Universidad de Alcalá": { 'regexp': ur"(?im)(https?://(?:[^/\s]+\.)?(?:dspace\.uah\.es|hdl\.handle\.net/10017/))", 'type': 'UNI' }, 
    u"Helvia Difusión. Repositorio Universidad de Huelva": { 'regexp': ur"(?im)(https?://(?:[^/\s]+\.)?(?:helvia\.uco\.es|hdl\.handle\.net/10396/))", 'type': 'UNI' }, 
    u"Jable. Archivo de prensa digital. ULPG": { 'regexp': ur"(?im)(https?://(?:[^/\s]+\.)?jable\.ulpgc\.es)", 'type': 'UNI' }, 
    u"Biblioteca Digital de Castellón": { 'regexp': ur"(?im)(https?://(?:[^/\s]+\.)?(?:repositori\.uji\.es|hdl\.handle\.net/10234/))", 'type': 'UNI' }, 
    u"Repositori Obert UdL. Fons Especials": { 'regexp': ur"(?im)(https?://(?:[^/\s]+\.)?(?:repositori\.udl\.cat/handle/10459\.2/|hdl\.handle\.net/10459\.2/))", 'type': 'UNI' }, 
    u"Universidad Santigo Compostela": { 'regexp': ur"(?im)(https?://(?:[^/\s]+\.)?(?:dspace\.usc\.es|hdl\.handle\.net/10347/))", 'type': 'UNI' }, 
    u"Universidad Internacional de Andalucía. Fondo Histórico Digital de La Rábida": { 'regexp': ur"(?im)(https?://(?:[^/\s]+\.)?(?:dspace\.unia\.es|hdl\.handle\.net/10334/))", 'type': 'UNI' }, 
    u"RIUMA. Universidad de Málaga. Patrimonio": { 'regexp': ur"(?im)(https?://(?:[^/\s]+\.)?(?:riuma\.uma\.es|hdl\.handle\.net/10630/))", 'type': 'UNI' }, 
    u"Rodin. Universidad de Cádiz. Patrimonio bibliográfico": { 'regexp': ur"(?im)(https?://(?:[^/\s]+\.)?(?:rodin\.uca\.es|hdl\.handle\.net/10498/))", 'type': 'UNI' }, 
    u"Repositorio Universidad Coruña": { 'regexp': ur"(?im)(https?://(?:[^/\s]+\.)?(?:ruc\.udc\.es|hdl\.handle\.net/2183/))", 'type': 'UNI' }, 
    u"Ruidera. UCLM": { 'regexp': ur"(?im)(https?://(?:[^/\s]+\.)?(?:ruidera\.uclm\.es|hdl\.handle\.net/10578/))", 'type': 'UNI' }, 
    u"UvaDoc. Universidad de Valladolid": { 'regexp': ur"(?im)(https?://(?:[^/\s]+\.)?uvadoc\.uva\.es)", 'type': 'UNI' }, 
    u"Arias Montano: Repositorio Institucional de la Universidad de Huelva": { 'regexp': ur"(?im)(https?://(?:[^/\s]+\.)?(?:rabida\.uhu\.es/dspace/|hdl\.handle\.net/10272/))", 'type': 'UNI' }, 
    u"CEU Repositorio Institucional": { 'regexp': ur"(?im)(https?://(?:[^/\s]+\.)?(?:dspace\.ceu\.es|hdl\.handle\.net/10637/))", 'type': 'UNI' }, 
    u"Flons So Torres. Universitat Lérida": { 'regexp': ur"(?im)(https?://(?:[^/\s]+\.)?(?:soltorres\.udl\.cat|hdl\.handle\.net/10459/))", 'type': 'UNI' }, 
    u"Biblioteca Digital Universidad de Oviedo": { 'regexp': ur"(?im)(https?://(?:[^/\s]+\.)?digibuo\.sheol\.uniovi\.es)", 'type': 'UNI' }, 
    
    #INS
    u"Biblioteca Virtual de Derecho Aragonés": { 'regexp': ur"(?im)(https?://(?:[^/\s]+\.)?derechoaragones\.es)", 'type': 'INS' }, 
    u"Portal Teatro Siglo de Oro": { 'regexp': ur"(?im)(https?://(?:[^/\s]+\.)?teatrosiglodeoro\.bne\.es)", 'type': 'INS' }, 
    u"Biblioteca Virtual Miguel de Cervantes": { 'regexp': ur"(?im)(https?://(?:[^/\s]+\.)?cervantesvirtual\.com)", 'type': 'INS' }, 
    u"Biblioteca Digital Ateneo Madrid": { 'regexp': ur"(?im)(https?://(?:[^/\s]+\.)?ateneodemadrid\.com/biblioteca_digital/)", 'type': 'INS' }, 
    u"Biblioteca Digital Jardín Botánico": { 'regexp': ur"(?im)(https?://(?:[^/\s]+\.)?bibdigital\.rjb\.csic\.es)", 'type': 'INS' }, 
    u"Archivo Ateneo Madrid": { 'regexp': ur"(?im)(https?://(?:[^/\s]+\.)?archivo\.ateneodemadrid\.es)", 'type': 'INS' }, 
    u"Biblioteca Virtual Larramendi": { 'regexp': ur"(?im)(https?://(?:[^/\s]+\.)?larramendi\.es/i18n/)", 'type': 'INS' }, 
    u"Iuris Digital. Biblioteca Digital de la Real Academia de Jurisprudencia y Legislación": { 'regexp': ur"(?im)(https?://(?:[^/\s]+\.)?bvrajyl\.insde\.es)", 'type': 'INS' }, 
    u"Cartoteca Digital i Col·leccions d'imatges del Institut Cartografic de Catalunya": { 'regexp': ur"(?im)(https?://(?:[^/\s]+\.)?cartotecadigital\.icc\.cat)", 'type': 'INS' }, 
    u"Almirall, portal del pensamiento del Segle XIX": { 'regexp': ur"(?im)(https?://(?:[^/\s]+\.)?194\.224\.194\.201\:9080/Almirall/)", 'type': 'INS' }, 
    u"Repositorio de la Alhambra": { 'regexp': ur"(?im)(https?://(?:[^/\s]+\.)?(?:alhambra\-patronato\.es/ria/|hdl\.handle\.net/10514/))", 'type': 'INS' }, 
    u"Repositorio de la Real Academia de Córdoba de Ciencias, Bellas Letras y Nobles Artes": { 'regexp': ur"(?im)(https?://(?:[^/\s]+\.)?(?:repositorio\.racordoba\.es|hdl\.handle\.net/10853/))", 'type': 'INS' }, 
    u"Biblioteca Digital Fundación Sierra de Pambley": { 'regexp': ur"(?im)(https?://(?:[^/\s]+\.)?bibliotecavirtualsierrapambley\.org)", 'type': 'INS' }, 
    u"Biblioteca Saavadra Fajardo de Pensamiento Político Hispánico": { 'regexp': ur"(?im)(https?://(?:[^/\s]+\.)?saavedrafajardo\.um\.es)", 'type': 'INS' }, 
    u"Biblioteca Virtual de la Real Academia Nacional de Farmacia": { 'regexp': ur"(?im)(https?://(?:[^/\s]+\.)?bibliotecavirtual\.ranf\.com)", 'type': 'INS' }, 
    u"Biblioteca Digital Real Academia Historia": { 'regexp': ur"(?im)(https?://(?:[^/\s]+\.)?bibliotecadigital\.rah\.es)", 'type': 'INS' }, 
    
    #TEST
    u"Archivo ABC": { 'regexp': ur"(?im)(https?://(?:[^/\s]+\.)?hemeroteca\.abc\.es)", 'type': 'TEST' }, 
    u"Hemeroteca La Vanguardia": { 'regexp': ur"(?im)(https?://(?:[^/\s]+\.)?hemeroteca\.lavanguardia\.es)", 'type': 'TEST' },
    u"Memoria de Chile": { 'regexp': ur"(?im)(https?://(?:[^/\s]+\.)?memoriachilena\.cl)", 'type': 'TEST' },
    u"Biblioteca Digital Mundial de Unesco": { 'regexp': ur"(?im)(https?://(?:[^/\s]+\.)?wdl\.org)", 'type': 'TEST' },
    u"LOC": { 'regexp': ur"(?im)(https?://(?:[^/\s]+\.)?loc\.gov)", 'type': 'TEST' },
    u"Google Books": { 'regexp': ur"(?im)(https?://(?:[^/\s]+\.)?books\.google\.com)", 'type': 'TEST' },
    
}

for repository, props in repositories.items():
    print 'Compiling', props['regexp']
    repositories[repository]['compiled'] = re.compile(props['regexp'])
    repositories[repository]['links'] = []
    repositories[repository]['totallinks'] = 0
    repositories[repository]['articles'] = {}

if not 'page' in sys.argv[1] or not 'external' in sys.argv[2]:
    print 'param 1 = pages dump, param 2 = externallinks dump'
    sys.exit()

lang = sys.argv[1].split('wiki')[0]
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
                if props['type'] != 'TEST':
                    crepolinks += 1
                repositories[repository]['links'].append(el_to)
                repositories[repository]['totallinks'] += 1
                if not pageswithrepolinks.has_key(el_from) and props['type'] != 'TEST':
                    pageswithrepolinks[el_from] = ''
                if not repositories[repository]['articles'].has_key(el_from):
                    repositories[repository]['articles'][el_from] = ''
                break
        
        if clinks and clinks % 1000 == 0:
            print 'Analysed', clinks, 'external links'
            #breakk = True
f.close()

cpageswithrepolinks = len(pageswithrepolinks.keys())

#links
output = u"repository\tlink\ttype"
for repository, props in repositories.items():
    for link in props["links"]:
        output += u'\n%s\t%s\t%s' % (repository, link, props['type'])
f = open('repos.%s.links.csv' % lang, 'w')
f.write(output.encode('utf-8'))
f.close()

#repos
output = u"repository\tlinks\tarticles\ttype\tratio"
for repository, props in repositories.items():
    totalarticles = len(props['articles'].keys())
    output += u"\n%s\t%d\t%d\t%s\t%f" % (repository, props['totallinks'], totalarticles, props['type'], totalarticles and float(props['totallinks'])/totalarticles or 0)
f = open('repos.%s.ranking.csv' % lang, 'w')
f.write(output.encode('utf-8'))
f.close()

#summary
print u"\nTotal articles analysed: %d. Total articles with links to repositories (without TEST): %d (%.2f%%)." % (cpages, cpageswithrepolinks, cpageswithrepolinks/(cpages/100.0))
print u"Total links: %d. Total links to repositories (without TEST): %d (%.2f%%)." % (clinks, crepolinks, crepolinks/(clinks/100.0))
