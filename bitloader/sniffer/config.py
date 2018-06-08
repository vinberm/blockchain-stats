import sys


class Config:

    seeds = {'seed.bitcoin.sipa.be':['', 'x1', 'x5', 'x9', 'xd'],
             'dnsseed.bluematt.me':['', 'x9'],
             'dnsseed.bitcoin.dashjr.org':['',],
             'seed.bitcoinstats.com':['','x1','x2','x3','x4','x5','x6','x7','x8','x9','xa','xb','xc','xd','xe','xf'],
             'bitseed.xf2.org':['',],
             'seed.bitcoin.jonasschnelli.ch':['', 'x1', 'x5', 'x9', 'xd'],
             'seed.bitnodes.io':['','x1','x2','x3','x4','x5','x6','x7','x8','x9','xa','xb','xc','xd','xe','xf'],
             }

    rpc_host = '127.0.0.1'
    rpc_port = 8333
    

    zmq_host = '127.0.0.1'
    zmq_port = 28332
    
    MY_VERSION = 31800
    MY_SUBVERSION = ".4"
    
    
    NODES_LIMITS = 2