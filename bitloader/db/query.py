#! /usr/bin/env python
# -*- coding: utf-8 -*-

from db.session import *
from exception import DBException

def shutdown():
    session_close()

def startup():
    get_session()

def block_get(block_id):
    try:
        session = get_session()

        sql = """
        SELECT block_height, block_nTime
        FROM 
            block
        WHERE
            block_id = %d
        """  % block_id
        
        cursor = session.execute(sql)
        res = cursor.fetchone()
        return res if res else None
    except DBException, e:
        print "block_get: "+str(e)

def block_get_coinbase_out(block_id):
    try:
        session = get_session()
            
        sql = """
              SELECT 
              SUM(txout_value)
              FROM block_tx bt
              JOIN txout ON (bt.tx_id=txout.tx_id) 
              JOIN chain_candidate cc ON (cc.block_id = bt.block_id)
              WHERE bt.tx_pos=0 
              AND bt.block_id=%d
              """ % int(block_id)
        
        cursor = session.execute(sql);
        value,  = cursor.fetchone()
        return value  
    except Exception,e:
        raise exception.DBError(e)


def block_get_tx(block_id):
    try:
        session = get_session()

        sql = """
        SELECT tx_id 
        FROM 
            block_tx bt
        JOIN chain_candidate cc ON (cc.block_id = bt.block_id)
        WHERE
            cc.in_longest=1
        AND
            cc.block_id = %d
        """  % block_id
        
        cursor = session.execute(sql)
        res = cursor.fetchall()
        return [int(r[0]) for r in res] if res else None
    except DBException, e:
        print "block_get_tx: "+str(e)


def block_get_next_id(block_id):
    try:
        session = get_session()
        if block_id == 0:
            return 1

        sql = """
        SELECT MIN(block_id)
        FROM 
            block
        WHERE
            block_id > %d
        """  % block_id
        
        cursor = session.execute(sql)
        res = cursor.fetchone()
        return  int(res[0]) if res else None
    except DBException, e:
        print "block_get_next_id: "+str(e)    
    
def block_get_last_id():
    try:
        session = get_session()

        sql = """
        SELECT MAX(block_id) 
        FROM 
            block 
        """
        cursor = session.execute(sql)
        res = cursor.fetchone()
        return  int(res[0]) if res else None
    except DBException, e:
        print "block_get_last_id: "+str(e)   


def block_get_coinbase_pubkey(block_id):
    try:
        session = get_session()

        sql = """SELECT pubkey_hash
                FROM txout_detail
                WHERE block_id =%d AND tx_pos = 0        
        """ % int(block_id)
        cursor = session.execute(sql)
        rows = cursor.fetchall()
        return rows
    except Exception,e:
        return None
    
    
def block_get_coinbase_script(block_id):
    try:
        session = get_session()

        sql = """SELECT txin_scriptSig
                FROM txin_detail
                WHERE block_id =%d AND
                tx_pos = 0 AND txin_pos=0
            """ % int(block_id)
        cursor = session.execute(sql)
        (script, ) = cursor.fetchone()
        return script
    except Exception,e:
        return ''


def block_relay_update(relay):
    try:
        session = get_session()

        args = (relay['block_id'], relay['relay'], relay['size'], relay['ntime'], relay['block_fee'])

        sql = """INSERT INTO block_relay
        (block_id, relay, size, ntime, block_fee)
        VALUES (%d, '%s', %d, %d, %d)
        """ % args
        session.execute(sql)
    except Exception,e:
        print str(e)
        print "error in block_miner_update"



def get_txin_info_in_range(tx_ids):
    try:
        session = get_session()            
               
        txs = [str(id) for id in tx_ids]   
        sql = """
        SELECT
            txout.pubkey_id,
            txout.txout_value,
            txin.tx_id,
            b.block_nTime,
            HEX(tx.tx_hash)

        FROM txin
        JOIN txout ON (txin.txout_id = txout.txout_id)
        JOIN block_tx bt ON (txin.tx_id = bt.tx_id)
        JOIN tx ON (tx.tx_id = bt.tx_id)
        JOIN block b ON (b.block_id = bt.block_id)
        JOIN chain_candidate cc ON (cc.block_id = b.block_id)
        WHERE
            txin.tx_id IN (%s)
        AND
            cc.in_longest=1
            """ % (','.join(txs) if len(txs)>1 else txs[0])
        cursor = session.execute(sql)
        res = cursor.fetchall()
        return res
    except DBException, e:
        print "get_txin_info_in_range:"+str(e)
        

def get_txout_info_in_range(tx_ids):
    try:
        session = get_session()            
        
        txs = [str(id) for id in tx_ids]   

        sql = """
        SELECT
            txout.pubkey_id,
            txout.txout_value,
            txout.tx_id,
            b.block_nTime,
            HEX(tx.tx_hash)
        FROM
            txout
        JOIN block_tx bt ON (txout.tx_id = bt.tx_id)
        JOIN tx ON (tx.tx_id = bt.tx_id)
        JOIN block b ON (b.block_id = bt.block_id)
        JOIN chain_candidate cc ON (cc.block_id = b.block_id)
        WHERE
            txout.tx_id IN (%s)
        AND
            cc.in_longest=1
            """ % (','.join(txs) if len(txs)>1 else txs[0])
        cursor = session.execute(sql)
        res = cursor.fetchall()
        return res
    except DBException, e:
        print "get_txout_info_in_range: "+str(e)    


