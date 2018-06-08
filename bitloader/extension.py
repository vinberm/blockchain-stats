import flags
import logging
from gevent import monkey
monkey.patch_all()

from authproxy import AuthServiceProxy, JSONRPCException
from cache_module import RedisClient, MongodbClient, GetIpInfo


FLAGS = flags.FLAGS

#rpc
rpc_client = AuthServiceProxy("http://%s:%s@%s:8332/" % (FLAGS.rpc_user, FLAGS.rpc_password, FLAGS.rpc_host))


#redis
rc_main = RedisClient(db=FLAGS.main_db)
rc_probe = RedisClient(db=FLAGS.probe_db)
rc_node = RedisClient(db=FLAGS.node_db)


#monogdb 
mongodb_cli = MongodbClient()

#geoip
geoip_loc = GetIpInfo(FLAGS.geoip_db)
