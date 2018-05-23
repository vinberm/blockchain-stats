# -*- coding: utf-8 -*-


from gevent import monkey; monkey.patch_all()
import gevent
import os
from proxy import DbProxy
import socket
import threading
import time
from utils import data_dir, parse_address


mutex = threading.Lock()
TOTAL_GEVENT_TIMEOUT = 60
LOCK_CONN_TIMEOUT = 2
NODE_STATS_TIMEOUT = 5


class NodeStats(object):

    def __init__(self):
        self.hosts = []
        self.online_num = 0
        self.online_node = []
        self.time_lapse = 0
        self.proxy = DbProxy()
        # self.timestamp = time.time()
        # self.positons = []

    def node_conn(self, host, timeout):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(timeout)
        errno = s.connect_ex(host)
        s.close()
        if errno == 0:
            mutex.acquire(LOCK_CONN_TIMEOUT)
            self.online_num += 1
            self.online_node.append(host)
            mutex.release()

    def _connect(self, timeout):
        time_start = time.time()
        jobs = [gevent.spawn(self.node_conn, h, timeout) for h in self.hosts]
        gevent.joinall(jobs, timeout=TOTAL_GEVENT_TIMEOUT)
        time_end = time.time()
        self.time_lapse = time_end - time_start

    def get_node_stats(self):
        filepath = os.path.join(data_dir(), 'addrbook.json')
        self.hosts = parse_address(filepath)
        self._connect(NODE_STATS_TIMEOUT)
        result = {
            "current_node_num": self.online_num,
            "online_nodes": self.online_node,
            "timestamp": time.time(),
            "time_lapse": self.time_lapse
        }
        return result

    def save(self):
        status = self.get_node_stats()
        self.proxy.save_node(status)
