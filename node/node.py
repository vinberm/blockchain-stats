# -*- coding: utf-8 -*-

import json
import os
import socket


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
for ip in hosts:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(0.1)
    r = s.connect_ex(ip)
    if r == 0:
        num += 1
        valid.append(ip)
        print 'online node: ', ip
        print 'return value of r: ', r
    else:
        print "error-r:", r
        # continue
    s.close()

print 'number of online node: ', num
print 'valid node: ', valid
print '******************END!!!**********************'
