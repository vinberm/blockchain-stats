# -*- coding: utf-8 -*-

import socket

s = socket.socket()
host = '45.79.213.28'
port = 46657

s.connect_ex((host, port))
print s.recv(1024).encode('hex')
s.close()
