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
    addr = item['Addr']['IP']
    print addr
    hosts.append(addr)

num = 0

# '149.28.23.212:46657'
for ip in hosts:
    s = socket.socket()
    r = s.connect((ip, 46657))
    if r == socket.error:
        continue
    else:
        num += 1
        print 'r', r
    s.close()

print 'num', num
