# -*- coding: utf-8 -*-

from report import BasicInfo
import click
import json
import os
import sys


@click.command()
@click.option("--url", default="127.0.0.1:9888", help="base url of rpc")
def run(url):
    base_url = "http://" + url
    asl = BasicInfo(base_url)
    status = asl.all_chain_status()
    if status is None:
        sys.exit()
    filename = os.path.join(os.getcwd(), 'result.json')
    print 'filename', filename
    if not os.path.exists('result.json'):
        os.system(r'touch {}'.format(filename))

    with open(filename, 'w') as f:
        json.dump(status, f, indent=4, sort_keys=True)
    with open(filename, 'r') as f:
        json.load(f)

    print "*************let's go!!!***************"
    print status


if __name__ == '__main__':
    run()
