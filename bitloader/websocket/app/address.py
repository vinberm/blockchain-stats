#! /usr/bin/env python
# -*- coding: utf-8 -*-
from collections import defaultdict
from extension import rc_main as redis_client



class AddrMessage(object):
    
    def __init__(self):
        self.rec_addr = defaultdict(list)
        self.cache = redis_client

    def sub_process(self, cmd, data):
        
       pass