#! /usr/bin/env python
# -*- coding: utf-8 -*-
import sys, os
import logging
import gevent
import random
from sniffer import PeerManager
from publish import Messager
from config import Config
from dns import resolver



def crawler_nodes(seeds):
    
    nodes = set()
    resolve = resolver.Resolver()
    resolver.timeout = 1
    resolver.lifetime = 1
    for seed, prefix in seeds.items():
        for pfx in prefix:
            if pfx:
                uri = '{0}.{1}'.format(pfx, seed)
            else:
                uri = seed 
            try:  
                answers = resolve.query(uri, raise_on_no_answer=False).response.answer
            except Exception,e: 
                LOG.error('DNS query Error: %s' % str(e)) 
                continue     
            for ans in answers:
                for r in ans.items:
                    nodes.add(r.address)
    
    #return random.sample(list(nodes), Config.NODES_LIMITS) 
    return ["106.187.49.227",]   




    
def process():
    
    threads = []

    pub = Messager(Config.zmq_host, Config.zmq_port)
    peermgr = PeerManager(pub)
    
    for node in crawler_nodes(Config.seeds):
        c = peermgr.add(node, Config.rpc_port)
        threads.append(c)
        
    for t in threads: 
        t.start()
    try:
        gevent.joinall(threads,timeout=None, raise_error=True)
    finally:
        for t in threads: 
            t.kill()
        gevent.joinall(threads)
        LOG.debug('Sniffer end')      


if __name__ == "__main__":
    try:
    
        logging.basicConfig(level=logging.DEBUG,
                            format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                            datefmt='%m-%d %H:%M',
                            filename='../logs/sniffer.log',
                            filemode='a')
        LOG = logging.getLogger('setup')
        LOG.debug('service started') 
        process()
        
    except Exception,e:
        LOG.error('Service terminated: %s' % str(e))
        sys.exit(1)
