# -*- coding: utf-8 -*-

# import fcntl
import logging
import json
import gevent
import threading
import os
import socket
from parser import ip_info
from gevent import Greenlet
from gevent import monkey; monkey.patch_all()

mutex = threading.Lock()
LOG = logging.getLogger('node')


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


class NodeConn(Greenlet):

    def __init__(self, addr, port, timeout=1):

        super(NodeConn, self).__init__()

        self.daddr = addr
        self.dport = port
        self.timeout = timeout
        self.sock = gevent.socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.state = "Connecting"

        LOG.debug("Connecting to Node IP #%s:%d" % (self.daddr, self.dport))

        try:
            self.sock.settimeout(self.timeout)
            self.sock.connect((addr, port))
        except:
            self.handle_close()

        self.state = "Connected"

    def handle_close(self):

        LOG.debug("%s closed" % self.daddr)
        try:
            self.sock.close()
        except BaseException:
            pass
        self.state = "Closed"





filename = '/Users/Nov/Library/bytom/addrbook.json'

with open(filename, 'r') as f:
    data = json.load(f)
address = data['Addrs']
print address

hosts = []
for item in address:
    ip = item['Addr']['IP']
    post = item['Addr']['Port']
    print ip, post
    hosts.append((ip, post))


num = 0
valid = []
offline = []
for ip in hosts:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(0.2)
    r = s.connect_ex(ip)
    if r == 0:
        num += 1
        valid.append(ip)
        print 'online node: ', ip
        print 'return value of r: ', r
    else:
        print "Can't connect with the node: %s, %s" % (ip, r)
        offline.append(ip)
        # continue
    s.close()

result = {}
for item in valid:
    ip, port = item
    result[ip] = ip_info(ip)
record_to_file(result, 'vnode.json')

print 'number of online node: ', num
print 'valid node: ', valid
print 'number of online node', len(valid)
print 'number of offline node', len(offline)
print 'total number of node', len(hosts)
print '******************END!!!**********************'
