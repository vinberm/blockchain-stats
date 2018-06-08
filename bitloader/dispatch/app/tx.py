#! /usr/bin/env python
# -*- coding: utf-8 -*-

from config import message
from core import Radio
import binascii
from application import app

@message.register_app(name='hashtx')
def init_hashtx(conf):
    show = Radio(conf)
    show.set_handler(u'hashtx', TxHandler)


@message.register_app(name='rawtx')
def init_rawtx(conf):
    show = Radio(conf)
    show.set_handler(u'rawtx', TxRawHandler)


class TxHandler(object):
    
    def process(self, pub, topic, body):
       #tid = binascii.hexlify(body)
       print topic, body 
       app.send_task('tx_process', args=(topic, body))
       

class TxRawHandler(object):
    
    def process(self, pub, topic, body):
       #tid = binascii.hexlify(body)
       print topic
       app.send_task('tx_process', args=(topic, body))