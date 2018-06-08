#! /usr/bin/env python
# -*- coding: utf-8 -*-
import time
import db
import flags
from ast import literal_eval
from extension import rpc_client, rc_main, rc_probe
from collections import defaultdict
from utils import format_bitcoin_satoshis as satoshis
from utils import BTC_IN_SATOSHIS, hashin_hex, FEE_PER_BYYE, ONE_DAY, this_day
from tools import bitcoin as btc

FLAGS = flags.FLAGS


class TxProc():
    def __init__(self):
        self.rc_m = rc_main
        self.rc_p = rc_probe
        self.addrs = defaultdict(set)
        self.db = db
    

    def process_tx(self, rawtx):
        
        tx = literal_eval(rawtx)
        tx_hash = tx['hash']

        if self.db.tx_get(tx_hash) or self.rc_m.hashexist("TX_MEMPOOL", tx_hash):
            print "EXISTED_TX: %s" % tx_hash
            return 
        
        try:
            tx_lite, tx_detail = self.parse_transaction(tx)
        except Exception, e:
            print "proces_tx: %s" % str(e)
            return 
        
        self.process_rank(tx_detail)
        
        self.rc_m.hashset("TX_MEMPOOL", {tx_hash: int(time.time())})
        self.rc_m.hashset("UNCONFIRMED_%s" % tx_hash, {'lite': tx_lite, 'detail':tx_detail})
        self.rc_m.set("CURRENT_TX", tx_lite)
        self.rc_m.set_time(tx_hash, tx_lite['time'])
        
        print "NEW_TX: %s" % tx_hash
        #add addr:[tx, ]
        for addr, txs in self.addrs.items():
            self.rc_m.add_list("ADDR_%s" % addr, txs)

        #stat
        mempool = self.rc_m.hashlen("TX_MEMPOOL")
        self.rc_m.set("TX_MEMPOOL_NUM", int(mempool))
        self.rc_m.incrby("TX_MEMPOOL_SIZE", tx_detail['size'])
        #self._probe_conflict(tx)

    def process_rank(self, tx_detail):
        #tx_hash = tx['hash']        
        
        now = this_day(datetime.date.today())
        rec = self.rc_m.get('RANK_RECORD_TIME')
        
        if rec == None: rec = 0
        if now > rec: 
            self.rc_m.delete('RANK_VALUE_OUT')
            self.rc_m.delete('RANK_TX_FEE')
            self.rc_m.delete('RANK_TX_SIZE')
            self.rc_m.set('RANK_RECORD_TIME', now)
            
        #top tx_value  today          
        fee =  tx_detail['fee']
        size = tx_detail['size']
        output = tx_detail['total_output']
        hash = tx_detail['hash']
        tx_time = int(time.time())
                
        outputs = self.rc_m.get('RANK_VALUE_OUT')
        if outputs != None:       
            outputs.append({'tx_hash': hash, 'value_out':output, 'time': tx_time})
            top_list = sorted(outputs, key=lambda d:d['value_out'], reverse=True)[:FLAGS.top_limit]
        else:
            top_list = [{'tx_hash': hash, 'value_out':output, 'time': tx_time}]
        self.rc_m.set("RANK_VALUE_OUT", top_list)
        
        fees = self.rc_m.get('RANK_TX_FEE')    
        if fees != None:    
            fees.append({'tx_hash': hash, 'fee':fee, 'time': tx_time})
            top_list = sorted(outputs, key=lambda d:d['fee'], reverse=True)[:FLAGS.top_limit]
        else:
            top_list = [{'tx_hash': hash, 'fee':fee, 'time': tx_time}]
        self.rc_m.set("RANK_TX_FEE", top_list)
        
        sizes = self.rc_m.get('RANK_TX_SIZE')  
        if sizes != None:     
            sizes.append({'tx_hash': hash, 'size':size, 'time': tx_time})
            top_list = sorted(outputs, key=lambda d:d['size'], reverse=True)[:FLAGS.top_limit]
        else:
            top_list = [{'tx_hash': hash, 'size':fee, 'time': tx_time}]
        self.rc_m.set("RANK_TX_SIZE", top_list)
        
    
    def probe_conflict(self,  tx):
        
        hash = tx['hash']
        
        for v in tx['vin']:
            prev_hash, n = v['prev_output'], v['pos']
            if not btc.is_hash_prefix(prev_hash):
                return
            
            #in db
            if self.db.get_utxo_output(hashin_hex(prev_hash), n):
                self.rc_p.add('CONFLICT_TXS', hash)
                continue
             
            #in mempool     
            if self.rc_p.add_if_no_exist("UTXO_%s_%d" % (prev_hash, n), hash, expire=ONE_DAY):
                self.rc_p.add('CONFLICT_TXS', hash)
                continue
   
   
    def parse_transaction(self, tx):

        tx_hash = tx['hash']
        txin, in_val  = self.__get_vin_detail(tx["vin"], tx_hash)
        txout, out_val = self.__get_vout_detail(tx["vout"], tx_hash)
        
        tx_time = int(time.time())
        tx_lite = {
                 'hash': tx_hash, 
                 'amount': satoshis(int(in_val)), 
                 'time': tx_time, 
                 }
        
        tx_detail = {
               "block_height": -1,
               "fee":     satoshis(int((in_val-out_val))),
               "hash":    tx_hash,
               "inputs":  txin,
               "outputs": txout, 
               "size":    tx['size'],
               "tx_time": tx_time,
               "total_input":  satoshis(int(in_val)),
               "total_output": satoshis(int(out_val)),
               "confirmation": 0,
               }
        
        if self.__filter_dust(tx_detail):
            raise Exception("DUST TX ignored %s " % tx_hash)
        
        return tx_lite, tx_detail
    
    
    ##private 
    def __get_vin_detail(self, tx_vin, tx_hash):
        
        in_val = 0
        vin = []
        for v in tx_vin:
            prev_hash, pos, script = v['prev_output'], v['pos'], v['scriptSig']
            if not btc.is_hash_prefix(prev_hash):
                raise Exception("INVALID TX: %s " % prev_hash)
            
            addr, value = self.__get_txin_info(prev_hash, pos)
            res = {"addr": addr,
                   "amount": satoshis(int(value)),
                   "prev_output": prev_hash,
                   'script': script}
            
            self.addrs[addr].add(tx_hash)
            
            vin.append(res)
            in_val += value
            
        return vin, in_val  


    def __get_vout_detail(self, tx_vout, tx_hash):

        out_val = 0
        vout = []
        
        for v in tx_vout:
            
            value, script= v["amount"], hashin_hex(v["scriptPubKey"])
            ret =  {
                "script":  script,
                "value":   None if value is None else int(value),
            }
            
            btc.export_scriptPubKey(ret, script)
            addr = btc.format_addresses(ret)            
            res = {"addr": addr,
                   "amount": satoshis(int(value)),
                   "redeemed_input": '',
                   "script":  btc.decode_script(script)
                   }
            
            if type(addr) == str and addr != 'Unknown':
                self.addrs[addr].add(tx_hash)

            if type(addr) == list:
                for i in addr:
                    self.addrs[i].add(tx_hash)
                
            vout.append(res)
            out_val += value
            
        return vout, out_val
    
    
    def __get_txin_info(self, prev_hash, pos):
        
        #if in cache
        addr_info = self.rc_m.hashget("UNCONFIRMED_%s" % prev_hash, 'detail')
        if addr_info:
            outputs = addr_info['outputs'][pos]
            return outputs['addr'],  int(float(outputs['amount'])*BTC_IN_SATOSHIS)
        
        #if in db
        res = self.db.pubkey_get_unspent(hashin_hex(prev_hash), pos)
        if res:
            addr = btc.format_bitcoin_address(res['scriptPubkey'], res['pubkey_hash'])
            return addr, int(res['value'])
        else:
            raise Exception("prev_hash:%s pos:%d NOT FOUND" % (prev_hash, pos))
        

    def __filter_dust(self,  tx_info):
        fee, size = tx_info["fee"], tx_info["size"]
        need = FEE_PER_BYYE * size * 0.1 / BTC_IN_SATOSHIS
        return True if fee < need else False 
        
        
        