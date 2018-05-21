# -*- coding: utf-8 -*-

import threading
import time


def fun_timer():
    print 'Hello S!'
    global timer
    timer = threading.Timer(2, fun_timer)
    timer.start()


fun_timer()

while True:
    print 'Hello P!'
    time.sleep(2)

