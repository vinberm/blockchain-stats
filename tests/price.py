# -*- coding: utf-8 -*-

import requests


def coinmaketcap(ticker, convert='USD'):
    '''
    Args:
        ticker: cryptocurrency symbol.
        convert: which currency to convert.
    '''
    url = 'https://api.coinmarketcap.com/v2/ticker/%s/?convert=%s' % (ticker, convert)
    print "url: ", url
    res = requests.get(url)
    return res.json()['data']


def listcoins():
    url = 'https://api.coinmarketcap.com/v2/listings'
    res = requests.get(url)
    return res.json()['data']


def btm_coin():
    for y in listcoins():
        if y['symbol'] == 'BTM':
            return y
    return None


def btm_info():
    info = btm_coin()
    if info is None:
        return None
    return coinmaketcap(info['id'])


if __name__ == '__main__':
    print btm_info()
