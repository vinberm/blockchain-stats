# -*- coding: utf-8 -*-

import json
import requests
import time

DEFAULT_ASSET_ID = 'ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff'


class BasicInfo:
    def __init__(self, base):
        self.url_base = base

    def get_recent_height(self):
        url = '/'.join([self.url_base, 'get-block-count'])
        response = requests.post(url).json()
        if response['status'] == 'fail':
            raise Exception('get chain height failed: %s', response['msg'])
        return response['data']['block_count']

    def get_last_block_interval(self, height):
        if height <= 0:
            return None
        times = []
        for h in range(height-1, height+1):
            params = json.dumps({'block_height': h})
            url = '/'.join([self.url_base, 'get-block'])
            response = requests.post(url, params).json()
            if response['status'] == 'fail':
                raise Exception('get block failed: %s', response['msg'])
            time = response['data']['timestamp']
            times.append(time)
        return times[1] - times[0]

    def get_difficulty(self, height):
        params = json.dumps({'block_height': height})
        url = '/'.join([self.url_base, 'get-difficulty'])
        response = requests.post(url, params).json()
        if response['status'] == 'fail':
            raise Exception('get difficulty failed: %s', response['msg'])
        return response['data']['difficulty']

    def get_average_hash_rate(self, height, num):
        if height - num <= 0 or height <= 0 or num <= 0:
            return None
        sum = 0
        for h in range(height-num, height+1):
            params = json.dumps({'block_height': h})
            url = '/'.join([self.url_base, 'get-hash-rate'])
            response = requests.post(url, params).json()
            if response['status'] == 'fail':
                raise Exception('get hash rate: %s', response['msg'])
            hash_rate = response['data']['hash_rate']
            sum += hash_rate
        return sum / num

    def get_tx_num(self, height, num):
        if height - num <= 0 or height <= 0 or num <= 0:
            return None
        sum = 0
        for h in range(height-num, height+1):
            params = json.dumps({'block_height': h})
            url = '/'.join([self.url_base, 'get-block'])
            response = requests.post(url, params).json()
            if response['status'] == 'fail':
                raise Exception('get block failed: %s', response['msg'])
            tx_num = len(response['data']['transactions'])
            sum += tx_num
        return sum / num

    def get_block_fee(self, height, num):
        if height - num <= 0 or height <= 0 or num <= 0:
            return None
        sum = 0
        for h in range(height-num, height+1):
            params = json.dumps({'block_height': h})
            url = '/'.join([self.url_base, 'get-block'])
            response = requests.post(url, params).json()
            if response['status'] == 'fail':
                raise Exception('get block failed: %s', response['msg'])
            coinbase = response['data']['transactions'][0]
            fee = coinbase['outputs'][0]['amount'] - self.get_recent_award(height)
            sum += fee
        return sum / num

    def get_recent_award(self, height):
        if height < 0:
            return None
        s = height / 840000
        return 41250000000 / (s + 1)

    def get_block_by_height(self, height):
        if height < 0:
            return None
        params = json.dumps({'block_height': height})
        url = '/'.join([self.url_base, 'get-block'])
        response = requests.post(url, params).json()
        if response['status'] == 'fail':
            raise Exception('get block failed: %s', response['msg'])
        return response['data']

    # 交易平均手续费（x neu/byte)
    def get_average_txs_fee(self, height):
        block = self.get_block_by_height(height)
        total_size = 0
        total_fee = 0
        for tx in block['transactions'][1:]:
            total_size += tx['size']
            total_fee += self.cal_tx_fee(tx)
        return 0 if total_size == 0 else total_fee / total_size

    def cal_tx_fee(self, tx):
        total_in = 0
        total_out = 0
        for txin in tx['inputs']:
            btm_in = txin['amount'] if txin['asset_id'] == DEFAULT_ASSET_ID else 0
            total_in += btm_in
        for txout in tx['outputs']:
            btm_out = txin['amount'] if txout['asset_id'] == DEFAULT_ASSET_ID else 0
            total_out += btm_out
        return total_in - total_out

    def list_txpool_num(self):
        url = '/'.join([self.url_base, 'list-unconfirmed-transactions'])
        response = requests.post(url).json()
        if response['status'] == 'fail':
            raise Exception('get block failed: %s', response['msg'])
        return response['data']['total']

    # 24小时出块总数和所有块时间戳等
    def new_block_status(self):
        ticks = int(time.time())
        recent_height = self.get_recent_height()
        recent_timestamp = self.get_block_by_height(recent_height)['timestamp']
        if recent_timestamp + 86400 < ticks:
            return 0, []
        ti = ticks
        height = recent_height
        timestamps = []
        while ticks - ti < 86400:
            height = height - 1
            ti = self.get_block_by_height(height)['timestamp']
            timestamps.append(ti)
        total_num = recent_height - height
        timestamps.sort()
        average_block_time = 86400 / total_num

        # 所有出块间隔列表
        intervals = []
        for y in range(len(timestamps) - 1):
            interval = timestamps[y + 1] - timestamps[y]
            intervals.append(interval)
        intervals.sort()

        length = len(intervals)
        median_interval = (intervals[length/2] + intervals[length/2-1]) / 2 if length % 2 == 0 else intervals[(length+1)/2]
        # 24小时内出块总数、平均时间、中位数、最大、最小
        return [total_num, average_block_time, median_interval, intervals[-1], intervals[0]]
