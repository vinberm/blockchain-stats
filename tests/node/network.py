# -*- coding: utf-8 -*-

import random
import time
from core import CAddress
from config import Config


class MsgVersion(object):
    command = "version"

    def __init__(self):
        self.nVersion = Config.MY_VERSION
        self.nServices = 1
        self.nTime = time.time()
        self.addrTo = CAddress()
        self.addrFrom = CAddress()
        self.nNonce = random.getrandbits(64)
        self.nStartingHeight = -1
