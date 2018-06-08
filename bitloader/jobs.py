from decorators import attrs
from worker.tx import TxProc
from worker.node import NodeProc
from worker.block import BlockProc
from websocket.app.tx import TxMessage
from websocket.app.block import BlockMessage
from websocket.app.address import AddrMessage


@attrs(name='block_process', queue='block_notice', routing_key='block_notice', monitor=True)
def block_process(topic, bid):
    block_handle = BlockProc()    
    block_handle.notify(bid)

@attrs(name='tx_process', queue='tx_notice', routing_key='tx_notice', monitor=True)
def tx_process(topic, tid):    
    tx_handle = TxProc()    
    tx_handle.process_tx(tid)
    
@attrs(name='node_process', queue='node_notice', routing_key='node_notice', monitor=True)
def node_process(topic, nodes):
    node_handle = NodeProc()
    node_handle.send_node(nodes)
    
    
@attrs(name='ws_process', queue='ws_notice', routing_key='ws_notice', monitor=False)
def ws_process(uid, op, data):
 
    if op == 'tx_sub':
       resp = TxMessage.sub_tx(uid, op, data)      
    if op == 'block_sub':
        resp = BlockMessage.sub_block(uid, op, data)
    if op == 'addr_sub':
        resp = AddrMessage.sub_addr(uid, op, data)



    
