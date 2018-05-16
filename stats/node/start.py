# -*- coding: utf-8 -*-


from config import Config
import ed25519
import curve25519
import logging
import socket
from util import *

LOG = logging.getLogger('sniffer')

PexChannel = bytes(0x00)


def gen_ed25519():
    locPrivKey, locPubKey = ed25519.create_keypair()


def shareEphPubKey(s, locEphPub):
    remEphPub = s.recv(1024)
    s.sendall(locEphPub)
    return remEphPub



# 1.seeds
config = Config()
hosts = []
seeds = config.seeds.split(',')

for seed in seeds:
    ip, port = seed.split(':')
    hosts.append((ip, int(port)))
print 'seeds: ', hosts


# 2.try to connect to seeds, and send msg
addr1 = hosts[0]
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.settimeout(5)
s.connect_ex(addr1)


# ed25519
locPrivKey, locPubKey = ed25519.create_keypair()
print locPrivKey.to_ascii(encoding='hex'), locPubKey.to_ascii(encoding='hex')
print locPrivKey.to_bytes().encode('hex'), locPubKey.to_bytes().encode('hex')
print "ed25519: ", len(locPrivKey.to_bytes()), len(locPubKey.to_bytes())

# curve25519
locEphPriv = curve25519.Private()
locEphPub = locEphPriv.get_public()
print locEphPriv.serialize().encode('hex'), locEphPub.serialize().encode('hex')
print "curve25519: ", len(locEphPriv.serialize()), len(locEphPub.serialize())

# 3.从connect中读取对方的curve25519公钥, 计算共享密钥
remEphPub = shareEphPubKey(s, locEphPub.serialize())
print 'remote EphPub: ', remEphPub.encode('hex')

remote_pub = curve25519.Public(remEphPub)
share = locEphPriv.get_shared_key(remote_pub, hashfunc=hashfun)
s = [hex_str_to_int(b) for b in share]
print 'share: ', s
share_key = hsalsa20(s, zeros_in, s, sigma)
print 'share key: ', share_key


loc_pub = [hex_str_to_int(p) for p in locEphPub.serialize()]
rem_pub = [hex_str_to_int(p) for p in remEphPub]

# 4.私钥签名
loEphPub, hiEphPub = sort32(loc_pub, rem_pub)
print 'loEphPub hiEphPub: ', loEphPub, hiEphPub

lo_pub_hex = ''
hi_pub_hex = ''
for lb in loEphPub:
    lo_pub_hex += int_to_hex_str(lb)
for hb in hiEphPub:
    hi_pub_hex += int_to_hex_str(hb)
print lo_pub_hex, hi_pub_hex
challenge = sha256(lo_pub_hex+hi_pub_hex)
print 'challenge', challenge.encode('hex')

