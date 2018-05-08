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


if __name__ == '__main__':
    c = listcoins()
    pa = []
    for x in c:
        if x['symbol'] == 'EOS' or x['symbol'] == 'ETH':
            pa.append(x)
    print pa

    for coin in pa:
        print coinmaketcap(coin['id'])
