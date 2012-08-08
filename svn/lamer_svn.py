#!/usr/bin/env python
"""
This script get all informations (user,passwd,uri) of local subversion accounts
pylint : 10/10 :)
"""

import os

HOME = os.environ['HOME']

SVNPATH = HOME + '/.subversion/auth/svn.simple'
SVNINFO = {}

class Svninfo:
    """ This class provide a simple structure with a dispatch table """

    def __init__(self, path, svninfo):
        """ construct a new Svninfo object """
        self.path = path
        self.svninfo = svninfo
        self.dispatch_table = {
            16: Svninfo.user_case,
            8: Svninfo.passwd_case,
            12: Svninfo.http_case
        }


    def user_case(self, line):
        """ user case dispatch """
        self.svninfo['username'] = line.strip()

    def passwd_case(self, line):
        """ passwd case dispatch """
        self.svninfo['passwd'] = line.strip()

    def http_case(self, line):
        """ http case dispatch """
        self.svninfo['http'] = line.split()[0].strip("<>")

    def svn_print(self):
        """ svn_print() Print svn account information """
        print "svn account %(http)s %(username)s:%(passwd)s" % self.svninfo

    def svn_process(self):
        """ svn_process() Process searching """
        for svnfile in os.listdir(self.path):
            svnfd = open('%s/%s' % (self.path, svnfile), 'r')
            line_number = 1
            for line in svnfd.readlines():
                if line_number in [8, 12, 16]:
                    self.dispatch_table[line_number](self, line)
                line_number = line_number + 1
            svnfd.close()
            self.svn_print()

if __name__ == '__main__':
    S = Svninfo(SVNPATH, SVNINFO)
    S.svn_process()
