#!/usr/bin/env python3

"""
One updater script to pull them all
"""

import configparser
import io
import os
import shlex
import subprocess
import sys

user = os.environ['USER']
pwd = os.path.expanduser('~{0}'.format(user) or '/home/{0}'.format(user))

config = """
[default]
scm=git
git_update_cmd=git pull
git_clone_cmd=git clone
svn_update_cmd=svn update
svn_clone_cmd=svn checkout

[freebsd-src]
scm=svn
remote=svn+ssh://{1}@svn.freebsd.org/base/head
local={0}/freebsd/svn/src

[freebsd-ports]
scm=svn
remote=svn+ssh://{1}@svn.freebsd.org/ports/head
local={0}/freebsd/svn/ports

[freebsd-doc]
scm=svn
remote=svn+ssh://{1}@svn.freebsd.org/doc/head
local={0}/freebsd/svn/doc

[netbsd-src]
remote=http://git.edgebsd.org/EdgeBSD/netbsd-src.git
local={0}/netbsd/git/src

[netbsd-pkgsrc]
remote=http://git.edgebsd.org/EdgeBSD/netbsd-pkgsrc.git
local={0}/netbsd/git/pkgsrc

[openbsd-src]
remote=git://anoncvs.estpak.ee/openbsd-src
local={0}/openbsd/git/src
""".format(pwd, user)

cfg = configparser.ConfigParser()
cfg.read_string(config)

def call(cmd):
    subprocess.call(shlex.split(cmd))

class UpdaterFactory(object):

    class BaseUpdater(object):
        def __init__(self):
            self.scm = "none"
            self.already_cloned = False

        def setCloned(self):
            self.already_clone = True

        def isCloned(self):
            return self.already_cloned

        def up(self): raise NotImplemented("up() method to implement")

        def clone(self): raise NotImplemented("clone() method to implement")

    class SVNUpdater(BaseUpdater):
        def __init__(self, p):
            super().__init__()
            self.p = p
            self.scm = 'svn'

        def up(self):
            os.chdir(self.p.get('local'))
            cmd = cfg.get('default', 'svn_update_cmd')
            call(cmd)

        def clone(self):
            cmd = cfg.get('default', 'svn_clone_cmd')
            rc = call('svn checkout {0} {1}'.format(self.p.get('remote'), self.p.get('local')))
            if rc == 0:
                self.setCloned()

    class GitUpdater(BaseUpdater):
        def __init__(self, p):
            super().__init__()
            self.p = p
            self.scm = 'git'

        def up(self):
            os.chdir(self.p.get('local'))
            cmd = cfg.get('default', 'git_update_cmd')
            call(cmd)

        def clone(self):
            cmd = cfg.get('default', 'git_clone_cmd')
            rc = call('{0} {1} {2}'.format(cmd , self.p.get('remote'), self.p.get('local')))
            if rc == 0:
                self.setCloned()

    @classmethod
    def fromdict(cls, p):
        scm_type = p.get('scm')
        if scm_type == 'git':
            return cls.GitUpdater(p)
        elif scm_type == 'svn':
            return cls.SVNUpdater(p)
        else:
            raise Exception("scm_type '{0}' unknown".format(scm_type))

class Config(object):
    def __init__(self, cp):
        self.cp = cp

    def getSection(self, s, k):
        if self.cp is None:
            return ""
        return self.cp._sections[s].get(k)

    def getProjects(self):
        projects = []
        for s in self.cp._sections:
            if s == 'default':
                continue
            remote = self.getSection(s, 'remote')
            local = self.getSection(s, 'local')
            scm = self.getSection(s, 'scm') or self.getSection('default', 'scm')
            projects.append(
                {'name': s, 'remote': remote, 'local': local, 'scm': scm}
            )

        return projects

if __name__ == '__main__':

    for p in Config(cfg).getProjects():
        u = UpdaterFactory.fromdict(p)
        if not u.isCloned():
            u.clone()
        else:
            u.up()
