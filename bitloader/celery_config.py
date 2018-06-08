#! /usr/bin/env python
# -*- coding: utf-8 -*-
from kombu import Queue, Exchange
from datetime import timedelta
import flags

FLAGS = flags.FLAGS

class MyRouter(object):

    def route_for_task(self, task, args=None, kwargs=None):

        if task.startswith('block_'):
            return {'exchange': 'block_notice',
                    'exchange_type': 'direct',
                    'routing_key': 'block_notice'}
                
        if task.startswith('tx_'):
            return {'exchange': 'tx_notice',
                    'exchange_type': 'direct',
                    'routing_key': 'tx_notice'}

        if task.startswith('node_'):
            return {'exchange': 'node_notice',
                    'exchange_type': 'direct',
                    'routing_key': 'node_notice'}
            
        if task.startswith('ws_'):
            return {'exchange': 'ws_notice',
                    'exchange_type': 'direct',
                    'routing_key': 'ws_notice'}


class Config(object):
    # redis://:password@hostname:port/db_number
    BROKER_URL = FLAGS.broker_url
    # BROKER_URL = 'amqp://guest:guest@localhost:5672//'
    # CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
    BROKER_TRANSPORT_OPTIONS = {
        'visibility_timeout': 43200,
        'fanout_patterns': True,
        'fanout_prefix': True
    }
    CELERY_TASK_SERIALIZER = 'json'
    CELERY_RESULT_SERIALIZER = 'json'
    CELERY_ACCEPT_CONTENT = ['json']
    CELERY_TIMEZONE = 'Asia/Shanghai'
    CELERY_ENABLE_UTC = True

    CELERY_IMPORTS = ('tasks',)

    CELERY_DEFAULT_EXCHANGE = 'default'
    CELERY_DEFAULT_EXCHANGE_TYPE = 'direct'
    CELERY_DEFAULT_ROUTING_KEY = 'default'
    
    CELERYD_CONCURRENCY = 4
    
    # logs
    CELERYD_LOG_FILE = "logs/celery_log.log"

    # admin email, send message to when task which admin wants to monitor failed
    TASK_ERROR_EMAILS = ("langyu@8btc.com")
    
    # 报警邮件的发送时间间隔, 单位秒
    WARN_EMAIL_TIME_SPACE = 60

    # queues
    CELERY_QUEUES = (
        Queue('default', Exchange('default'), routing_key='default'),  # 默认队列
        Queue('block_notice', Exchange('block_notice'), routing_key='block_notice'), # 区块通知队列
        Queue('tx_notice', Exchange('tx_notice'), routing_key='tx_notice'),  # 交易通知队列
        Queue('node_notice', Exchange('node_notice'), routing_key='node_notice'),  # 结点通知队列
        Queue('ws_notice', Exchange('ws_notice'), routing_key='ws_notice'),  # 交易通知队列

    )
    
    # routes
    CELERY_ROUTES = (MyRouter(), )
