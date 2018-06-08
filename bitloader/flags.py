#! /usr/bin/env python
# -*- coding: utf-8 -*-
import gflags
FLAGS = gflags.FLAGS

#RPC
gflags.DEFINE_string('rpc_host', 'localhost', 'rpc host')
gflags.DEFINE_string('rpc_user', 'bitcoinrpcuser',  'rpc user')
gflags.DEFINE_string('rpc_password', 'langyufred', 'rpr password')

#redis
gflags.DEFINE_string('redis_host', '106.186.113.235', 'redis host')
gflags.DEFINE_string('redis_port',  6379, 'redis port')
gflags.DEFINE_string('redis_passwd', '1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa', 'redis password')

gflags.DEFINE_string('main_db', 1, 'redis cache db')
gflags.DEFINE_string('probe_db', 2, 'redis cache db')
gflags.DEFINE_string('node_db', 3, 'redis cache db')
gflags.DEFINE_string('broker_url', 'redis://localhost:6379/0', 'broker') 

#mysql
gflags.DEFINE_string('sql_connection', 'mysql://blockmetaaccount:1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa@106.185.41.188/bitcoin', 'mysql host')
gflags.DEFINE_integer('sql_idle_timeout', 300, 'mysql timeout')
gflags.DEFINE_integer('sql_pool_size', 300, 'mysql host')


#mongodb
gflags.DEFINE_string('mongodb_host', '106.187.49.47', 'mongodb host')
gflags.DEFINE_string('mongodb_port',  27017, 'mongodb port')
gflags.DEFINE_string('mongodb_user', 'abe', 'mongodb user')
gflags.DEFINE_string('mongodb_password', '14cZMQk89mRYQkDEj8Rn25AnGoBi5H6uer', 'mongodb password')

#IP db
gflags.DEFINE_string('geoip_db', '../misc/GeoLite2-City.mmdb', 'ip database')


#mongodb slice table size
gflags.DEFINE_bool('SLICE_ENABLE', False, 'switch')
gflags.DEFINE_integer('slice_size', 176000000, 'table item count')


gflags.DEFINE_integer('top_limit', 10, 'tx count')


