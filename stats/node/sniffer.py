# -*- coding: utf-8 -*-

import logging
import gevent
import socket
import struct
import time
import network
from gevent import Greenlet
from util import *

LOG = logging.getLogger('sniffer')
MIN_PROTO_VERSION = 209

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
        self.last_sent = 0
        self.last_addr = 0
        self.state = "Connecting"

        LOG.debug("Connecting to Node IP #%s:%d" % (self.daddr, self.dport))

        try:
            self.sock.settimeout(self.timeout)
            self.sock.connect((addr, port))
        except:
            self.handle_close()

        # self.sock.settimeout(0)

        self.state = "Connected"
        # stuff version msg into sendbuf
        vt = network.MsgVersion()
        vt.addrTo.ip = self.daddr
        vt.addrTo.port = self.dport
        vt.addrFrom.ip = "0.0.0.0"
        vt.addrFrom.port = 0
        self.send_message(vt, True)

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
        except BaseException:
            self.handle_close()
