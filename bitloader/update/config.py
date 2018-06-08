import sys
import gflags

class Config:
        
    BTC_IN_SATOSHIS = 100000000
    TX_RANGE = 5000
    SHARDING_SIZE = 1000
    
    #FLAG
    DEBUG = False
    
    #db collection
    meta_db = "meta"
    bitcoin_db = "bitcoin"
    checkpoint = "checkpoint"
    address_tx = "address_tx"
    address_info = "pubkey_info"
    tx_value = "tx_value"
    
    