#! /usr/bin/env python
# -*- coding: utf-8 -*-
import os, sys
path = os.path.abspath(os.path.join(os.path.dirname('.'),os.path.pardir))
sys.path.append(path)

import logging
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import tornado.websocket
from collections import defaultdict
from tornado.ioloop import PeriodicCallback
from register import COMMANDS
from utils import import_object


class MessageSocketHandler(tornado.websocket.WebSocketHandler):

    conn_num = 0 
    
    def open(self):
        self.conn_num += 1
        self.sub_messages = defaultdict(list)
        self.handler = {}
        
        for op, handle in COMMANDS.items():
            self.handler[op] = import_object(handle)
        
        self.callback = PeriodicCallback(self.on_send, 1000)
        self.callback.start()
    
    def check_origin(self, origin):
        return True  
    
    def on_close(self):
        self.conn_num -= 1
        self.callback.stop()

    def on_message(self, message):
        try:
            cmd =  eval(message)
            if cmd["op"]  in COMMANDS:
                self.sub_messages[cmd["op"]].extend(cmd["data"])
            if cmd["op"] == "clear_sub":
                self.sub_messages.clear()
        except Exception, e:
            print str(e)
        
    
    def on_send(self):
        print "send: %d" % len(self.sub_messages)
        for op, data in self.sub_messages.items():
            print op, data
            resp = self.handler[op].sub_process(op, data)
            if resp:
                self.write_message(resp)
            
            
def main():
    application = tornado.web.Application([
        ('/ws', MessageSocketHandler)
    ], debug=True)
    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(8000)
    tornado.ioloop.IOLoop.instance().start()

if __name__ == '__main__':
    main()