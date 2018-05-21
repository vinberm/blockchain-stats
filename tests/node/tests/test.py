# -*- coding: utf-8 -*-
import curve25519
from binascii import unhexlify, hexlify


test_priv = "23 52 11 200 157 181 185 84 18 65 203 74 43 66 20 49 12 16 24 104 159 69 210 137 0 89 79 184 227 152 68 98"
test_pub = "45 46 225 90 85 127 120 206 167 222 141 57 113 52 121 207 219 101 153 10 192 133 181 137 131 30 22 183 29 156 93 234"
priv_str = test_priv.split(' ')
pub_str = test_pub.split(' ')
priv_array = [hex(int(s))[2:] for s in priv_str]
pub_array = [hex(int(s))[2:] for s in pub_str]
print 'priv_array', priv_array
print 'pub_array', pub_array

priv = ''
pub = ''
for x in priv_array:
    if len(x) == 2:
        priv += x
    else:
        priv += x + '0'
for x in pub_array:
    if len(x) == 2:
        pub += x
    else:
        pub += x + '0'
print 'priv: ', priv
print 'pub: ', pub

'''
priv = '1734b0c89db5b9541241cb4a2b421431c01018689f45d28900594fb8e3984462'
pub = '2d2ee15a557f78cea7de8d39713479cfdb6599a0c085b589831e16b71d9c5dea'
'''

# test
privs = curve25519.Private()
print 'type:', type(privs.private)
privs.private = unhexlify(priv)
print 'private: ', privs.private

pub = privs.get_public()
print 'python pubkey:', pub.serialize().encode('hex'), hexlify(pub.serialize())

''' 
privkey = '1734b0c89db5b9541241cb4a2b421431c01018689f45d28900594fb8e3984462'
pubkey = '05b4547e78a5a4e08cb550f3f2bbd83dfd3edd609ba225e6594f85261f973103'
'''

# scalarBaseMult
