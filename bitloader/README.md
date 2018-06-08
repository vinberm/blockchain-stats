#bitloader


交互REDIS数据结构 

TX:  
TX\_MEMPOOL\_NUM   #tx总数   （REDIS string)  
TX\_MEMPOOL\_SIZE  #tx总大小  (REDIS string)   
CURRENT\_TX        #当前tx，string取出  
UNCONFIRMED\_{hash}:{'lite': tx\_lite, 'detail':tx\_detail})  #交易结构, (REDIS hash)   

ADDRESS:  
ADDR\_{addr}: [tx1, tx2]    #地址结构, ( REDIS set) 

UTXO:  
UTXO\_{txhash}: {0: "[tx1, tx2, ...]", 1:"[tx3，...]"}  #UTXO探测结构， （REDIS hash)  
CONFLICT\_TXS: [tx1, tx2, ...]  #存在双花的交易数 （REDIS set)  

NODES:  
CURRENT\_NODES: [node1, node2, ...] #活跃节点信息， （REDIS hash)   
node: {ip}:{iso_code}  



CELERY启动命令: 
celery -A application.app worker -P gevent -Q tx_notice,block_notice -l info

