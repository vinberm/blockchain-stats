#! /usr/bin/env python
# -*- coding: utf-8 -*-

import re
import base58
import deserialize
import Crypto.Hash.SHA256 as SHA256
import util

try:
    import Crypto.Hash.RIPEMD160 as RIPEMD160
except:
    import ripemd_via_hashlib as RIPEMD160


DEFAULT_DECIMALS = 8
HIGIHEST_TARGET = 0x00000000FFFF0000000000000000000000000000000000000000000000000000

def identity(x):
    return x

def rev(x):
    return None if x is None else x[::-1]
def to_hex(x):
    return None if x is None else str(x).encode('hex')
def from_hex(x):
    return None if x is None else x.decode('hex')
def to_hex_rev(x):
    return None if x is None else str(x)[::-1].encode('hex')
def from_hex_rev(x):
    return None if x is None else x.decode('hex')[::-1]


binin       = identity
binin_hex   = from_hex
binout      = identity
binout_hex  = to_hex
hashin      = rev
hashin_hex  = from_hex
hashout     = rev
hashout_hex = to_hex


def binout_int(x):
    if x is None:
        return None
    return int(binout_hex(x), 16)

def binin_int(x, bits):
    if x is None:
        return None
    return binin_hex(("%%0%dx" % (bits / 4)) % x)

def format_satoshis(satoshis, chain):
    decimals = DEFAULT_DECIMALS if chain['decimals'] is None else chain['decimals']
    coin = 10 ** decimals

    if satoshis is None:
        return ''
    if satoshis < 0:
        return '-' + format_satoshis(-satoshis, chain)
    satoshis = int(satoshis)
    integer = satoshis / coin
    frac = satoshis % coin
    return (str(integer) +
            ('.' + (('0' * decimals) + str(frac))[-decimals:])
            .rstrip('0').rstrip('.'))
    

def format_bitcoin_satoshis(satoshis):
    decimals = DEFAULT_DECIMALS
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




def format_time(nTime):
    import time
    return time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(int(nTime)))


def format_difficulty(diff):
    idiff = int(diff)
    ret = '.%03d' % (int(round((diff - idiff) * 1000)),)
    while idiff > 999:
        ret = (' %03d' % (idiff % 1000,)) + ret
        idiff = idiff / 1000
    return str(idiff) + ret


def work_to_difficulty(work):
    return work * HIGIHEST_TARGET * 1000 / (1 << 256) / 1000.0

def calculate_target(nBits):
    return (nBits & 0xffffff) << (8 * ((nBits >> 24) - 3))

def target_to_difficulty(target):
    #return ((1 << 224) - 1) * 1000 / (target + 1) / 1000.0
    return (HIGIHEST_TARGET) * 1000 / (target + 1) / 1000.0

def calculate_difficulty(nBits):
    return target_to_difficulty(calculate_target(nBits))

def hash_to_address(version, hash):
    vh = version + hash
    return base58.b58encode(vh + double_sha256(vh)[:4])

def double_sha256(s):
    return SHA256.new(SHA256.new(s).digest()).digest()

ADDRESS_RE = re.compile('[1-9A-HJ-NP-Za-km-z]{26,}\\Z')
def possible_address(string):
    return ADDRESS_RE.match(string)

HASH_PREFIX_RE = re.compile('[0-9a-fA-F]{64}\\Z')
HASH_PREFIX_MIN = 64
def is_hash_prefix(s):
    return HASH_PREFIX_RE.match(s) and len(s) == HASH_PREFIX_MIN


def is_address_version(v):
    return len(v) == 1


HASH_160_PREFIX_RE = re.compile('[0-9a-f]{40}\\Z')
HASH_160_LEN = 40
def possible_hash160(s):
    return HASH_160_PREFIX_RE.match(s) and len(s)==HASH_160_LEN
    
def decode_address(addr):
    bytes = base58.b58decode(addr, None)
    if len(bytes) < 25:
        bytes = ('\0' * (25 - len(bytes))) + bytes
    return bytes[:-24], bytes[-24:-4]


def decode_script(script):
    if script is None:
        return ''
    try:
        return deserialize.decode_script(script)
    except KeyError, e:
        return 'Nonstandard script'
    

def decode_check_address(address):
    if possible_address(address):
        version, hash = decode_address(address)
        if hash_to_address(version, hash) == address:
            return version, hash
    return None, None


