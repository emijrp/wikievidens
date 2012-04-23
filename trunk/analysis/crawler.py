# -*- coding: utf-8 -*-

import socket
import sys
import thread
import time
import urllib2

# los access denied pueden ser bloqueos del user-agent de python

def check_url(url):
    try:
        req = urllib2.Request(url, None, headers)
        html = urllib2.urlopen(req, None, timeout).read()
    except urllib2.HTTPError, err:
        if err.code == 404:
            print "Page not found!", '|', url
        elif err.code == 403:
            print "Access denied!", '|',url
        else:
            print "Something happened! Error code", err.code, '|', url
        return
    except urllib2.URLError, err:
        print "Some other error happened:", err.reason, '|', url
        return
    except socket.timeout, err:
        print "Timeout", '|', url
        return
    
    print 'OK', '|', url

headers = { 'User-Agent' : 'Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:11.0) Gecko/20100101 Firefox/11.0' }
timeout = 25 # pueden ser PDFs, que hacemos?
for url in open(sys.argv[1], 'r').read().splitlines():
    if 'pdf' in url.lower() or 'hemeroteca.abc' in url.lower(): #checked sample randomly by hand and they are OK: cervantesvirtual, hemeroteca.lavanguardia.es, saber.es...
        print 'Skiping PDF', '|', url
        continue
    
    thread.start_new_thread(check_url, (url,))
    time.sleep(0.5)

time.sleep(timeout+5)
