#!/usr/bin/env python

import os
import sys
import subprocess

DAYO_CMD = "/Applications/Day-O/Day-O.app/Contents/MacOS/Day-O"


class TimeZone(object):
    """
    This class allow to launch Day-O app with the given timezone.

    'tz_string' is a string corresponding to the correct zonename info
    according database located into /usr/share/zoneinfo.

    All available values can be listed using shell command below
        % find /usr/share/zoneinfo -type f

    See also tzfile(5), zdump(8).
    """
    def __init__(self):
        self.tz_string = os.environ.get("TZ", "Europe/Paris")

    def _set_zone(self):
        os.environ["TZ"] = self.tz_string

    def set_bdt(self):
        """
        British Daylight Time
        """
        self.tz_string = "Europe/London"
        self._set_zone()

    def set_pdt(self):
        """
        Pacific Daylight time
        """
        self.tz_string = "US/Pacific"
        self._set_zone()

    def set_jst(self):
        """
        Japan Standard time
        """
        self.tz_string = "Asia/Tokyo"
        self._set_zone()

    def set_gmt(self):
        """
        Greenwich Mean time
        """
        self.tz_string = "Europe/Dublin"
        self._set_zone()


def main():
    tz = TimeZone()
    tz.set_pdt()

    rc = subprocess.call([DAYO_CMD, "-psn_0_503931"], shell=True)
    return rc

if __name__ == "__main__":
    sys.exit(main())
