#! /usr/bin/env python
# -*- coding: utf-8 -*-

from application import app
from inspect import getmembers, isfunction
import jobs
__all__ = ['tasks', 'TASK_MONITOR_LIST']


task_monitor_list = []
# 队列任务
d_tasks = {}
for t in getmembers(jobs, isfunction):
    if 'attrs' not in t[0]:
        d_tasks.update({t[0]: app.task(t[1], **t[1].__dict__)})
    
    try:
        if t[1].monitor:
            task_monitor_list.append(t[1].name)
    except:
        pass


class DictToObject(object):
    def __init__(self, **ctx):
        self.__dict__.update(ctx)

tasks = DictToObject(**d_tasks)