#! /usr/bin/env python
# -*- coding: utf-8 -*-

from exception import DBException
from db.session import *
from loader import util

def new_id(key):
    try:
        session = get_session()
        sql = """INSERT INTO %s_seq () VALUES () """  % key
        cursor = session.execute(sql)
        
        cursor =  session.execute("SELECT LAST_INSERT_ID()")
        (ret, ) = cursor.fetchone()
        if ret % 1000 == 0:
            session.execute("DELETE FROM %s_seq WHERE id < %d" % (key, ret))
        return ret
    
    except DBException,e:
        print "Error: new_id %s" % str(e)
        return None


def commit():
    try:
        session = get_session()   
        session.commit()
    except DBException,e:
        print "Error: commit %s" % str(e)
    
def rollback():
    try:
        session = get_session()   
        session.rollback()
    except DBException,e:
        print "Error: rollback %s" % str(e)
        return None
    

def insert_pubkey(pubkey_id, dbhash, pubkey):
    try:
        session = get_session()
        sql = """
            INSERT INTO pubkey (pubkey_id, pubkey_hash, pubkey)
            VALUES (%d, :dbhash, :pubkey)""" % pubkey_id
        session.execute(sql, {'dbhash': dbhash, 'pubkey': pubkey})
    except DBException,e:
        print "Error: insert_pubkey %s" % str(e)


def insert_block(b):
    try:
        session = get_session()
        
        sql =  """INSERT INTO block (
                    block_id, block_hash, block_version, block_hashMerkleRoot,
                    block_nTime, block_nBits, block_nNonce, block_height,
                    prev_block_id, block_chain_work, block_value_in,
                    block_value_out, block_total_satoshis,
                    block_total_seconds, block_total_ss, block_num_tx,
                    search_block_id
                ) VALUES (%d, :bhash, %d, :mroot, %d, %d, %d, %d, %d, :cwork, %d, %d, %d, %d, %d, %d, %d
                )""" % (b['block_id'], b['version'], b['ntime'], b['nbits'], b['nonce'], b['height'],
                        b['prev_block_id'], b['value_in'], b['value_out'], b['satoshis'], b['total_ss'],
                        b['txs'], b['search_id'])
                
        session.execute(sql, {'bhash': b['bhash'], 'mroot': b['mroot'], 'cwork':b['chain_work']})
        
    except DBException,e:
        print "Error: insert_block %s" % str(e)


def insert_block_tx(block_id, tx, tx_pos):
    try:
        session = get_session()
        sql = """
        INSERT INTO block_tx 
        (block_id, tx_id, tx_pos)
         VALUES (%d, %d, %d)""" (block_id, tx['tx_id'], tx_pos)
        session.execute(sql)
        
    except DBException,e:
        print "Error: insert_block_tx %s" % str(e)
       
        
def insert_block_next(prev_block_id, block_id):
    try:
        session = get_session()
        sql = """
        INSERT INTO block_next (block_id, next_block_id)
        VALUES (%d, %d)""" %(prev_block_id, block_id)
        session.execute(sql)
        
    except DBException,e:
        print "Error: insert_block_next %s" % str(e)
        return None

def insert_block_txin(block_id, txin_id, oblock_id):
    try:
        session = get_session()
        sql = """
        INSERT INTO block_txin (block_id, txin_id, out_block_id)
        VALUES (%d, %d, %d)""" % (block_id, txin_id, oblock_id)
        session.execute(sql)
    except DBException,e:
        print "Error: insert_block_txin %s" % str(e)

def insert_orphan_block(block_id, prev_hash):
    try:
        session = get_session()
        sql = """
            INSERT INTO orphan_block (block_id, block_hashPrev)
             VALUES (%d, ':prev_hash)""" % block_id
        session.execute(sql, {'prev_hash': prev_hash})
        
    except DBException,e:
        print "Error: insert_orphan_block %s" % str(e)
        return None        
    

def insert_tx(tx_id, dbhash, version, locktime, size):
    try:
        session = get_session()
        sql = """
            INSERT INTO tx (tx_id, tx_hash, tx_version, tx_lockTime, tx_size)
             VALUES (%d, :txhash, %d, %d, %d)""" %(tx_id, version, locktime, size)
        session.execute(sql, {'txhash':dbhash})
    except DBException,e:
        print "Error: insert_block_next %s" % str(e)
        return None        
    


