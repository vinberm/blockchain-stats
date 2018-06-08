#!/usr/bin/python
#
# sniffer.py - Bitcoin P2P Network Sniffer
# https://github.com/sebicas/bitcoin-sniffer by @sebicas
#
# This is a Fork of pynode mininode from jgarzik ( https://github.com/jgarzik/pynode )
# But since his version is a little know branch with in pynode I dedided to keep my
# Fork but contribute my changes to his repository.
#
# Distributed under the MIT/X11 software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.

import struct
import socket
import binascii
import time
import sys
import re
import json
import logging
import cStringIO
import hashlib
import network
import gevent
from IPy import IP
from gevent import Greenlet
from config import Config
from util import *
from gevent import monkey; monkey.patch_all()
from extension import geoip_loc as geo, rc_node as rc


MIN_PROTO_VERSION = 209

LOG = logging.getLogger('sniffer')

class PeerManager(object):
    def __init__(self, pub=None):
        self.pub = pub
        self.peers = []
        self.addrs = {}
        self.tried = {}

    def add(self, host, port):
        LOG.debug("PeerManager: connecting to %s:%d" % (host, port))
        self.tried[host] = True
        c = NodeConn(self.pub, host, port)
        self.peers.append(c)
        return c

    def close_all(self):
        for peer in self.peers:
            peer.handle_close()
        self.peers = []


class NodeConn(Greenlet):
    
    def __init__(self, pub, addr, port, timeout=1):
        
        super(NodeConn, self).__init__()
        
        self.daddr = addr
        self.dport = port
        self.publish = pub
        self.timeout = timeout
        self.sock = gevent.socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.recvbuf = ""
        self.ver_send = MIN_PROTO_VERSION #209
        self.ver_recv = MIN_PROTO_VERSION #209
        self.last_sent = 0
        self.last_addr = 0
        self.state = "Connecting"
        
        LOG.debug("Connecting to Node IP #%s:%d" % (self.daddr, self.dport))
        
        try:
            self.sock.settimeout(self.timeout)
            self.sock.connect((addr, port))
        except:
            self.handle_close()
        
        #self.sock.settimeout(0)

        self.state = "Connected"
        #stuff version msg into sendbuf
        vt = network.msg_version()
        vt.addrTo.ip = self.daddr
        vt.addrTo.port = self.dport
        vt.addrFrom.ip = "0.0.0.0"
        vt.addrFrom.port = 0
        self.send_message(vt, True)
    
    
    def _run(self):
        LOG.debug("%s connected" % self.daddr)
        
        while True:
            try:
                t = self.sock.recv(8192)
                if len(t) <= 0: raise ValueError
            except (IOError, ValueError):
                self.handle_close()
                return
            self.recvbuf += t
            finished = self.got_data()
            if finished: 
                return 

                
    def handle_close(self):
        
        LOG.debug("%s closed" % self.daddr)
        self.recvbuf = ""
        self.sendbuf = ""

        try:
            self.sock.shutdown(socket.SHUT_RDWR)
            self.close()
        except:
            pass
        self.state = "Closed"
    
    def got_data(self):
        while True:
            if len(self.recvbuf) < 4:
                return
            if self.recvbuf[:4] != "\xf9\xbe\xb4\xd9":
                raise ValueError("got garbage %s" % repr(self.recvbuf))
            if self.ver_recv < MIN_PROTO_VERSION:
                if len(self.recvbuf) < 4 + 12 + 4:
                    return
                command = self.recvbuf[4:4+12].split("\x00", 1)[0]
                msglen = struct.unpack("<i", self.recvbuf[4+12:4+12+4])[0]
                checksum = None
                if len(self.recvbuf) < 4 + 12 + 4 + msglen:
                    return
                msg = self.recvbuf[4+12+4:4+12+4+msglen]
                self.recvbuf = self.recvbuf[4+12+4+msglen:]
            else:
                if len(self.recvbuf) < 4 + 12 + 4 + 4:
                    return
                command = self.recvbuf[4:4+12].split("\x00", 1)[0]
                msglen = struct.unpack("<i", self.recvbuf[4+12:4+12+4])[0]
                checksum = self.recvbuf[4+12+4:4+12+4+4]
                if len(self.recvbuf) < 4 + 12 + 4 + 4 + msglen:
                    return
                msg = self.recvbuf[4+12+4+4:4+12+4+4+msglen]
                th = sha256(msg)
                h = sha256(th)
                if checksum != h[:4]:
                    raise ValueError("got bad checksum %s" % repr(self.recvbuf))
                self.recvbuf = self.recvbuf[4+12+4+4+msglen:]
            if command in network.messagemap:
                f = cStringIO.StringIO(msg)
                t = network.messagemap[command]()
                t.deserialize(f)
                res = self.got_message(t)
                if res: return True
            else:
                LOG.error("Unknown command: '" + command + "' " + repr(msg))
    
    
    def send_message(self, message, pushbuf=False):
        if self.state != "Connected" and not pushbuf:
            return
        LOG.info("Send %s" % repr(message))
        command = message.command
        data = message.serialize()
        tmsg = "\xf9\xbe\xb4\xd9"
        tmsg += command
        tmsg += "\x00" * (12 - len(command))
        tmsg += struct.pack("<I", len(data))
        if self.ver_send >= MIN_PROTO_VERSION:
            th = sha256(data)
            h = sha256(th)
            tmsg += h[:4]
        tmsg += data
    
        try:
            self.sock.sendall(tmsg)
            self.last_sent = time.time()
        except:
            self.handle_close()
    
    def got_message(self, message):
        if self.last_sent + 30 * 60 < time.time():
            self.send_message(network.msg_ping())
        
        if self.last_addr + 3 * 60 < time.time():
            self.send_message(network.msg_getaddr())
            self.last_addr = time.time()
        
        LOG.debug("Recv %s" % repr(message))
        
        if message.command  == "version":
            if message.nVersion >= MIN_PROTO_VERSION:
                self.send_message(network.msg_verack())
            self.ver_send = min(Config.MY_VERSION, message.nVersion)
            if message.nVersion < MIN_PROTO_VERSION:
                self.ver_recv = self.ver_send
            
            self.notify_version(message)
            return True
            
        elif message.command == "verack":
            self.ver_recv = self.ver_send

    
    def notify_version(self, message):
        
        ver = message.nVersion
        ntime = message.nTime
        ip, port = message.addrFrom.ip, message.addrFrom.port
        subver = message.strSubVer
        ns_height = message.nStartingHeight
        
        loc = geo.get_country(ip)
        if not loc: loc = 'Unknown'
        rec = { "version": ver, 
                "ntime": ntime,  
                "port": port, 
                "subver": subver,  
                "ns_height": ns_height, 
                "location": loc}
            
        if ip not in IP('0.0.0.0/23'):
            if not rc.exists(ip):
                rc.hash_incrby("NODES_STAT", 'LOCAL_%s' % loc, 1)
                rc.hash_incrby("NODES_STAT", 'SUBVER_%s' % subver, 1)
                rc.hash_incrby("NODES_STAT", 'TOTAL_NODES', 1)
                rc.hashset('CURRENT_NODES', {ip: str(rec)})
            rc.set(ip, 1, expire=Config.VERSION_EXPIRE)


        
