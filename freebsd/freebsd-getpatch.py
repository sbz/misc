#!/usr/bin/env python

import urllib2
import re
import sys

QUERY_PR='http://www.freebsd.org/cgi/query-pr.cgi?pr='
REGEX='.*<b>Download <a href="([^"]*)">([^<]*)</a>.*'

"""
FreeBSD getpatch
"""

def fetchpatch(pr_number, category='ports'):
    print("[+] Fetching patch for pr %s/%s" % (category, pr_number))
    pattern = re.compile(REGEX)
    u = urllib2.urlopen(QUERY_PR+'%s/%s' % (category, pr_number))
    data = u.read()

    for line in data.split('\n'):
        if 'Download' in line:
            url, patchname = re.match(pattern, line).groups()

    return url, patchname

def writepatch(filename, data):
    f=open(filename, 'w')
    f.write(data)
    print("[+] %s created" % filename)

def getpatch(pr):
    url, patch = fetchpatch(pr)
    patchdata = urllib2.urlopen(url).read()
    writepatch(patch[:patch.rindex('.')]+'.diff', patchdata)

def main(pr):
    getpatch(pr)

if __name__ == '__main__':
    pr_number = sys.argv[1]

    if '/' in pr_number:
        pr_number = pr_number.split('/')[1]

    main(pr_number)
