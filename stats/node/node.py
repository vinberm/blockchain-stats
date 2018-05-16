# -*- coding: utf-8 -*-

import json
import os
import socket
from parser import ip_info


def record_to_file(data, filename):
    filepath = os.path.join(os.getcwd(), filename)
    if not os.path.exists('vnode.json'):
        os.system(r'touch {}'.format(filename))
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=4, sort_keys=True)


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
