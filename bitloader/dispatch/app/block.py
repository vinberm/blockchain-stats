#! /usr/bin/env python
# -*- coding: utf-8 -*-

import zmq, time
from config import message
from core import Radio
from application import app


@message.register_app(name='rawblock')
def init(conf):
    show = Radio(conf)
    show.set_handler(u'rawblock', BlockHandler)


class BlockHandler(object):
        
    def process(self, pub, topic, body):
        app.send_task('block_process', args=(topic, body))
       
        
 