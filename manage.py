# -*- coding: utf-8 -*-

from report import BasicInfo
import click
import json
import os


@click.command()
@click.option("--url", default="127.0.0.1:9888", help="base url of rpc")
def run(url):
    base_url = "http://" + url
    asl = BasicInfo(base_url)
    h = asl.get_recent_height()
    block_status = asl.new_block_status()

    filename = os.getcwd() + '/result.json'
    print filename
    if not os.path.exists('result.json'):
        os.system(r'touch {}'.format(filename))

    result = {
        "height": h,
        "last_block_interval": asl.get_last_block_interval(h),
        "difficulty": asl.get_difficulty(h),
        "hash_rate": asl.get_average_hash_rate(h, 100),
        "tx_num": asl.get_tx_num(h, 100),
        "block_fee": asl.get_block_fee(h, 100),
        "tx_fee": asl.get_average_txs_fee(h),
        "pool_tx_num": asl.list_txpool_num(),
        "block_num_one_day": block_status[0],
        "average_block_interval": block_status[1],
        "median_block_interval": block_status[2],
        "max_block_interval": block_status[3],
        "min_block_interval": block_status[4]
    }

    with open(filename, 'w') as f:
        json.dump(result, f, indent=4, sort_keys=True)
    with open(filename, 'r') as f:
        print json.load(f)

    print "*************let's go!!!***************"
    print
    print "--recent height--: %s" % h
    print
    print "--last block interval--: %s" % asl.get_last_block_interval(h)
    print
    print "--difficulty--: %s" % asl.get_difficulty(h)
    print
    print "--hash rate--: %s" % asl.get_average_hash_rate(h, 100)
    print
    print "--tx number--: %s" % asl.get_tx_num(h, 100)
    print
    print "--block fee--: %s" % asl.get_block_fee(h, 100)
    print
    print "--tx fee--: %s" % asl.get_average_txs_fee(h)
    print
    print "--txpool num--: %s" % asl.list_txpool_num()
    print
    print "--block num in 24 hours--: %s" % block_status[0]
    print
    print "--average block time in 24 hours--: %s" % block_status[1]
    print
    print "--median block time in 24 hours-- %s" % block_status[2]
    print
    print "--max block time in 24 hours-- %s" % block_status[3]
    print
    print "--min block time in 24 hours-- %s" % block_status[4]
    print


if __name__ == '__main__':
    run()
