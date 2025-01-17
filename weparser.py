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

import datetime
import re
import sqlite3
import subprocess
import time
import xmlreader
import sys
import os
import hashlib
import tkMessageBox
import zlib
#import bz2 as zlib
import cPickle
import difflib

#TODO:
#campos adicionales: categorías, ficheros, plantillas, etc
#capturar los namespaces del comienzo del XML y meter un campo namespace en la tabla page

#fix filtrar Mediawiki default (que aparece como ip)
#todo añadir un campo a la base de datos como último apso, para indicar que todo el parseo fue bien (esto sirve para avisar al usuario cuando hace #Load que el fichero está "corrupto" y debe reparsear)

"""
regexps para el parser
re.compile(ur"#\s*(REDIRECT|local name)\s*\[\[[^\|\]]+?(\|[^\|\]]*?)?\]\]")
"""

def createDB(conn=None, cursor=None):
    #en comentarios cosas que se pueden añadir
    #algunas ideas de http://git.libresoft.es/WikixRay/tree/WikiXRay/parsers/dump_sax_research.py
    cursor.execute('''create table image (img_name text)''') #quien la ha subido? eso no está en el xml, sino en pagelogging...
    cursor.execute('''create table revision (rev_id integer, rev_title text, rev_page integer, rev_user_text text, rev_is_ipedit integer, rev_timestamp timestamp, rev_text text, rev_text_md5 text, rev_text_diff blob, rev_size integer, rev_comment text, rev_internal_links integer, rev_external_links integer, rev_interwikis integer, rev_sections integer, rev_templates integer)''')
    #rev_is_minor, rev_is_redirect, rev_highwords (bold/italics/bold+italics), rev_diff, ref_diff_len, rev_maths, rev_refs (<ref>, <ref name), rev_categories, ref_html_tags (- rev_refs, - rev_maths)
    cursor.execute('''create table page (page_id integer, page_title text, page_editcount integer, page_creation_timestamp timestamp, page_last_timestamp timestamp, page_text blob, page_size integer, page_internal_links integer, page_external_links integer, page_interwikis integer, page_sections integer, page_templates integer)''') 
    #page_namespace, page_views, page_editorscount (number of distinct editors)
    cursor.execute('''create table user (user_name text, user_is_ip integer, user_editcount integer, user_first_timestamp timestamp, user_last_timestamp timestamp)''') #fix, poner si es ip basándonos en ipedit?
    #user_id (viene en el dump? 0 para ips), user_is_anonymous (ips)
    conn.commit()

def generateUserTable(conn, cursor):
    result = cursor.execute("SELECT rev_user_text AS user_name, rev_is_ipedit AS user_is_ip, COUNT(*) AS user_editcount, MIN(rev_timestamp) AS user_first_timestamp, MAX(rev_timestamp) AS user_last_timestamp FROM revision WHERE 1 GROUP BY user_name")
    users = []
    for user_name, user_is_ip, user_editcount, user_first_timestamp, user_last_timestamp in result:
        users.append([user_name, user_is_ip, user_editcount, user_first_timestamp, user_last_timestamp])

    for user_name, user_is_ip, user_editcount, user_first_timestamp, user_last_timestamp in users:
        cursor.execute('INSERT INTO user VALUES (?,?,?,?,?)', (user_name, user_is_ip, user_editcount, user_first_timestamp, user_last_timestamp))
    conn.commit()

    print "GENERATED USER TABLE: %d" % (len(users))

def generateAuxTables(conn=None, cursor=None):
    print '#'*30, '\n', 'Generating auxiliar tables', '\n', '#'*30
    generateUserTable(conn=conn, cursor=cursor)

