# -*- coding: utf-8 -*-

import hashlib
import platform
import os
from numpy import uint32, uint8


def hex_str_to_int(s):
    return int(s.encode('hex'), 16)


def int_to_hex_str(i):
    return hex(i)[2:]


def sort32(a, b):
    if a < b:
        lo, hi = a, b
    else:
        lo, hi = b, a
    return lo, hi


def data_dir():
    home_dir = os.environ['HOME']
    sysstr = platform.system()
    if sysstr == 'Darwin':
        path = os.path.join(home_dir, "Library", "Bytom")
    elif sysstr == 'Windows':
        path = os.path.join(home_dir, "AppData", "Roaming", "Bytom")
    else:
        path = os.path.join(home_dir, ".bytom")
    return path




_sigma = ['e', 'x', 'p', 'a', 'n', 'd', ' ', '3', '2', '-', 'b', 'y', 't', 'e', ' ', 'k']
# sigma = b"expand 32-byte k".decode('ascii')
sigma = []
for v in _sigma:
    sigma.append(hex_str_to_int(v))
print sigma

zeros_in = [0] * 16


def sha256(s):
    return hashlib.new('sha256', s).digest()


def hash256(s):
    return sha256(sha256(s))


def hashfun(s):
    return s


def hsalsa20(out, oin, k, c):
    x0 = uint32(c[0]) | uint32(c[1]) << 8 | uint32(c[2]) << 16 | uint32(c[3]) << 24
    x1 = uint32(k[0]) | uint32(k[1]) << 8 | uint32(k[2]) << 16 | uint32(k[3]) << 24
    x2 = uint32(k[4]) | uint32(k[5]) << 8 | uint32(k[6]) << 16 | uint32(k[7]) << 24
    x3 = uint32(k[8]) | uint32(k[9]) << 8 | uint32(k[10]) << 16 | uint32(k[11]) << 24
    x4 = uint32(k[12]) | uint32(k[13]) << 8 | uint32(k[14]) << 16 | uint32(k[15]) << 24
    x5 = uint32(c[4]) | uint32(c[5]) << 8 | uint32(c[6]) << 16 | uint32(c[7]) << 24
    x6 = uint32(oin[0]) | uint32(oin[1]) << 8 | uint32(oin[2]) << 16 | uint32(oin[3]) << 24
    x7 = uint32(oin[4]) | uint32(oin[5]) << 8 | uint32(oin[6]) << 16 | uint32(oin[7]) << 24
    x8 = uint32(oin[8]) | uint32(oin[9]) << 8 | uint32(oin[10]) << 16 | uint32(oin[11]) << 24
    x9 = uint32(oin[12]) | uint32(oin[13]) << 8 | uint32(oin[14]) << 16 | uint32(oin[15]) << 24
    x10 = uint32(c[8]) | uint32(c[9]) << 8 | uint32(c[10]) << 16 | uint32(c[11]) << 24
    x11 = uint32(k[16]) | uint32(k[17]) << 8 | uint32(k[18]) << 16 | uint32(k[19]) << 24
    x12 = uint32(k[20]) | uint32(k[21]) << 8 | uint32(k[22]) << 16 | uint32(k[23]) << 24
    x13 = uint32(k[24]) | uint32(k[25]) << 8 | uint32(k[26]) << 16 | uint32(k[27]) << 24
    x14 = uint32(k[28]) | uint32(k[29]) << 8 | uint32(k[30]) << 16 | uint32(k[31]) << 24
    x15 = uint32(c[12]) | uint32(c[13]) << 8 | uint32(c[14]) << 16 | uint32(c[15]) << 24

    for i in range(0, 20, 2):
        u = uint32(x0 + x12)
        x4 ^= (u << 7 | u >> (32 - 7))
        u = uint32(x4 + x0)
        x8 ^= (u << 9 | u >> (32 - 9))
        u = uint32(x8 + x4)
        x12 ^= (u << 13 | u >> (32 - 13))
        u = uint32(x12 + x8)
        x0 ^= (u << 18 | u >> (32 - 18))

        u = uint32(x5 + x1)
        x9 ^= (u << 7 | u >> (32 - 7))
        u = uint32(x9 + x5)
        x13 ^= (u << 9 | u >> (32 - 9))
        u = uint32(x13 + x9)
        x1 ^= (u << 13 | u >> (32 - 13))
        u = uint32(x1 + x13)
        x5 ^= (u << 18 | u >> (32 - 18))

        u = uint32(x10 + x6)
        x14 ^= (u << 7 | u >> (32 - 7))
        u = uint32(x14 + x10)
        x2 ^= (u << 9 | u >> (32 - 9))
        u = uint32(x2 + x14)
        x6 ^= (u << 13 | u >> (32 - 13))
        u = uint32(x6 + x2)
        x10 ^= (u << 18 | u >> (32 - 18))

        u = uint32(x15 + x11)
        x3 ^= (u << 7 | u >> (32 - 7))
        u = uint32(x3 + x15)
        x7 ^= (u << 9 | u >> (32 - 9))
        u = uint32(x7 + x3)
        x11 ^= (u << 13 | u >> (32 - 13))
        u = uint32(x11 + x7)
        x15 ^= (u << 18 | u >> (32 - 18))

        u = uint32(x0 + x3)
        x1 ^= (u << 7 | u >> (32 - 7))
        u = uint32(x1 + x0)
        x2 ^= (u << 9 | u >> (32 - 9))
        u = uint32(x2 + x1)
        x3 ^= (u << 13 | u >> (32 - 13))
        u = uint32(x3 + x2)
        x0 ^= (u << 18 | u >> (32 - 18))

        u = uint32(x5 + x4)
        x6 ^= (u << 7 | u >> (32 - 7))
        u = uint32(x6 + x5)
        x7 ^= (u << 9 | u >> (32 - 9))
        u = uint32(x7 + x6)
        x4 ^= (u << 13 | u >> (32 - 13))
        u = uint32(x4 + x7)
        x5 ^= (u << 18 | u >> (32 - 18))

        u = uint32(x10 + x9)
        x11 ^= (u << 7 | u >> (32 - 7))
        u = uint32(x11 + x10)
        x8 ^= (u << 9 | u >> (32 - 9))
        u = uint32(x8 + x11)
        x9 ^= (u << 13 | u >> (32 - 13))
        u = uint32(x9 + x8)
        x10 ^= (u << 18 | u >> (32 - 18))

        u = uint32(x15 + x14)
        x12 ^= (u << 7 | u >> (32 - 7))
        u = uint32(x12 + x15)
        x13 ^= (u << 9 | u >> (32 - 9))
        u = uint32(x13 + x12)
        x14 ^= (u << 13 | u >> (32 - 13))
        u = uint32(x14 + x13)
        x15 ^= (u << 18 | u >> (32 - 18))

    out[0] = uint8(x0)
    out[1] = uint8(x0 >> 8)
    out[2] = uint8(x0 >> 16)
    out[3] = uint8(x0 >> 24)

    out[4] = uint8(x5)
    out[5] = uint8(x5 >> 8)
    out[6] = uint8(x5 >> 16)
    out[7] = uint8(x5 >> 24)

    out[8] = uint8(x10)
    out[9] = uint8(x10 >> 8)
    out[10] = uint8(x10 >> 16)
    out[11] = uint8(x10 >> 24)

    out[12] = uint8(x15)
    out[13] = uint8(x15 >> 8)
    out[14] = uint8(x15 >> 16)
    out[15] = uint8(x15 >> 24)

    out[16] = uint8(x6)
    out[17] = uint8(x6 >> 8)
    out[18] = uint8(x6 >> 16)
    out[19] = uint8(x6 >> 24)

    out[20] = uint8(x7)
    out[21] = uint8(x7 >> 8)
    out[22] = uint8(x7 >> 16)
    out[23] = uint8(x7 >> 24)

    out[24] = uint8(x8)
    out[25] = uint8(x8 >> 8)
    out[26] = uint8(x8 >> 16)
    out[27] = uint8(x8 >> 24)

    out[28] = uint8(x9)
    out[29] = uint8(x9 >> 8)
    out[30] = uint8(x9 >> 16)
    out[31] = uint8(x9 >> 24)

    return out
