#!/usr/bin/env python
# -*- coding: utf-8 -*-
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
        self.patchs = list()
        self.url = str()
        self.patch = str()
        self.output_stdout = False

    def fetch(self, *largs, **kwargs):
        raise NotImplementedError()

    def write(self, filename, data):
        f=open(filename, 'w')
        f.write(data)
        f.close()
        self.out("[+] %s created" % filename)

    def get(self,only_last=False, output_stdout=False):
        self.output_stdout = output_stdout
        self.fetch(self.pr, category='ports', action='edit')

        if only_last:
            self.patchs = [self.patchs.pop()]

        for patch in self.patchs:
            url = patch['url']
            p = patch['name']
            if '.' not in p:
                self.out("[-] No patch found")
                sys.exit(1)

            data = urllib2.urlopen(url).read()

            if self.output_stdout:
                sys.stdout.write(data)
            else:
                self.write(p[:p.rindex('.')]+'.diff', data)

    def out(self, s):
        if not self.output_stdout:
            print(s)

class GnatsGetPatch(GetPatch):

    URL_BASE='http://www.freebsd.org/cgi'
    URL='%s/query-pr.cgi?pr=' % URL_BASE
    REGEX=r'<b>Download <a href="([^"]*)">([^<]*)</a>'

    def __init__(self, pr):
        GetPatch.__init__(self, pr)

    def fetch(self, *largs, **kwargs):
        category = kwargs['category']
        self.out("[+] Fetching patch for pr %s/%s" % (category, self.pr))
        pattern = re.compile(self.REGEX)
        u = urllib2.urlopen(self.URL+'%s/%s' % (category, self.pr))
        data = u.read()
        if data == None:
            self.out("[-] No patch found")
            sys.exit(1)

        for patchs in re.findall(pattern, data):
            self.patchs.append({'url': patchs[0], 'name': patchs[1]})

class BzGetPatch(GetPatch):

    URL_BASE='https://bugzilla.freebsd.org'
    URL='%s/attachment.cgi?id=' % URL_BASE
    REGEX=r'<div class="details">([^ ]+) \(text/plain\)'

    def __init__(self, pr):
        GetPatch.__init__(self, pr)

    def fetch(self, *largs, **kwargs):
        category = kwargs['category']
        action = 'action=%s' % kwargs['action']
        self.out("[+] Fetching patch for pr %s/%s" % (category, self.pr))
        pattern = re.compile(self.REGEX)
        u = urllib2.urlopen(self.URL+'%s&%s' % (self.pr, action))
        data = u.read()
        if data == None:
            self.out("[-] No patch found")
            sys.exit(1)

        url = self.URL+'%s' % self.pr
        name = re.findall(pattern, data)[0]

        if name == None:
            self.out("[-] No patch found")
            sys.exit(1)

        self.patchs.append({'url': url, 'name': name})

def main():

    parser = argparse.ArgumentParser(description='Gets patch from Bug Tracking System')
    parser.add_argument('pr', metavar='pr', type=str, nargs=1, help='Pr id number')
    parser.add_argument('--mode', type=str, help='Available modes to retrieve patch', choices=['gnats','bz'], default='gnats')
    parser.add_argument('--last', action='store_true', help='Only retrieve last iteration of the patch')
    parser.add_argument('--stdout', action='store_true', help='Output patch on stdout')

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)

    args = parser.parse_args()

    pr = str(args.pr[0])
    mode = args.mode

    if '/' in pr and pr is not None:
        pr = pr.split('/')[1]

    Clazz = globals()['%sGetPatch' % args.mode.capitalize()]
    gp = Clazz(pr)
    gp.get(only_last=args.last, output_stdout=args.stdout)

if __name__ == '__main__':

    main()
