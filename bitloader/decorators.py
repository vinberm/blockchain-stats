#! /usr/bin/env python
# -*- coding: utf-8 -*-
import flags
FLAGS = flags.FLAGS


def attrs(**kwargs):
    """
    设置queue、routing_key、name属性,若不存在则默认为'default'
    :param kwargs: 属性字典
    :return:
    """
    def wrapper(f):
        if 'queue' not in kwargs:
            setattr(f, 'queue', 'default')

        if 'routing_key' not in kwargs:
            setattr(f, 'routing_key', 'default')

        if 'name' not in kwargs:
            setattr(f, 'name', f.func_name)

        for k in kwargs:
            setattr(f, k, kwargs[k])
        return f
    return wrapper



def slice(f):
    """ choose the right table """
    def wrapper(*args, **kwargs):
        
        id = kwargs.get('id')
        table = kwargs.get('table')
                  
        table_name = table
        #choose table 
        if isinstance(id, int) and FLAGS.SLICE_ENABLE:
            table_id = id / FLAGS.slice_size
            table_name = table_name + (str(table_id) if table_id else '')
        kwargs['table'] = table_name
        res = f(*args, **kwargs)
        return res
    return wrapper