def insert_txout(txout_id, tx_id, pos, value, scriptPubkey, pubkey_id):
    try:
        session = get_session()
        sql = """
            INSERT INTO txout (
                   txout_id, tx_id, txout_pos, txout_value,
                    txout_scriptPubKey, pubkey_id
                ) VALUES (%d, %d, %d, %d, :scriptPubkey, %d)""" % (txout_id, tx_id, pos, value, pubkey_id)
        session.execute(sql, {'scriptPubkey': scriptPubkey})
    except DBException,e:
        print "Error: insert_txout %s" % str(e)
        
    
def insert_txin(txin_id, tx_id, pos, txout_id, scriptSig, sequence):
    try:
        session = get_session()
        sql = """
            INSERT INTO txin (
            txin_id, tx_id, txin_pos, txout_id, txin_scriptSig, txin_sequence ) 
            VALUES (%d, %d, %d, %d, ':scriptSig', %d) 
            """ % (txin_id, tx_id, pos, txout_id, sequence)
            
        session.execute(sql, {'scriptSig': scriptSig})
    except DBException,e:
        print "Error: insert_txin %s" % str(e)
        return None  

            
            
def insert_unlinked_txin(txin_id, prev_hash, prev_n):
    try:
        session = get_session()
        sql = """
            INSERT INTO unlinked_txin (
            txin_id, txout_tx_hash, txout_pos) 
            VALUES (%d, ':txhash', %d) 
            """ % (txin_id, prev_n)
        session.execute(sql, {'txhash': prev_hash})
    except DBException,e:
        print "Error: insert_unlinked_txin %s" % str(e)
        return None  


def insert_candidate(chain_id, b, in_longest):
    try:
        session = get_session()
        sql = """
            INSERT INTO chain_candidate (
                chain_id, block_id, in_longest, block_height
            ) VALUES (%d, %d, %d, %d)""" % (chain_id, b['block_id'], in_longest, b['height'])
        session.execute(sql)
         
    except DBException,e:
        print "Error: insert_candidate %s" % str(e)
        return None


def update_chain(block_id, chain_id):
    try:
        session = get_session()
        sql = """
             UPDATE chain
             SET chain_last_block_id = %d
             WHERE chain_id = %d""" % (block_id, chain_id)
        session.execute(sql)
    except DBException,e:
        print "Error: update_chain %s" % str(e)


def get_txin_by_txout_pos(dbhash, pos):
    try:
        session = get_session()              
        sql = """ SELECT txin_id FROM unlinked_txin
                 WHERE txout_tx_hash = :dbhash AND txout_pos = %d""" % pos
        cursor = session.execute(sql, {"dbhash": dbhash})
        return cursor.fetchall()
    except DBException,e:
        print "Error: get_txin_by_txout_pos %s" % str(e)
        return None        
        
    

def get_orphan_block_id(dbhash):
    try:
        session = get_session()           
        sql = """
            SELECT block_id FROM orphan_block WHERE block_hashPrev =:dbhash
            """
        cursor = session.execute(sql, {"dbhash": dbhash})
        return cursor.fetchall()
    except DBException,e:
        print "Error: get_orphan_block_ids %s" % str(e)
        return None        
                    



def get_pubkey_id(dbhash, pubkey):
    try:
        session = get_session()           
        sql = """
            SELECT pubkey_id
              FROM pubkey
             WHERE pubkey_hash = :dbhash
             """
        cursor = session.execute(sql, {"dbhash": dbhash})
        row = cursor.fetchone()             
        return row[0] if row else  None    
    except DBException,e:
        print "Error: get_pubkey_id %s" % str(e)
        return None   


def update_prev_block_id(block_id, orphan_id):
    try:
        session = get_session()  
        sql = """"UPDATE block SET prev_block_id = %d 
                WHERE block_id = %d""" % (block_id, orphan_id)
        session.execute(sql)      
    except DBException,e:
        print "Error: update_prev_block_id %s" % str(e)
    
    
