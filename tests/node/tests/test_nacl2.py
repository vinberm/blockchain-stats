# -*- coding: utf-8 -*-


from pysodium import crypto_box_keypair
from binascii import hexlify


pk, sk = crypto_box_keypair()

print hexlify(pk), hexlify(sk)
print pk.encode('hex'), sk.encode('hex')
