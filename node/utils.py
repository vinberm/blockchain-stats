# -*- coding: utf-8 -*-

import json
import numpy as np
import os
import platform


def compact_to_big(compact):

    mantissa = compact & 0x007fffffffffffff
    is_negative = (compact & 0x0080000000000000) != 0
    exponent = int(compact >> 56)

    if exponent <= 3:
        mantissa >>= 8 * (3 - exponent)
        bn = np.int64(mantissa)
    else:
        bn = np.int64(mantissa)
        bn <<= 8 * (exponent - 3)

    if is_negative:
        bn = -1 * bn

    return bn


def calc_work(nbit):
    difficultyNum = compact_to_big(nbit)
    if difficultyNum <= 0:
        return 0
    # (1 << 256) / (difficultyNum + 1)
    denominator = difficultyNum + 1
    return (1 << 256) / denominator


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


# path: addrbook.json
def read_addr_book(path):
    with open(path, 'r') as f:
        data = json.load(f)
    if data is None:
        return None
    return data['Addrs']


# (ip, port)
def parse_address(path):
    addrs = read_addr_book(path)
    hosts = []
    for item in addrs:
        ip = item['Addr'].get('IP')
        port = item['Addr'].get('Port')
        if ip is None and port is None:
            return None
        hosts.append((ip, port))
    return hosts


def record_to_file(data, filename):
    filepath = os.path.join(os.getcwd(), filename)
    if not os.path.exists('vnode.json'):
        os.system(r'touch {}'.format(filename))
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=4, sort_keys=True)


if __name__ == '__main__':
    height = 21349
    nbit = 2089670227100065245
    difficult = 1814785054
    nonce = 4434603461217934767

    diff_time = 35

    hashcount = calc_work(nbit)
    print 'hashcount:', hashcount
    hashrate = hashcount / diff_time
    print 'hashrate:', hashrate
    print hex(hashrate)
    print hex(hashrate)[-17: -1]