def update_new_block(bs_secs, ss_destroyed, block_id):
    try:
        session = get_session()  
        sql = """UPDATE block SET block_satoshi_seconds = %d,
                block_ss_destroyed = %d
                WHERE block_id = %d""" % (bs_secs, ss_destroyed, block_id)
        session.execute(sql)      
    except DBException,e:
        print "Error: update_new_block %s" % str(e)

def update_txin(txout_id, txin_id):
    try:
        session = get_session()  
        sql ="UPDATE txin SET txout_id =%d WHERE txin_id =%d" % (txout_id, txin_id)
        session.execute(sql)
    except DBException,e:
        print "Error: update_txin %s" % str(e)
    
def update_block():
    try:
        session = get_session()  
        sql ="""
            UPDATE block
                SET block_height = %d,
                    block_chain_work = ':cwork',
                    block_value_in = %d,
                    block_total_seconds = %d,
                    block_total_satoshis = %d,
                    block_total_ss = %d,
                    search_block_id = %d
                 WHERE block_id = %d 
             """
        session.execute(sql)
    except DBException,e:
        print "Error: update_block %s" % str(e)

    
def update_block_ss(ss, destroyed, next_id):
    try:
        session = get_session()  
        sql ="""
            UPDATE block
            SET block_satoshi_seconds = %d,
            block_ss_destroyed = %d
            WHERE block_id = %d""" % (ss, destroyed, next_id)
        session.execute(sql)
    except DBException,e:
        print "Error: update_block_ss %s" % str(e)
    
 
def update_candidate(height, block_id):
    try:
        session = get_session()  
        sql ="""
            UPDATE chain_candidate SET block_height = %d
            WHERE block_id = %d""" % (height, block_id)
        session.execute(sql)
    except DBException,e:
        print "Error: update_candidate %s" % str(e)
    
    
def delete_unlinked_txin(txin_id): 
        
    try:
        session = get_session()              
        sql = "DELETE FROM unlinked_txin WHERE txin_id = %d" % txin_id
        session.execute(sql)
    except DBException,e:
        print "Error: delete_unlinked_txin %s" % str(e)
        

def delete_orphan_block(orphan_id):
    try:
        session = get_session()              
        sql = "DELETE FROM orphan_block WHERE block_id = %d" % orphan_id
        session.execute(sql)
    except DBException,e:
        print "Error: delete_orphan_block %s" % str(e)


 
def exist_block():
    store.selectrow("""
                    SELECT 1
                      FROM chain_candidate cc
                      JOIN block b ON (cc.block_id = b.block_id)
                     WHERE b.block_hash = ?
                       AND b.block_height IS NOT NULL
                       AND cc.chain_id = ?""", (
                        store.hashin_hex(str(hash)), chain.id))


def exist_candidate(block_id, chain_id):
    
    try:
        session = get_session()
        sql = """SELECT 1
              FROM chain_candidate
             WHERE block_id = %d
               AND chain_id = %d """ %(block_id, chain_id)
        cursor = session.execute(sql)
        res = cursor.fetchone()
        return False if res is None else True
    except DBException,e:
        print "Error: exist_candidate %s" % str(e)
        return False


def lookup_txout(tx_hash, txout_pos):
    try:
        session = get_session()

        sql ="""
            SELECT txout.txout_id, txout.txout_value
              FROM txout, tx
             WHERE txout.tx_id = tx.tx_id
               AND tx.tx_hash = :txhash
               AND txout.txout_pos = %d""" % txout_pos
        cursor = session.execute(sql, {'txhash': tx_hash})   
        row = cursor.fetchone()
        return (None, None) if row is None else (row[0], int(row[1]))
    except DBException,e:
        print "Error: lookup_txout %s" % str(e)
        return (None, None) 




