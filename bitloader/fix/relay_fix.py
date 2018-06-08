#! /usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import datetime
import time
import json
import re
import sys
import db
import utils
import Crypto.Hash.SHA256 as SHA256
import requests

START_ID = 410761
END_ID = 414083

DISPLAY_ONLY = False

ONE_DAY = 60 * 60 * 24

HASH160_LIST = {
"c825a1ecf2a6830c4401620c3a16f1995057c2ab":                 "F2Pool",    
"27a1f12771de5cc3b73941664b2537c15316be43":                 "BTC Guild",                    
"80ad90d403581fa3bf46086a91b2d9d4125db6c1":                 "GHash.IO",              
"66589e7031b5bb0a8ed1df0f4a3c273d3cc0f445":                 "CloudHashing",
"4e07c35c92af1bb757a10e9ebcaf27bace73d9b7":                 "EclipseMC",
"afac714e69c4667c3104e4978578069bfcebd7fc":                 "KnCMiner",
"691a2f713369aa828b084ac596470807b3b8b4b1":                 "Polmine",
"5c0e4a6830ff6ea9aea773d75bc207299cd50b74":                 "BitMinter",
"b93dfd929a473f652c7c3e73ed093d60ae6385c3":                 "ASICMiner",
"bfd9c318852ca57a563786e67bb4d0a20b1d8f67":                 "50BTC",
"ea132286328cfc819457b9dec386c4b5c84faa5c":                 "OzCoin",
"c6c500a363006915700742e34ab21921a2923ecf":                 "MegaBigPower",
"695fcf6995ff21de6ddf326749e6e2a32b3a0e64":                 "Address-1AcAj9p",
"7361888c0d575a0e88cd7f36d776536d1bd1512c":                 "Address-1BX5YoL",
"2c30a6aaac6d96687291475d7d52f4b469f665a6":                 "BTCC",
"a09be8040cbf399926aeb1f470c37d1341f3b465":                 "BitFury",
}

SCRIPT_LIST ={     
"456c696769757300": "Eligius",
"2f736c7573682f":   "Slush",
"736c757368": "Slush",
"416e74506f6f6c":   "AntPool",
"547269706c656d696e696e67": "TripleMining",
"6e6f64655374726174756d2f":   "BW.COM",
"425720506f6f6c": "BW.COM",
"54616e67706f6f6c": "TangPool",
"54616e67506f6f6c": "TangPool",
"636b706f6f6c": "ckpool",
"4b6e434d696e6572": "KnCMiner",
"42697446757279": "BitFury",
"68756f6269": "HuoBi",
"626974636f696e616666696c69617465": "BitcoinAffiliate",
"48616f425443": "HaoBTC",
"31686173682e636f6d": "1HASH",
"566961425443":       "ViaBTC",
"4254432e434f4d":     "BTC.COM",
"706f6f6c2e626974636f696e2e636f6d": "Bitcoin.com",
}

BLOCK_API="https://chain.api.btc.com/v3/block/"

def run_schedule():
    
    for id in range(START_ID, END_ID):
        #block_id not existed
        block = db.block_get(id)
        if block == None:
            continue
        height, ntime = block
        coinbase_total_out = db.block_get_coinbase_out(id)
        fee = coinbase_total_out - (5000000000L / (2**(int(height) / 210000)))
        relay = get_relay_by_block_id(id)
            
        res = requests.get(BLOCK_API+str(height))
        size = res.json().get('data').get('size')
        
        br = {"block_id": id, 
              "relay": relay, 
              "size": size,
              "ntime": int(ntime),
              "block_fee": int(fee),
              }
        
        print br
        if not DISPLAY_ONLY: 
            db.block_relay_update(br)           
       
       
def get_relay_by_block_id(block_id):    
    pubkey_hash_list = db.block_get_coinbase_pubkey(block_id)
    for pubkey_hash in pubkey_hash_list:
        hash160 = utils.hashout_hex(pubkey_hash[0]) 
        if hash160 in HASH160_LIST.keys():
            return HASH160_LIST.get(hash160)
    
    script = db.block_get_coinbase_script(block_id)
    for pattern in SCRIPT_LIST.keys():
        p = re.compile(pattern)
        if p.search(utils.hashout_hex(script)):
            return SCRIPT_LIST.get(pattern)
    return 'Unknown'  
    

 

