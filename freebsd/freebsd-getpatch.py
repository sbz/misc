#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#
# Copyright (c) 2012 Sofian Brabez <sbz@FreeBSD.org>
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE AUTHOR AND CONTRIBUTORS ``AS IS'' AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.  IN NO EVENT SHALL THE AUTHOR OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS
# OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
# HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY
# OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
#
# $FreeBSD$
#
# MAINTAINER=   sbz@FreeBSD.org

import argparse
import re
import sys
import urllib2

"""
FreeBSD getpatch handles Gnats and Bugzilla patch attachment
"""

class GetPatch(object):

    def __init__(self, pr):
        self.pr = pr
        self.url = str()
        self.patch = str()

    def fetch(self, *largs, **kwargs):
        raise NotImplementedError()

    def write(self, filename, data):
        f=open(filename, 'w')
        f.write(data)
        f.close()
        print("[+] %s created" % filename)

    def get(self):
        self.fetch(self.pr, category='ports', action='edit')

        # alias self.patch
        patch = self.patch
        if '.' not in patch:
            print("[-] No patch found")
            sys.exit(1)

        self.write(
            patch[:patch.rindex('.')]+'.diff', urllib2.urlopen(self.url).read()
        )

class GnatsGetPatch(GetPatch):

    URL_BASE='http://www.freebsd.org/cgi'
    URL='%s/query-pr.cgi?pr=' % URL_BASE
    REGEX=r'.*<b>Download <a href="([^"]*)">([^<]*)</a>.*'

    def __init__(self, pr):
        GetPatch.__init__(self, pr)

    def fetch(self, *largs, **kwargs):
        category = kwargs['category']
        print("[+] Fetching patch for pr %s/%s" % (category, self.pr))
        pattern = re.compile(self.REGEX)
        u = urllib2.urlopen(self.URL+'%s/%s' % (category, self.pr))
        data = u.read()
        if data == None:
            print("[-] No patch found")
            sys.exit(1)

        for line in data.split('\n'):
            if 'Download' in line:
                self.url, self.patch = re.match(pattern, line).groups()
                break

class BzGetPatch(GetPatch):

    URL_BASE='https://bugzilla.freebsd.org'
    URL='%s/attachment.cgi?id=' % URL_BASE
    REGEX=r'.*<div class="details">([^ ]+) \(text/plain\)'

    def fetch(self, *largs, **kwargs):
        category = kwargs['category']
        action = 'action=%s' % kwargs['action']
        print("[+] Fetching patch for pr %s/%s" % (category, self.pr))
        pattern = re.compile(self.REGEX)
        u = urllib2.urlopen(self.URL+'%s&%s' % (self.pr, action))
        data = u.read()
        if data == None:
            print("[-] No patch found")
            sys.exit(1)

        for line in data.split('\n'):
            if 'details' in line:
                self.patch = re.match(pattern, line).groups()[0]
                break

        self.url = self.URL+'%s' % self.pr

def main(pr):

    parser = argparse.ArgumentParser(description='Gets patch from Bug Tracking System')
    parser.add_argument('pr', metavar='pr', type=str, nargs=1, help='Pr id number')
    parser.add_argument('--mode', type=str, help='Available modes to retrieve patch [gnats|bz]', default='gnats')

    args = parser.parse_args()

    pr = str(args.pr[0])
    mode = args.mode

    if '/' in pr and pr is not None:
        pr = pr.split('/')[1]

    Clazz = globals()['%sGetPatch' % args.mode.capitalize()]
    gp = Clazz(pr)
    gp.get()

if __name__ == '__main__':

    main(sys.argv[1])
