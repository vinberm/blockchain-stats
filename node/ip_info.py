from geoip2 import database
from geoip2.errors import AddressNotFoundError


class IpInfo(object):

    def __init__(self, path):
        try:
            self.reader = database.Reader(path)
        except IOError:
            self.reader = None

    def get_country(self, ip):
        try:
            address_info = self.reader.city(ip)
            return address_info.country.name
        except (AddressNotFoundError, ValueError):
            return None





reader = database.Reader('../misc/GeoLite2-City.mmdb')
res = reader.city('101.132.176.116')

print res.country.iso_code
print res.country.name
print res.country.names['zh-CN']

print res.city.name
print res.city.names['zh-CN']

print res.postal.code
print res.location.latitude
print res.location.longitude
