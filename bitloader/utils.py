#! /usr/bin/env python

import os
import sys
import random
import datetime
import time

def identity(x):
    return x
def rev(x):
    return None if x is None else x[::-1]
def to_hex(x):
    return None if x is None else str(x).encode('hex')
def from_hex(x):
    return None if x is None else x.decode('hex')
def to_hex_rev(x):
    return None if x is None else str(x)[::-1].encode('hex')
def from_hex_rev(x):
    return None if x is None else x.decode('hex')[::-1]

binin       = identity
binin_hex   = from_hex
binout      = identity
binout_hex  = to_hex
hashin      = rev
hashin_hex  = from_hex
hashout     = rev
hashout_hex = to_hex


def import_class(import_str):
    """Returns a class from a string including module and class"""
    mod_str, _sep, class_str = import_str.rpartition('.')
    try:
        __import__(mod_str)
        return getattr(sys.modules[mod_str], class_str)
    except Exception, e:
        print e

def import_object(import_str):
    """Returns an object including a module or module and class"""
    try:
        __import__(import_str)
        return sys.modules[import_str]
    except ImportError:
        cls = import_class(import_str)
        return cls()


def this_day(now):
    return int(time.mktime(now.timetuple()))

def last_month(now):
    last = now - datetime.timedelta(days=1)
    last_month = datetime.date(day=1, month=last.month, year=last.year)
    return last_month

def next_month(now):
    if now.month == 12:
        nextmonth = now.replace(year=now.year+1, month=1)
    else:
        nextmonth = now.replace(month=now.month+1)
    return nextmonth

def last_week(now):
    last_week = now - datetime.timedelta(days=7)
    return last_week

def next_week(now):
    next_week = now + datetime.timedelta(days=7)
    return next_week

def last_hour(now):
    this_hour = now.replace(minute=0, second=0)
    last_hour = this_hour - datetime.timedelta(hours=1)
    return int(time.mktime(last_hour.timetuple()))

def next_hour(now):
    this_hour = now.replace(minute=0, second=0)
    next_hour = this_hour + datetime.timedelta(hours=1)
    return int(time.mktime(next_hour.timetuple()))

def this_hour(now):
    this_hour = now.replace(minute=0, second=0)
    return int(time.mktime(this_hour.timetuple()))


BTC_IN_SATOSHIS = 10 ** 8
DEFAULT_DECIMALS = 8
FEE_PER_BYYE  = 20
DEFAULT_PORT = 8333
ONE_DAY = 60 * 60 * 24
def format_bitcoin_satoshis(satoshis):
    decimals = DEFAULT_DECIMALS
    coin = 10 ** decimals

    if satoshis is None:
        return ''
    if satoshis < 0:
        return '-' + format_bitcoin_satoshis(-satoshis)
    satoshis = int(satoshis)
    integer = satoshis / coin
    frac = satoshis % coin
    return (str(integer) +
            ('.' + (('0' * decimals) + str(frac))[-decimals:])
            .rstrip('0').rstrip('.'))