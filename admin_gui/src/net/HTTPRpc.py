#!/usr/bin/python
#-*- coding: utf-8 -*-

import pycurl
import StringIO
import threading
import time
import json
import gobject

class ScovilleRPC(threading.Thread):
    HEADERS = ['Accept-Language: en-us,en;q=0.5',
                    #'Accept-Encoding: gzip,deflate', 
                    'Accept-Charset: ISO-8859-1,utf-8;q=0.7,*;q=0.7', 
                    'Content-Type: application/json; charset=UTF-8',
                    'Keep-Alive: 300', 
                    'Pragma: no-cache, no-cache',
                    'Cache-Control: no-cache, no-cache',
                    'Connection: Keep-Alive']
    USER_AGENT = 'ScovilleAdmin'    
    def __init__(self,server,callback, method, params=[]):
        threading.Thread.__init__(self)
        self.server = server
        self.callback = callback
        #TODO: Server Muss online sein! Check!
        self.curl = pycurlConnect = pycurl.Curl()
        
        json_enc = json.JSONEncoder()
        
        LOGIN_URL = 'http://'+server.getIp()+'/rpc/?nocache='+ str(int (time.time()*1000))
        POST_DATA = '{"service":"scoville_admin.scvRpc","method":"'+method+'","id":1,"params":'+json_enc.encode(params)+'}'
        self.pycurlConnect = pycurl.Curl()
        self.pycurlConnect.setopt(pycurl.URL, LOGIN_URL)
        self.pycurlConnect.setopt(pycurl.HTTPHEADER, self.HEADERS)
        self.pycurlConnect.setopt(pycurl.COOKIEFILE, 'cookies.txt')
        self.pycurlConnect.setopt(pycurl.POSTFIELDS, POST_DATA)
        self.pycurlConnect.setopt(pycurl.POST, 1)
        
    def run(self):        
        answer = StringIO.StringIO()
        
        json_dec = json.JSONDecoder()
        
        self.pycurlConnect.setopt(pycurl.WRITEFUNCTION, answer.write)
        self.pycurlConnect.perform()
        
        gobject.idle_add(self.callback,json_dec.decode(answer.getvalue()))
        #self.callback(json_dec.decode(answer.getvalue()))
        answer.close()
        self.pycurlConnect.close()
        
        