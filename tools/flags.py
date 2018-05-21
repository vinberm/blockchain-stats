# -*- coding: utf-8 -*-

import gflags
FLAGS = gflags.FLAGS

# mongodb
gflags.DEFINE_string('mongo_bytom', 'bytom', 'mongodb bytom main db')
gflags.DEFINE_string('mongodb_user', 'bytom', 'mongodb user name')
gflags.DEFINE_string('mongodb_password', 'bytom', 'mongodb user password')
gflags.DEFINE_integer('table_capacity', 99000000, 'table capacity')


