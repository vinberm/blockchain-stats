
from pysodium import crypto_box_keypair, crypto_scalarmult_curve25519_base
from binascii import hexlify, unhexlify
from tests.node.util import array_to_bytes

# pk, sk = crypto_box_keypair()
# print hexlify(pk), hexlify(sk)
# isinstance(pk, str)
# print type(pk), type(hexlify(pk))


def go_to_python(priv):
    privkey = [int(r) for r in priv.split(' ')]
    hex_pri = array_to_bytes(privkey)
    return hex_pri


def priv_to_pub(priv):
    pub = crypto_scalarmult_curve25519_base(priv)
    return pub


go_priv = "11 151 169 145 3 220 88 104 155 156 176 251 180 25 133 126 87 215 35 49 180 47 124 243 19 215 233 105 199 159 53 46"
go_pub = "192 26 201 94 15 144 185 72 33 51 199 174 184 135 250 97 177 34 252 58 85 168 191 127 42 232 193 149 237 118 175 230"

hex_priv = go_to_python(go_priv)
hex_pub = go_to_python(go_pub)

print hexlify(hex_priv), hexlify(hex_pub)

loc_pub = priv_to_pub(hex_priv)
print hexlify(loc_pub)

