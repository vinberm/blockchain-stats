#! /usr/bin/env python
# -*- coding: utf-8 -*-
import sys, os
path = os.path.abspath(os.path.join(os.path.dirname('.'),os.path.pardir))
sys.path.append(path)
import logging
import gevent
import random
from sniffer import PeerManager
from publish import Messager
from config import Config
from dns import resolver
from extension import rc_node as rc

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
    nlist = []
    for node in nodes:
        if not rc.hashexist('CURRENT_NODES', node):
            nlist.append(node)          
    return nlist
    
def clear():
    for node in rc.hashkeys('CURRENT_NODES'):
        if not rc.exists(node):
            rec = rc.hashget('CURRENT_NODES', node)
            rc.hash_incrby("NODES_STAT", 'LOCAL_%s' % rec['location'], -1)
            rc.hash_incrby("NODES_STAT", 'SUBVER_%s' % rec['subver'],  -1)
            rc.hash_incrby("NODES_STAT", 'TOTAL_NODES', -1)
            rc.hashdel('CURRENT_NODES', node)  
    

def process():
    
    threads = []

    #pub = Messager(Config.zmq_host, Config.zmq_port)
    peermgr = PeerManager()
    
    nodes = crawler_nodes(Config.seeds)
    print nodes
    
    if len(nodes) == 0:
        return 
    
    for node in nodes:
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
        LOG.debug('crawler end')      
    
    clear()
    

if __name__ == "__main__":
    try:

        logging.basicConfig(level=logging.DEBUG,
                            format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                            datefmt='%m-%d %H:%M',
                            filename='../logs/nodes.log',
                            filemode='a')
        LOG = logging.getLogger('setup')
        LOG.debug('service started')
        process()

    except Exception, e:
        LOG.error('Service terminated: %s' % str(e))
        sys.exit(1)

