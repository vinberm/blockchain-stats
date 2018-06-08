#! /usr/bin/env python
# -*- coding: utf-8 -*-
import sys, os
path = os.path.abspath(os.path.join(os.path.dirname('.'),os.path.pardir))
sys.path.append(path)
import logging
import core
import app
import getopt
import config
from zmq.eventloop.ioloop import ZMQIOLoop
from config import message
from register import apps



def process():
    message.setup(apps)
    ZMQIOLoop.instance().start()


if __name__ == "__main__":
    try:
        includes = None
        config_path = '.'
        opts, argvs = getopt.getopt(sys.argv[1:], "c:h")
        for op, value in opts:
            if op == '-c':
                includes = value
                config_path = os.path.dirname(os.path.abspath(value))
            elif op == '-h':
                print u'''使用参数启动:
                        usage: [-c]
                        -c <file> 加载配置文件 (默认为: default.conf）
                   '''
                sys.exit(0)
        
        if not includes:
            includes = os.path.join(config_path, 'default.conf')
            print "No Configuration Found!, Use [%s] Instead" % includes
    
    
        logging.basicConfig(level=logging.DEBUG,
                            format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                            datefmt='%m-%d %H:%M',
                            filename='../logs/dispatch.log',
                            filemode='a')
        LOG = logging.getLogger('setup')
        LOG.debug('service started')
        config.config_parse(includes)
        #test 
        #config.CONFIGS.daemon = True
        process()
        
    except Exception,e:
        LOG.error('Service terminated: %s' % str(e))
        sys.exit(1)