def find_orphan(limit=10):
    try:
        session = get_session()            
        
        info = {}          
        sql = """
        SELECT
            block_id
        FROM
            chain_candidate 
        WHERE 
            in_longest = 0
        ORDER BY block_id DESC 
        LIMIT %d
            """ % limit
            
        cursor = session.execute(sql)
        res = cursor.fetchall()
        
        return [int(r[0]) for r in res] if res else None
    except DBException, e:
        print "find_orphan: "+str(e)  


def get_txin_info_by_blocks(block_ids):
    try:
        session = get_session()            
                  
        sql = """
        SELECT
            txout.pubkey_id,
            txout.txout_value
        FROM txin
        JOIN txout ON (txin.txout_id = txout.txout_id)
        JOIN block_tx bt ON (txin.tx_id = bt.tx_id)
        JOIN block b ON (b.block_id = bt.block_id)
        JOIN chain_candidate cc ON (cc.block_id = b.block_id)
        WHERE
            b.block_id IN (%s)
        AND
            cc.in_longest=0
            """ %  (','.join(block_ids) if len(block_ids)>1 else block_ids[0])
        cursor = session.execute(sql)
        res = cursor.fetchall()
        return res
    except DBException, e:
        print "get_txin_info_by_blocks:"+str(e)

def get_txout_info_by_blocks(block_ids):
    try:
        session = get_session()            
        
        sql = """
        SELECT
            txout.pubkey_id,
            txout.txout_value
        FROM
            txout
        JOIN block_tx bt ON (txout.tx_id = bt.tx_id)
        JOIN tx ON (tx.tx_id = bt.tx_id)
        JOIN block b ON (b.block_id = bt.block_id)
        JOIN chain_candidate cc ON (cc.block_id = b.block_id)
        WHERE
            b.block_id IN (%s)
        AND
            cc.in_longest=0
            """ % (','.join(block_ids) if len(block_ids)>1 else block_ids[0])
        cursor = session.execute(sql)
        res = cursor.fetchall()
        return res
    except DBException, e:
        print "get_txout_info_by_blocks: "+str(e)    



def get_utxo_output(hash, n):
    try:
        session = get_session()            
        
        sql = """
        SELECT  tid.tx_hash 
        FROM txout_detail tod 
        JOIN txin_detail tid ON (tod.txout_id = tid.prevout_id)  
        WHERE tod.tx_hash =:txhash 
        AND tod.txout_pos = %d 
        AND tod.in_longest=1 
        AND tid.in_longest=1
            """ % n
        cursor = session.execute(sql, {'txhash': hash})
        res = cursor.fetchone()
        return res if res is None else res[0]
    
    except Exception, e:
        print "get_utxo_output: "+str(e)   
        
        
def pubkey_get_unspent(prev_hash, pos):
    try:
        session = get_session()            
        
        sql = """
            SELECT pubkey_hash,  txout_value, txout_scriptPubKey
            FROM  txout_detail 
            WHERE tx_hash =:prev_hash  AND txout_pos = %d AND in_longest=1
            """ % int(pos)
        cursor = session.execute(sql, {'prev_hash': prev_hash})
        res = cursor.fetchone()
        return {'pubkey_hash':res[0],'value':int(res[1]),'scriptPubkey':res[2]} if res else None
                
    except DBException, e:
        print "pubkey_get_unspent: "+str(e)
        raise Exception(e)     
    

def tx_get(txhash):
    try:
        session = get_session()    
        sql = """
             SELECT tx_id, tx_version, tx_lockTime, tx_size
              FROM tx
             WHERE tx_hash=UNHEX('%s')
            """ % txhash
        cursor = session.execute(sql)
        recs = cursor.fetchone()
        return recs
    except Exception, e:
        raise exception.DBError(e)


def get_received(pk_id, sid, eid):
    try:
        session = get_session()
        sql = """
                SELECT tx.tx_id, txout.txout_value
                  FROM chain_candidate cc
                  JOIN block b ON (b.block_id = cc.block_id)
                  JOIN block_tx ON (block_tx.block_id = b.block_id)
                  JOIN tx ON (tx.tx_id = block_tx.tx_id)
                  JOIN txout ON (txout.tx_id = tx.tx_id)
                  JOIN pubkey ON (pubkey.pubkey_id = txout.pubkey_id)
                 WHERE pubkey.pubkey_id=%d
                   AND tx.tx_id > %d AND tx.tx_id <= %d
                   AND cc.in_longest = 1
            """ % ( int(pk_id), sid, eid)
        cursor = session.execute(sql)
        return cursor.fetchall()
    except Exception, e:
        print "get_received: "+str(e)


def get_sent(pk_id, sid, eid):
    try:
        session = get_session()

        sql = """
            SELECT tx.tx_id, prevout.txout_value
            FROM chain_candidate cc
              JOIN block b ON (b.block_id = cc.block_id)
              JOIN block_tx ON (block_tx.block_id = b.block_id)
              JOIN tx ON (tx.tx_id = block_tx.tx_id)
              JOIN txin ON (txin.tx_id = tx.tx_id)              
              JOIN txout prevout ON (txin.txout_id = prevout.txout_id)
              JOIN pubkey ON (pubkey.pubkey_id = prevout.pubkey_id)
             WHERE pubkey.pubkey_id = %d
                AND  tx.tx_id > %d AND tx.tx_id <= %d
               AND cc.in_longest = 1
            """ % (int(pk_id), sid, eid)
        cursor = session.execute(sql)
        return cursor.fetchall()
    except Exception, e:
        print "get_sent: "+str(e)


