#! /usr/bin/env python
# -*- coding: utf-8 -*-
from celery import Celery
from celery_config import Config
from gevent import monkey; monkey.patch_all()
app = Celery()
app.config_from_object(Config)

if __name__ == '__main__':

    app.start()