def address_to_hash_version(addr):
    version, binaddr = decode_check_address(addr)
    if binaddr is None:
        raise"Invalid address format"
    dbhash = binin(binaddr)
    return version, dbhash

PUBKEY_HASH_LENGTH = 20
MAX_MULTISIG_KEYS = 3

# Template to match a pubkey hash ("Bitcoin address transaction") in
# txout_scriptPubKey.  OP_PUSHDATA4 matches any data push.
SCRIPT_ADDRESS_TEMPLATE = [
    deserialize.opcodes.OP_DUP, 
    deserialize.opcodes.OP_HASH160, 
    deserialize.opcodes.OP_PUSHDATA4, 
    deserialize.opcodes.OP_EQUALVERIFY, 
    deserialize.opcodes.OP_CHECKSIG ]

# Template to match a pubkey ("IP address transaction") in txout_scriptPubKey.
SCRIPT_PUBKEY_TEMPLATE = [ deserialize.opcodes.OP_PUSHDATA4, deserialize.opcodes.OP_CHECKSIG ]

# Template to match a BIP16 pay-to-script-hash (P2SH) output script.
SCRIPT_P2SH_TEMPLATE = [ deserialize.opcodes.OP_HASH160, PUBKEY_HASH_LENGTH, deserialize.opcodes.OP_EQUAL ]

# Template to match a script that can never be redeemed, used in Namecoin.
SCRIPT_BURN_TEMPLATE = [deserialize.opcodes.OP_RETURN ]

SCRIPT_TYPE_INVALID = 0
SCRIPT_TYPE_UNKNOWN = 1
SCRIPT_TYPE_PUBKEY = 2
SCRIPT_TYPE_ADDRESS = 3
SCRIPT_TYPE_BURN = 4
SCRIPT_TYPE_MULTISIG = 5
SCRIPT_TYPE_P2SH = 6

NULL_HASH = "\0" * 32
GENESIS_HASH_PREV = NULL_HASH

NULL_PUBKEY_HASH = "\0" * 20
NULL_PUBKEY_ID = 0
PUBKEY_ID_NETWORK_FEE = NULL_PUBKEY_ID


def parse_txout_script(script):
    """
    Return TYPE, DATA where the format of DATA depends on TYPE.

    * SCRIPT_TYPE_INVALID  - DATA is the raw script
    * SCRIPT_TYPE_UNKNOWN  - DATA is the decoded script
    * SCRIPT_TYPE_PUBKEY   - DATA is the binary public key
    * SCRIPT_TYPE_ADDRESS  - DATA is the binary public key hash
    * SCRIPT_TYPE_BURN     - DATA is None
    * SCRIPT_TYPE_MULTISIG - DATA is {"m":M, "pubkeys":list_of_pubkeys}
    * SCRIPT_TYPE_P2SH     - DATA is the binary script hash
    """
    if script is None:
        raise ValueError()
    try:
        decoded = [ x for x in deserialize.script_GetOp(script) ]
    except Exception:
        return SCRIPT_TYPE_INVALID, script
    return parse_decoded_txout_script(decoded)

def parse_decoded_txout_script(decoded):
    if deserialize.match_decoded(decoded, SCRIPT_ADDRESS_TEMPLATE):
        pubkey_hash = decoded[2][1]
        if len(pubkey_hash) == PUBKEY_HASH_LENGTH:
            return SCRIPT_TYPE_ADDRESS, pubkey_hash

    elif deserialize.match_decoded(decoded, SCRIPT_PUBKEY_TEMPLATE):
        pubkey = decoded[0][1]
        return SCRIPT_TYPE_PUBKEY, pubkey

    elif deserialize.match_decoded(decoded, SCRIPT_P2SH_TEMPLATE):
        script_hash = decoded[1][1]
        assert len(script_hash) == PUBKEY_HASH_LENGTH
        return SCRIPT_TYPE_P2SH, script_hash

    elif deserialize.match_decoded(decoded, SCRIPT_BURN_TEMPLATE):
        return SCRIPT_TYPE_BURN, None

    elif len(decoded) >= 4 and decoded[-1][0] == deserialize.opcodes.OP_CHECKMULTISIG:
        # cf. bitcoin/src/script.cpp:Solver
        n = decoded[-2][0] + 1 - deserialize.opcodes.OP_1
        m = decoded[0][0] + 1 - deserialize.opcodes.OP_1
        if 1 <= m <= n <= MAX_MULTISIG_KEYS and len(decoded) == 3 + n and \
                all([ decoded[i][0] <= deserialize.opcodes.OP_PUSHDATA4 for i in range(1, 1+n) ]):
            return SCRIPT_TYPE_MULTISIG, \
                { "m": m, "pubkeys": [ decoded[i][1] for i in range(1, 1+n) ] }

    # Namecoin overrides this to accept name operations.
    return SCRIPT_TYPE_UNKNOWN, decoded


