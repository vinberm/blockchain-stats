import flags
from authproxy import AuthServiceProxy, JSONRPCException
from cache_module import RedisClient


FLAGS = flags.FLAGS

#rpc
rpc_client = AuthServiceProxy("http://%s:%s@%s:8332/" % (FLAGS.rpc_user, FLAGS.rpc_password, FLAGS.rpc_host))


#redis
redis_client = RedisClient()
    
    