def tx_find_id_and_value(tx, is_coinbase):
    try:
        session = get_session()
        sql = """
            SELECT tx.tx_id, SUM(txout.txout_value), 
                SUM(CASE WHEN txout.pubkey_id > 0 THEN txout.txout_value ELSE 0 END)
            FROM tx
            LEFT JOIN txout ON (tx.tx_id = txout.tx_id)
            WHERE tx_hash=:txhash
            GROUP BY tx.tx_id""" 
        
        cursor = session.execute(sql, {'txhash': util.rev(tx['hash'])})
        row = cursor.fetchone()
        
        if row:
            tx_id, value_out, undestroyed = row
            value_out = 0 if value_out is None else int(value_out)
            undestroyed = 0 if undestroyed is None else int(undestroyed)
            
            sql = """
                SELECT COUNT(1), SUM(prevout.txout_value)
                FROM txin
                  JOIN txout prevout ON (txin.txout_id = prevout.txout_id)
                WHERE txin.tx_id = %d""" % int(tx_id)
            
            cursor = session.execute(sql)
            count_in, value_in = cursor.fetchone()
            
            if (count_in or 0) < len(tx['txIn']):
                value_in = 0 if is_coinbase else None
            tx['value_in'] = None if value_in is None else int(value_in)
            tx['value_out'] = value_out
            tx['value_destroyed'] = value_out - undestroyed
            return tx_id

        return None
    except DBException,e:
        print "Error: tx_find_id_and_value %s" % str(e)
        return None
    
    

def find_prev(dbhash):
    try:
        sql = """
            SELECT block_id, block_height, block_chain_work,
                   block_total_satoshis, block_total_seconds,
                   block_satoshi_seconds, block_total_ss, block_nTime
              FROM block
             WHERE block_hash =:dbahsh"""
        
        cursor = session.execute(sql, {'dbhash': dbhash})
        row = cursor.fetchone()
        
        if row is None:
            return (None, None, None, None, None, None, None, None)
        (id, height, chain_work, satoshis, seconds, satoshi_seconds,
         total_ss, nTime) = row
        return (id, None if height is None else int(height),
                chain_work,
                None if satoshis is None else int(satoshis),
                None if seconds is None else int(seconds),
                None if satoshi_seconds is None else int(satoshi_seconds),
                None if total_ss is None else int(total_ss),
                int(nTime))

    except DBException,e:
        print "Error: find_prev %s" % str(e)


def get_unlinked_txins(block_id):
    try:
        session = get_session()    
    
        sql = """
            SELECT COUNT(1)
              FROM block_tx bt
              JOIN txin ON (bt.tx_id = txin.tx_id)
              JOIN unlinked_txin u ON (txin.txin_id = u.txin_id)
             WHERE bt.block_id = %d""" % block_id
             
        cursor = session.execute(sql)
        (unlinked_count, ) = cursor.fetchone()
        return unlinked_count 
   
    except DBDBException,e:
        print "Error: get_unlinked_txins %s" % str(e)
        return None
    

def get_block_txin(block_id):

    try:
        session = get_session()
        
        sql = """
            SELECT txin.txin_id, MIN(obt.block_id)
              FROM block_tx bt
              JOIN txin ON (txin.tx_id = bt.tx_id)
              JOIN txout ON (txin.txout_id = txout.txout_id)
              JOIN block_tx obt ON (txout.tx_id = obt.tx_id)
             WHERE bt.block_id =%d
             GROUP BY txin.txin_id""" % block_id
             
        cursor = session.execute(sql)
        rows = cursor.fetchall()
        return rows if rows is not None else None

    except DBException,e:
        print "Error: get_block_height %s" % str(e)
        return None



def get_block_height():
    try:
        session = get_session()
        sql = """SELECT MAX(block_height)
              FROM chain_candidate
             WHERE in_longest = 1
               """  
        cursor = session.execute(sql)
        (height, ) = cursor.fetchone()
        return -1 if height is None else int(height)
    except DBException,e:
        print "Error: get_block_height %s" % str(e)
        return None


def get_block_id_by_height(block_id):
    try:
        session = get_session()
                    
        sql = """ SELECT block_height, prev_block_id, search_block_id
                  FROM block
                 WHERE block_id = %d""" % block_id
        cursor = session.execute(sql)
        row = cursor.fetchone()
        return row if row is not None else None
    except DBException,e:
        print "Error: get_block_id_by_height %s" % str(e)
        return None

    
