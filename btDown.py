#!/usr/bin/env python3
#-*- coding: utf-8 -*-
#pylint: disable=C0103,C0111,C0325,C0703

'''btDown.py - Download resource for FTP/Thunder/Magnet/BT

Usage: python3 btDown.py <url>

Required:
    url         FTP/Thunder/Magnet/BT downloading URL

Notice: Python3 required for btDown.py

Author: zanran (wayne@zanran.me)
CreatedAt: Mon Oct  8 21:27:28 CST 2018
'''

import os
import sys
import requests
import time
import re

def usage(err=None):
    if err:
        print(err)
    print(__doc__)
    sys.exit(0)

class BtDown(object):
    def __init__(self, url, media_type):
        pass

def main():
    if len(sys.argv) != 3:
        usage()
    print('------------------ Well done ------------------')


if __name__ == '__main__':
    main()
