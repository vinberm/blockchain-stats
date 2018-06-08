# -*- coding: utf-8 -*-

from gevent import monkey; monkey.patch_all()
import gevent
import logging
import json
import threading
import os
import socket
import time
from util import data_dir
from parser import ip_info


mutex = threading.Lock()
LOG = logging.getLogger('node')
TOTAL_GEVENT_TIMEOUT = 60
READ_ADDR_TIMEOUT = 5
LOCK_CONN_TIMEOUT = 2
NODE_STATS_TIMEOUT = 5


def record_to_file(data, filename):
    filepath = os.path.join(os.getcwd(), filename)
    if not os.path.exists('vnode.json'):
        os.system(r'touch {}'.format(filename))
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=4, sort_keys=True)


# path: addrbook.json
def read_addr_book(path):
    mutex.acquire(2)
    with open(path, 'r') as f:
        data = json.load(f)
    mutex.release()
    if data is None:
        return None
    return data['Addrs']


# (ip, port)
def parse_address(path):
    addrs = read_addr_book(path)
    hosts = []
    for item in addrs:
        ip = item['Addr'].get('IP')
        port = item['Addr'].get('Port')
        if ip is None and port is None:
            return None
        hosts.append((ip, port))
    return hosts


def node_conn(host, timeout=1):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(timeout)
    errno = s.connect_ex(host)
    s.close()
    return errno


def get_node_stats():
    filepath = os.path.join(data_dir(), 'addrbook.json')
    print 'filepath: ', filepath
    hosts = parse_address(filepath)
    stats = NodeStats(hosts)
    stats.node_stats(NODE_STATS_TIMEOUT)
    stats.node_position()
    result = {
        "current_node_num": stats.online_num,
        "online_nodes": stats.online_node,
        "node_position": stats.positons,
        "current_time": stats.timestamp
    }
    return result


def loop_stats():
    global timer
    get_node_stats()
    timer = threading.Timer(600, loop_stats)
    timer.start()


class NodeStats:

    def __init__(self, hosts):
        self.hosts = hosts
        self.online_num = 0
        self.online_node = []
        self.time_consume = 0
        self.timestamp = time.time()
        self.positons = []

    def analyze_conn(self, host, timeout):
        if node_conn(host, timeout) == 0:
            mutex.acquire(1)
            self.online_num += 1
            self.online_node.append(host)
            mutex.release()
            print 'Connected: ', host

    def node_stats(self, timeout):
        time_start = time.time()
        jobs = [gevent.spawn(self.analyze_conn, h, timeout) for h in self.hosts]
        gevent.joinall(jobs, timeout=TOTAL_GEVENT_TIMEOUT)
        time_end = time.time()
        self.time_consume = time_end - time_start

    def node_position(self):

        def get_position(h):
            ip, _ = h
            info = ip_info(ip)
            if info is not None:
                mutex.acquire(LOCK_CONN_TIMEOUT)
                self.positons.append(info)
                mutex.release()

        jobs = [gevent.spawn(get_position, node) for node in self.online_node]
        gevent.joinall(jobs, timeout=TOTAL_GEVENT_TIMEOUT)


if __name__ == "__main__":
    status = get_node_stats()
    print 'node num: ', status['current_node_num']
    print 'nodes: ', status['online_nodes']
    # timer = threading.Timer(20, loop_stats)
    # timer.start()
