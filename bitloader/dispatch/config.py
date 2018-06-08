import sys
import gflags

CONFIGS = gflags.FLAGS

def config_parse(file):
    pass
    #config = pyfig.Pyfig(file)
    #for x,y in config.general:
        #if x == "daemon":
            #gflags.DEFINE_integer('daemon', int(y), 'server run in background')



class proc(object):
    def __init__(self, func):
        self.func = func

    def __ror__(self, inputs):
        return self.func(inputs)


class Configer(object):
    
    config = {}
    setups = []


    def register_app(self, **deco):
        def foo(func):
            name = deco.get('name')
            level = deco.get('level', 99999)
            self.setups.append({
                'func': func,
                'name': name,
                'level': level
            })
            return func

        return foo

    def setup(self, own_cfg, onlevel=0):

        self.setups.sort(key=lambda x: x['level'])
        self.config.update(own_cfg)

        for s in Configer.setups:
            func = s['func']
            name = s['name']
            try:
                if name:
                    func(self.config[name])
                else:
                    func()
            except Exception, e:
                print str(e)
                sys.exit(1)

    def on_change(self):
        pass  


message = Configer()