def get_block_ss_destroyed(block_id, ntime, tx_ids):
    try:
        session = get_session()

        sql = """SELECT COALESCE(SUM(txout_approx.txout_approx_value *
                        (%d - b.block_nTime)), 0)
                  FROM block_txin bti
                  JOIN txin ON (bti.txin_id = txin.txin_id)
                  JOIN txout_approx ON (txin.txout_id = txout_approx.txout_id)
                  JOIN block_tx obt ON (txout_approx.tx_id = obt.tx_id)
                  JOIN block b ON (obt.block_id = b.block_id)
                 WHERE bti.block_id = %d AND txin.tx_id = %d"""

        block_ss_destroyed = 0
        for tx_id in tx_ids:            
            cursor = session.execute(sql % (ntime, block_id, tx_id))
            (destroyed, ) = cursor.fetchone()
            block_ss_destroyed += destroyed
        return block_ss_destroyed
    except DBException,e:
        print "Error: get_block_ss_destroyed %s" % str(e)
        return None


def get_next_block(block_id):
    try:
        sql = """
            SELECT bn.next_block_id, b.block_nBits,
                   b.block_value_out, b.block_value_in, b.block_nTime,
                   b.block_total_satoshis
              FROM block_next bn
             JOIN block b ON (bn.next_block_id = b.block_id)
             WHERE bn.block_id = %d""" % block_id
        
        cursor = session.execute(sql)   
        rows = cursor.fetchall()
        return rows
    except DBException,e:
        print "Error: get_next_block %s" % str(e)
        return None


def get_block_tx_info(next_id):
    try:
        sql = """
                SELECT SUM(txout.txout_value),
                    COUNT(1),
                    COUNT(txout.txout_value)
                      FROM block_tx bt
                      JOIN txin ON (bt.tx_id = txin.tx_id)
                      LEFT JOIN txout ON (txout.txout_id = txin.txout_id)
                     WHERE bt.block_id = %d""" % next_id
        
        cursor = session.execute(sql)   
        rows = cursor.fetchone()
        return rows
    except DBException,e:
        print "Error: get_block_tx_info %s" % str(e)
        return None
   

def get_block_by_chain():
        row = store.selectrow("""
                SELECT b.block_id, b.block_height, b.block_chain_work
                  FROM block b, chain c
                 WHERE c.chain_id = ?
                   AND b.block_id = c.chain_last_block_id""", (chain_id,))


def get_block_by_hash(dbhash):
    
    try:
        session = get_session()
        sql = """SELECT block_id, block_height, block_chain_work,
                   block_nTime, block_total_seconds,
                   block_total_satoshis, block_satoshi_seconds,
                   block_total_ss
              FROM block
             WHERE block_hash=:dbhash
               """  
        cursor = session.execute(sql, {'dbhash':dbhash})
        row = cursor.fetchone()
        return None if row is None else int(row[0])
    except DBException, e:
        print "Error: get_block_height %s" % str(e)
        return None


def get_block_txids(next_id):
    try:
        session = get_session()
        sql = """SELECT tx_id
                FROM block_tx
                WHERE block_id = %d""" % next_id
        cursor = session.execute(sql)
        return cursor.fetchall()
    except DBException,e:
        print "Error: get_block_txids %s" % str(e)
        return None        
        

def chain_get_all():
        
    try:
        session = get_session()
        sql = """
        SELECT chain_id, chain_magic, chain_name, chain_code3,
            chain_address_version, chain_script_addr_vers, chain_policy, chain_decimals
        FROM chain"""
        cursor = session.execute(sql)
        return cursor.fetchall()
    except DBException,e:
        print "Error: chain_get_all %s" % str(e)
        return None  


def get_prev_block_id(block_id):
    try:
        session = get_session()
        sql = """SELECT prev_block_id FROM block WHERE block_id =%d""" % block_id
        cursor = session.execute(sql)
        row = cursor.fetchone()
        return row[0]
    except DBException,e:
        print "Error: chain_get_all %s" % str(e)
        return None  

    
def disconnect_block( block_id, chain_id):
    try:
        session = get_session()
        sql = """UPDATE chain_candidate
               SET in_longest = 0
             WHERE block_id = %d AND chain_id = %d""" % (block_id, chain_id)
        cursor = session.execute(sql)
    except DBException,e:
        print "Error: disconnect_block %s" % str(e)
    
    
def connect_block(store, block_id, chain_id):
    try:
        session = get_session()
        sql = """UPDATE chain_candidate
               SET in_longest = 1
             WHERE block_id = %d AND chain_id = %d""" % (block_id, chain_id)
        cursor = session.execute(sql)
    except DBException,e:
        print "Error: connect_block %s" % str(e)