def parseMediaWikiXMLDump(self, dumpfilename=None, dbfilename=None, revlimit=None, pagelimit=None):
    #extract only the first .xml file available, scan the content
    s = subprocess.Popen('7z l %s' % dumpfilename, shell=True, stdout=subprocess.PIPE, bufsize=65535).stdout
    raw = s.read()
    xmlfilename = ''
    if re.findall(ur"(?im)^\d{4}-\d{2}-\d{2}.* ([^$]+\.xml)$", raw):
        xmlfilename = re.findall(ur"(?im)^\d{4}-\d{2}-\d{2}.* ([^$]+\.xml)$", raw)[0]
    
    if os.path.exists(dbfilename): #si existe lo borramos, pues el usuario ha marcado sobreescribir, sino no entraría aquí #fix, mejor renombrar?
        os.remove(dbfilename)

    conn = sqlite3.connect(dbfilename)
    cursor = conn.cursor()

    # Create table
    createDB(conn=conn, cursor=cursor)

    limit = 1000
    c = 0
    c_page = 0
    t1 = time.time()
    tt = time.time()
    
    r_internal_links = re.compile(ur'(?i)(\[\[[^\|\]\r\n]+?(\|[^\|\]\r\n]*?)?\]\])') #descontar external, images, categories, interwiki?
    r_external_links = re.compile(ur'(?i)\b(ftps?|git|gopher|https?|irc|mms|news|svn|telnet|worldwind)://')
    # http://en.wikipedia.org/wiki/Special:SiteMatrix
    r_interwikis = re.compile(ur'(?i)(\[\[([a-z]{2,3}|simple|classical)(\-([a-z]{2,3}){1,2}|tara)?\:[^\[\]]+?\]\])')
    r_sections = re.compile(ur'(?im)^(={1,6})[^=]+\1')
    r_templates = re.compile(ur'(?im)(^|[^\{])\{\{[^\{\}\|]+[\}\|]') # {{T1|...}} or {{T1}}
    
    xml = xmlreader.XmlDump(dumpfilename, innerxml=xmlfilename, allrevisions=True)
    errors = 0
    errors_page = 0
    page_id = -1 #impossible value
    page_title = ''
    page_editcount = 0
    page_creation_timestamp = ''
    page_last_timestamp = ''
    page_text = ''
    page_size = 0
    page_internal_links = 0
    page_external_links = 0
    page_interwikis = 0
    page_sections = 0
    page_templates = 0
    rev_prev_text_for_diff = ''
    
    for x in xml.parse(): #parsing the whole dump
        # Create page entry if needed
        if page_id != -1 and page_id != x.id:
            if page_id and page_title and page_editcount and page_creation_timestamp and page_last_timestamp: #page_text not needed, it can be a blanked page
                #fix, si le llega una página duplicada, mete dos o sobreescribe?
                #fix add namespace detector
                #fix add rev_id actual para cada pagina
                #meter estos valores para cada página usando la última revisión del historial: rev_size, rev_internal_links, rev_external_links, rev_interwikis, rev_sections, rev_timestamp, rev_text_md5; NO: rev_comment
                cursor.execute('INSERT OR IGNORE INTO page VALUES (?,?,?,?,?,?,?,?,?,?,?,?)', (page_id, page_title, page_editcount, page_creation_timestamp, page_last_timestamp, buffer(zlib.compress(page_text,9)), page_size, page_internal_links, page_external_links, page_interwikis, page_sections, page_templates))
                #conn.commit()
                c_page += 1
                if pagelimit and c_page >= pagelimit:
                    page_id = ''
                    break
            else:
                print '#'*30, '\n', 'ERROR PAGE:' , page_id, page_title, page_editcount, page_creation_timestamp, page_last_timestamp, 'text (', page_size, 'bytes)', page_text[:100], '\n', '#'*30
                errors_page += 1
            #reset values
            page_id = x.id
            page_title = x.title
            page_editcount = 0
            page_creation_timestamp = ''
            page_last_timestamp = ''
            page_text = ''
            page_size = 0
            page_internal_links = 0
            page_external_links = 0
            page_interwikis = 0
            page_sections = 0
            page_templates = 0
            rev_prev_text_for_diff = ''
        
        page_editcount += 1
        rev_id = int(x.revisionid)
        rev_title = x.title
        if page_title == '':
            page_title = x.title
        rev_page = x.id
        if page_id == -1:
            page_id = rev_page
        rev_user_text = x.username
        rev_is_ipedit = x.ipedit and 1 or 0 #fix, las ediciones de MediaWiki default cuentan como IP?
        rev_timestamp = datetime.datetime(year=int(x.timestamp[0:4]), month=int(x.timestamp[5:7]), day=int(x.timestamp[8:10]), hour=int(x.timestamp[11:13]), minute=int(x.timestamp[14:16]), second=int(x.timestamp[17:19]))
        rev_text = x.text
        x_text_encoded = x.text.encode('utf-8')
        rev_text_md5 = hashlib.md5(x_text_encoded).hexdigest()
        #rev_text_diff = buffer(zlib.compress(cPickle.dumps(list(difflib.Differ().compare(rev_prev_text_for_diff.splitlines(1), x_text_encoded.splitlines(1)))),9))
        #el join es vacío '' porque los splitlines(1) adjuntan el \n final a cada línea
        rev_text_diff = '' #buffer(zlib.compress(''.join(list(difflib.Differ().compare(rev_prev_text_for_diff.splitlines(1), x_text_encoded.splitlines(1)))),9))
        rev_prev_text_for_diff = x_text_encoded
        rev_size = len(x.text)
        rev_comment = x.comment or ''
        rev_internal_links = len(re.findall(r_internal_links, x.text)) #fix enlaces internos (esto incluye los iws, descontarlos después?)
        rev_external_links = len(re.findall(r_external_links, x.text)) #external links http://en.wikipedia.org/wiki/User:Emijrp/External_Links_Ranking
        rev_interwikis = len(re.findall(r_interwikis, x.text))
        rev_internal_links -= rev_interwikis # removing interwikis from [[links]]
        rev_sections = len(re.findall(r_sections, x.text))
        rev_templates = len(re.findall(r_templates, x.text))
        
        #saving values if this revision is the first or the last of a page
        if not page_creation_timestamp or rev_timestamp < page_creation_timestamp:
            page_creation_timestamp = rev_timestamp
        if not page_last_timestamp or rev_timestamp > page_last_timestamp:
            page_last_timestamp = rev_timestamp
            page_text = x_text_encoded
            page_size = len(x_text_encoded)
            page_internal_links = rev_internal_links
            page_external_links = rev_external_links
            page_interwikis = rev_interwikis
            page_sections = rev_sections
            page_templates = rev_templates
        
        # create tuple
        t = (rev_id, rev_title, rev_page, rev_user_text, rev_is_ipedit, rev_timestamp, rev_text, rev_text_md5, rev_text_diff, rev_size, rev_comment, rev_internal_links, rev_external_links, rev_interwikis, rev_sections, rev_templates)
        
        xmlbug = (rev_id, rev_title, rev_page, rev_user_text)
        if not None in xmlbug and not '' in xmlbug:
            #print rev_id
            cursor.execute('INSERT OR IGNORE INTO revision VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)', t)
            c += 1
        else:
            #print t
            errors += 1
        
        if (c+errors) % limit == 0:
            self.msg(msg='Analysed %d revisions [%d revs/sec]' % (c+errors, limit/(time.time()-t1)))
            conn.commit()
            t1 = time.time()
        
        if revlimit and c >= revlimit:
            break
    
    #add the last page
    if page_id and page_title and page_editcount and page_creation_timestamp and page_last_timestamp: #page_text not needed, it can be a blanked page
        cursor.execute('INSERT OR IGNORE INTO page VALUES (?,?,?,?,?,?,?,?,?,?,?,?)', (page_id, page_title, page_editcount, page_creation_timestamp, page_last_timestamp, buffer(zlib.compress(page_text,9)), page_size, page_internal_links, page_external_links, page_interwikis, page_sections, page_templates))
        c_page += 1
    
    conn.commit() #para cuando son menos de limit o el resto
    
    print 'Total revisions [%d], correctly inserted [%d], errors [%d]' % (c+errors, c, errors)
    print 'Total pages [%d], correctly inserted [%d], errors [%d]' % (c_page+errors_page, c_page, errors_page)
    print 'Total time [%d secs or %2f minutes or %2f hours]' % (time.time()-tt, (time.time()-tt)/60.0, (time.time()-tt)/3600.0)

    #tablas auxiliares
    tt = time.time()
    generateAuxTables(conn=conn, cursor=cursor)
    print time.time()-tt, 'seconds'
    
    cursor.close()
    conn.close()

if __name__ == "__main__":
    filename = sys.argv[1]
    path = ''
    parseMediaWikiXMLDump(path, filename)
