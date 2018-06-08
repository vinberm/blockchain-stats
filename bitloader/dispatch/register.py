#! /usr/bin/env python
# -*- coding: utf-8 -*-


apps = {
    'rawblock':{
        'protocol': "tcp://127.0.0.1:28332",
        'topic': 'rawblock',
        'publish': {'type': 'redis', 'host': '127.0.0.1', 'port': 6379, 'db': 0},
    },          
    'hashtx':{
        'protocol': "tcp://127.0.0.1:28332",
        'topic': 'hashtx',
        'publish': {'type': 'redis', 'host': '127.0.0.1', 'port': 6379, 'db': 1},
    },
    'rawtx':{
        'protocol': "tcp://127.0.0.1:28332",
        'topic': 'rawtx',
        'publish': {'type': 'redis', 'host': '127.0.0.1', 'port': 6379, 'db': 1},
    },
    'node':{
        'protocol': "tcp://127.0.0.1:28332",
        'topic': 'node',
        'publish': {'type': 'redis', 'host': '127.0.0.1', 'port': 6379, 'db': 0},
    },
}




