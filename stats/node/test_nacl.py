# -*- coding: utf-8 -*-

import nacl
from nacl.public import PrivateKey
from binascii import hexlify, unhexlify

go_priv = '1734b0c89db5b9541241cb4a2b421431c01018689f45d28900594fb8e3984462'
a = unhexlify(go_priv)
print 'aaa: ', a, len(a)

skbob = PrivateKey.generate()
pkbob = skbob.public_key
print 'bob:', skbob.__bytes__().encode('hex'), pkbob.__bytes__().encode('hex')


skalice = PrivateKey(a)
print 'alice:', skalice
print 'alice:', hexlify(skalice.__bytes__())
pkalice = skalice.public_key
print 'alice:', pkalice
print 'alice:', hexlify(pkalice.__bytes__()), pkalice.__bytes__().encode('hex')
'''
priv: 1734b0c89db5b9541241cb4a2b421431c01018689f45d28900594fb8e3984462
pub: 05b4547e78a5a4e08cb550f3f2bbd83dfd3edd609ba225e6594f85261f973103
'''

