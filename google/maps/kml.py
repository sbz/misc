#!/usr/bin/env python
import sys
import socket

import lxml.etree as le
import GeoIP

class KMLWriter(object):
    """Allow to create a kml file from a input file. The file contains list
       of ip address. (output of pfctl -t ssh-bruteforce -Ts)
    """
    def __init__(self, input, output):
        self.input = input
        self.output = output
        self.xml = le.Element("kml", {'xmlns' : 'http://www.opengis.net/kml/2.2'})

    def process(self):
        inputs = file(self.input, 'r')
        for ip in inputs.readlines():
            self.process_kml(self.process_geoip_recorid(ip.strip()))

        inputs.close()

        f = file(self.output, 'w')
        f.write(le.tostring(self.xml, pretty_print=True))
        f.close()

    def process_geoip_recorid(self, ip_address):
        gi = GeoIP.open('GeoLiteCity.dat', GeoIP.GEOIP_STANDARD)
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
   kw = KMLWriter(sys.argv[1], sys.argv[2])
   kw.process() 
