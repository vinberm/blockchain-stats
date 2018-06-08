import re
from cache import redis_cli

SCRIPT_LIST ={     
"456c696769757300":                 "Eligius",
"2f736c7573682f":                   "Slush",
"736c757368":                       "Slush",
"416e74506f6f6c":                   "AntPool",
"547269706c656d696e696e67":         "TripleMining",
"6e6f64655374726174756d2f":         "BW.COM",
"425720506f6f6c":                   "BW.COM",
"636b706f6f6c":                     "ckpool",
"4b6e434d696e6572":                 "KnCMiner",
"42697446757279":                   "BitFury",
"68756f6269":                       "HuoBi",
"626974636f696e616666696c69617465": "BitcoinAffiliate",
"3862616f6368692e636f6d":           "8BAOCHI",
"42544343":                         "BTCC",
"31686173682e636f6d":               "1HASH",
"48616f425443":                     "HaoBTC",
"e4b883e5bda9e7a59ee4bb99e9b1bc":   "F2Pool",
"566961425443":                     "ViaBTC",
"4254432e434f4d":                   "BTC.COM",
"706f6f6c2e626974636f696e2e636f6d": "Bitcoin.com",
}


def get_relay(script):    
    for pattern in SCRIPT_LIST.keys():
        p = re.compile(pattern)
        if p.search(str(script).encode('hex')):
            return SCRIPT_LIST.get(pattern)
    return 'Unknown'  


def format_bitcoin_satoshis(satoshis):
    decimals = 8
    coin = 10 ** decimals

    if satoshis is None:
        return ''
    if satoshis < 0:
        return '-' + format_bitcoin_satoshis(-satoshis)
    satoshis = int(satoshis)
    integer = satoshis / coin
    frac = satoshis % coin
    return (str(integer) +
            ('.' + (('0' * decimals) + str(frac))[-decimals:])
            .rstrip('0').rstrip('.'))



def notify_block(b, relay, size, fee):
    
    block = {"height": b['height'], 
             "id" : b['block_id'], 
             "relay":  relay, 
             "time": int(b['nTime']), 
             "tx_num": len(b['transactions']), 
             "fee":  format_bitcoin_satoshis(int(fee)),
             "size": size}
    if not redis_cli:
        print "Cannot Connect to redis.... Please check"
        return 
    redis_cli.set('CURRENT_BLOCK', block)
    