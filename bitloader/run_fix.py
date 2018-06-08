#! /usr/bin/env python
# -*- coding: utf-8 -*-
from fix import pubkey_info_fix, cache_clear, relay_fix

import sys

if sys.argv[1] == 'pubkey':
    file = sys.argv[2]
    pubkey_info_fix.run_schedule(file)
    
if sys.argv[1] == 'cache':
    cache_clear.run_schedule()
    
if sys.argv[1] == 'relay':
    relay_fix.run_schedule()
