# -*- coding:utf8 -*-

import requests


def ip_info(ip):
    url = 'http://ip.taobao.com/service/getIpInfo.php?ip=%s' % ip
    r = requests.get(url)
    if r.json()['code'] == 0:
        i = r.json()['data']
        country = i['country']  # 国家
        area = i['area']  # 区域
        region = i['region']  # 地区
        city = i['city']  # 城市
        isp = i['isp']  # 运营商
        print "ip: ", ip
        print u'国家: %s\n区域: %s\n省份: %s\n城市: %s\n运营商: %s\n' % (country, area, region, city, isp)
        return i
    else:
        print "ERRO! ip: %s" % ip
        return None


if __name__ == '__main__':
    ips = ['121.10.104.107', '202.96.128.86']
    for ip in ips:
        ip_info(ip)
