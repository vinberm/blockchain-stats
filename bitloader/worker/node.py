#! /usr/bin/env python
# -*- coding: utf-8 -*-

from extension import rc_main, geoip_loc
import time
from utils import DEFAULT_PORT


class NodeProc():
    def __init__(self):
        self.rc_m = rc_main
        self.loc = geoip_loc
            
    def send_node(self, node_str):
        node_list = eval(node_str)

        nodes = set()
        for node in node_list:
            ip, port = node
            loc = self._get_ip_location(ip)
            if not loc: continue
            if int(port) == DEFAULT_PORT:
                rec = "{0}:{1}:{2}".format(ip, port, loc)
                nodes.add(rec)

        if len(nodes) > 0:
            self.rc_m.add_list("CURRENT_NODES", nodes)
           
    ##private 
    def _get_ip_location(self, ip):
        return self.loc.get_country(ip)

