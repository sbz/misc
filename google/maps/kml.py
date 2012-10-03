#!/usr/bin/env python
import os
import sys
import socket

import lxml.etree as le
import GeoIP

GEOIP_URL='http://www.maxmind.com/download/geoip/database/'
GEOIP_CITY_DB='GeoLiteCity.dat.gz'

def fetch_and_extract_db():
        import gzip
        import urllib
        f = open(GEOIP_CITY_DB, 'w')
        f.write(urllib.urlopen('%s%s' % (GEOIP_URL, GEOIP_CITY_DB)).read())
        f.close()
        f = open(GEOIP_CITY_DB[:-3], 'w')
        f.write(gzip.open(GEOIP_CITY_DB, 'rb').read())
        f.close()
        os.unlink(GEOIP_CITY_DB)

class KMLWriter(object):
    """Allow to create a kml file from a input file. The file contains list
       of ip address. (output of pfctl -t ssh-bruteforce -Ts)
    """
    def __init__(self, input, output):
        self.input = input
        self.output = output
        self.xml = le.Element("kml", {'xmlns' : 'http://www.opengis.net/kml/2.2'})
        self.geoip_db = GEOIP_CITY_DB[:-3]

        if not os.path.exists(self.geoip_db):
            fetch_and_extract_db()

    def process(self):
        inputs = file(self.input, 'r')
        for ip in inputs.readlines():
            try:
                self.process_kml(self.process_geoip_record(ip.strip()))
            except:
                pass

        inputs.close()

        f = file(self.output, 'w')
        f.write(le.tostring(self.xml, pretty_print=True))
        f.close()

    def process_geoip_record(self, ip_address):
        gi = GeoIP.open(self.geoip_db, GeoIP.GEOIP_STANDARD)
        gr = gi.record_by_addr(ip_address)
        gr['ip'] = ip_address
        try:
            gr['host'] = socket.gethostbyaddr(ip_address)[0]
        except:
            #print gr
            gr['host'] = gr['ip']

        return gr

    def process_kml(self, gr):
        """
        <Placemark>
            <name>%host - %city (%country)</name>
            <description/>
            <Point>
                <coordinates>%longitude,%latitude</coordinates>
            </Point>
        </Placemark>
        """
        if not gr['city']:
            gr['city'] = 'Unknown'
        try:
            gr['city'] = unicode(gr['city'], 'latin-1')
        except Exception, e:
            print e
            return
        placemark = le.SubElement(self.xml, "Placemark")
        name = le.SubElement(placemark, "name")
        name.text = "%s - %s (%s)" % (gr['host'], gr['city'], gr['country_name'])
        description = le.SubElement(placemark, "description")
        point = le.SubElement(placemark, "Point")
        coord = le.SubElement(point, "coordinates")
        coord.text = "%(longitude)s,%(latitude)s" %  gr

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print "Usage: %s <input-file> <kml-file>\n" % sys.argv[0]
        sys.exit(1)

    kw = KMLWriter(sys.argv[1], sys.argv[2])
    kw.process()
