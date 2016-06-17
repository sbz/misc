#!/usr/bin/env python

import os
import sys
import subprocess

DAYO_CMD = "/Users/sbz/Downloads/Day-O/Day-O.app/Contents/MacOS/Day-O"


class TimeZone(object):

    def __init__(self):
        # tz_string according to find /usr/share/zoneinfo -type f
        self.tz_string = os.environ.get("TZ", "Europe/Paris")

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

    def _set_zone(self):
        os.environ["TZ"] = self.tz_string


def main():
    tz = TimeZone()
    tz.set_pdt()

    rc = subprocess.call([DAYO_CMD, "-psn_0_503931"], shell=True)
    return rc

if __name__ == "__main__":
    sys.exit(main())
