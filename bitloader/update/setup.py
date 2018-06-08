# -*- coding: utf-8 -*-
import sys, os
path = os.path.abspath(os.path.join(os.path.dirname('.'),os.path.pardir))
sys.path.append(path)

import db
from config import Config
from extension import mongodb_cli
from core import process_tx
from fix import fix_orphan

def setup():
    mongodb_cli.use_db(Config.bitcoin_db)
    
    max_id = db.block_get_last_id()
    start_id = mongodb_cli.get_checkpoint(Config.checkpoint, 'meta_max_block_id')
    
    orphan_id = start_id
        
    while start_id < max_id:
        
        end_id = db.block_get_next_id(start_id)
        print "block_id", start_id, end_id
        process_tx(end_id) 
        start_id = end_id
        if not Config.DEBUG:
            mongodb_cli.update_checkpoint(Config.checkpoint, 'meta_max_block_id', int(end_id))    
        
    #if orphan_id < max_id:
        #fix_orphan()
    
    mongodb_cli.close()



if __name__ == '__main__':
    setup()
