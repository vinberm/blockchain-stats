#! /usr/bin/env python
# -*- coding: utf-8 -*-

import db
from extension import mongodb_cli
from collections import defaultdict

SID = 0
EID =  9999999999999
SIZE = 50000


def address_info_fix(pk_id):
    sent = db.get_sent(pk_id, SID, EID)
    recv = db.get_received(pk_id, SID, EID)

    txout = len(sent) if sent else 0
    txin = len(recv) if recv else 0
    tx_dict = defaultdict(int)
    balance = 0
    last_sent = 0
    last_recv = 0
    first = 999999999999
    for s in sent:
        tx_id, value = s
        tx_dict[int(tx_id)] -= int(value)
        balance -= int(value)
        last_sent = max(last_sent, tx_id)
        first = min(first, tx_id)
    for r in recv:
        tx_id, value = r
        tx_dict[tx_id] += int(value)
        balance += int(value)
        last_recv = max(last_recv, tx_id)
        first = min(first, tx_id)

    recv = sum(v for v in tx_dict.values() if v > 0)
    sent = sum(v for v in tx_dict.values() if v < 0)
    txcounts = len(tx_dict.keys())

    print "###", pk_id, balance, txcounts, txin, txout, int(recv), int(first), int(last_sent), int(last_recv)

    return {'balance': balance,
            'txcounts': txcounts,
            'txin': txin,
            'txout': txout,
            'receive': int(recv),
            'first_txid': int(first),
            'last_sent_txid': int(last_sent),
            'last_recv_txid': int(last_recv)}


def run_schedule(file):
    f = open(file, 'r')
    mongodb_cli.use_db('bitcoin')
    for line in f.readlines():
        pk_id = int(line.strip())
        addr_info = address_info_fix(pk_id)
        mongodb_cli.update_address_info('pubkey_info', pk_id, addr_info)
        #print addr_info
                                               