def format_addresses(data):
    chain ={'address_version': '00'.decode('hex'),
            'script_addr_vers': '05'.decode('hex') }
    
    if data['binaddr'] is None:
        return 'Unknown'
    if data['binaddr'] == NULL_PUBKEY_HASH and data.get('script_type')==SCRIPT_TYPE_ADDRESS:   
        return '1111111111111111111114oLvT2'    
    if data['binaddr'] == NULL_PUBKEY_HASH:
        return 'Unknown'
    
    if 'subbinaddr' in data:
        # Multisig or known P2SH.
        ret = []
        script_address = hash_to_address(chain['script_addr_vers'], data['binaddr'])
        for binaddr in data['subbinaddr']:
            ret.append(hash_to_address(data['address_version'], binaddr))
        return ret
    else:
        return hash_to_address(data['address_version'], data['binaddr'])


def export_scriptPubKey(txout, scriptPubKey):  
    """In txout, set script_type, address_version, binaddr, and for multisig, required_signatures."""   
    chain ={'address_version': '00'.decode('hex'),
            'script_addr_vers': '05'.decode('hex') }

    if scriptPubKey is None:
        txout['script_type'] = None
        txout['binaddr'] = None
        return

    script_type, data = parse_txout_script(scriptPubKey)
    txout['script_type'] = script_type
    txout['address_version'] = chain['address_version']

    if script_type ==  SCRIPT_TYPE_PUBKEY:
        txout['binaddr'] = util.pubkey_to_hash(data)
    elif script_type == SCRIPT_TYPE_ADDRESS:
        txout['binaddr'] = data
    elif script_type == SCRIPT_TYPE_P2SH:       
        txout['address_version'] = chain['script_addr_vers']
        txout['binaddr'] = data
    elif script_type == SCRIPT_TYPE_MULTISIG:
        txout['required_signatures'] = data['m']
        txout['binaddr'] = util.pubkey_to_hash(scriptPubKey)
        txout['subbinaddr'] = [
                util.pubkey_to_hash(pubkey)
                for pubkey in data['pubkeys']
                ]
    elif script_type == SCRIPT_TYPE_BURN:
        txout['binaddr'] = NULL_PUBKEY_HASH
    else:
        txout['binaddr'] = None


def format_bitcoin_address(script, pubkey_hash):
    type, data = parse_txout_script(script)    
    version = '00'
    if type == SCRIPT_TYPE_INVALID:
        raise ValueError()
    elif type == SCRIPT_TYPE_P2SH:
        version = '05'
    version = version.decode('hex')
    return hash_to_address(version, pubkey_hash) 




###DECODE RAW TX
def parse_transaction(vds,  ntime=False):
    d = {}
    start_pos = vds.read_cursor
    d['version'] = vds.read_int32()
    if ntime:
        d['nTime'] = vds.read_uint32()
    
    n_vin = vds.read_compact_size()
    d['txin'] = []
    for i in xrange(n_vin):
        d['txin'].append(parse_txin(vds))
    
    n_vout = vds.read_compact_size()
    d['txout'] = []
    
    for i in xrange(n_vout):
        d['txout'].append(parse_txout(vds))
        
    d['lockTime'] = vds.read_uint32()
    d['raw_data'] =hashout_hex(vds.input[start_pos:vds.read_cursor])
    return d


def parse_txin(vds):
  d = {}
  d['txid'] = hashout_hex(vds.read_bytes(32))
  d['vout'] = vds.read_uint32()
  d['scriptSig'] = hashout_hex(vds.read_bytes(vds.read_compact_size()))
  d['sequence'] = int(vds.read_uint32())
  return d   

def parse_txout(vds):
  d = {}
  d['value'] = int(vds.read_int64())
  d['scriptPubKey'] = hashout_hex(vds.read_bytes(vds.read_compact_size()))
  return d

    