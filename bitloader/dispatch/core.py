#! /usr/bin/env python
# -*- coding: utf-8 -*-

import zmq, json
import logging
import redis
from zmq.eventloop.zmqstream import ZMQStream

LOG = logging.getLogger('radio')

class DefaultHandler(object):
    
    def process(self, topic, body):
       print topic, body


class Radio(object):

    def __init__(self, conf):
        self.config = conf
        self.pub = None
        self.handler = None
        self.connect()
        self.handlers = {}

        
    def set_handler(self, topic, handler):
        self.handlers[topic] = handler
    
    def broadcast(self, msg):
        try:
            topic, body = msg
            if not self.handler:
                self.handler = self.handlers.get(topic, DefaultHandler)()
            self.handler.process(self.pub, topic, body)
        except Exception, e:
            LOG.error("broadcast: %s" % str(e))
            self.socket.close()
            self.ctx.term()
            self.close()

        
            
    
      
    def connect(self):
        try:
            self.ctx = zmq.Context()
            self.socket = self.ctx.socket(zmq.SUB)            
            self.socket.connect(self.config['protocol'])
            self.stream = ZMQStream(self.socket)
            self.stream.on_recv(self.broadcast)
            self.config_sub(self.config['topic'])
            self.config_pub(self.config['publish'])
        except Exception, e:
            print str(e)        
        
    def config_pub(self, conf):
        if conf['type'] == 'redis':
            self.pub = RedisClient(conf)
            
    def config_sub(self, topic):
        self.socket.setsockopt_string(zmq.SUBSCRIBE, unicode(topic))
    
    def close(self):
        self.stream.close()




class RedisClient:
    def __init__(self, conf):
        pool = redis.ConnectionPool(host=conf['host'], port=conf['port'], db=conf['db'])
        self.rc = redis.Redis(connection_pool=pool)
        
    def get(self, key):
        value = self.rc.get(key)
        return value if value else None
    
    def set_and_expire(self, key, value, expire):
        str_value = json.dumps(value, ensure_ascii=False)
        self.rc.set(key, value)
    
    def delete(self, key):
        self.rc.delete(key)
    
    def get_set_list(self, key):
        return self.rc.smembers(key)
    
    def add_set(self, key, value):  
        self.rc.sadd(key, value)
