#! /usr/bin/env python
# -*- coding: utf-8 -*-

import zmq, time
from config import message
from core import Radio
from application import app

@message.register_app(name='node')
def init(conf):
    show = Radio(conf)
    show.set_handler(u'node', NodeHandler)


class NodeHandler(object):
        
    def process(self, pub, topic, body):
       print topic, len(body)
       app.send_task('node_process', args=(topic, body))
       
       
        
 