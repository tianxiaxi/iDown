#!/usr/bin/env python3
#-*- coding: utf-8 -*-

'''btDown.py - Download resource for HTTP/HTTPS/FTP/Thunder/Magnet/BT

Usage: python3 btDown.py <url> [path]

Required:
    url         HTTP/HTTPS/FTP/Thunder/MagNet/BT downloading URL

Optionals:
    path        The store path for the downloaded file

Notice: Python3 required for btDown.py

Author: zanran (wayne@zanran.me)
CreatedAt: Mon Oct  8 21:27:28 CST 2018
'''

import os
import sys
import requests
import time
import re
import enum
import base64
from urllib import parse, request

def usage(err=None):
    if err:
        print(err)
    print(__doc__)
    sys.exit(0)

@enum.unique
class PROTROL_TYEP(enum.Enum):
    UNKNOWN = 0
    HTTP        = 1 # HTTP/HTTPS下载
    FTP         = 2 # FTP下载
    BT          = 3 # BT下载
    MAGNET      = 4 # 磁力下载
    THUNDER     = 5 # 讯雷下载

class BtDown(object):
    def __init__(self, url, path = None):
        self.origin_url = url
        self.dest_path = path

    def detectProtrolType(self, url):
        bt_type = PROTROL_TYEP.UNKNOWN
        if (re.match('^ftp://', url, re.IGNORECASE)):
            bt_type = PROTROL_TYEP.FTP
        elif (re.match('^thunder://', url, re.IGNORECASE)):
            bt_type = PROTROL_TYEP.THUNDER
        elif (re.match('^magnet:?', url, re.IGNORECASE)):
            bt_type = PROTROL_TYEP.MAGNET
        elif (re.search(r'\.torrent$', url, re.IGNORECASE)):
            bt_type = PROTROL_TYEP.BT
        # http/https detect must be after torrent
        elif (re.match('^https?://', url, re.IGNORECASE)):
            bt_type = PROTROL_TYEP.HTTP
        return bt_type

    def _parserThunderUrl(self, url):
        thunder_url = re.sub('^thunder://', '', url, re.IGNORECASE)
        normalize_url = base64.b64decode(thunder_url).decode()
        normalize_url = re.sub('^AA', '', normalize_url)
        normalize_url = re.sub('ZZ$', '', normalize_url)
        return normalize_url

    def _parserMagnetUrl(self, url):
        return ''

    def parseUrlProtrol(self, url):
        normalize_url = url
        bt_type = self.detectProtrolType(url)
        if bt_type in [PROTROL_TYEP.THUNDER]:
            normalize_url = self._parserThunderUrl(url)
        elif bt_type in [PROTROL_TYEP.MAGNET]:
            normalize_url = self._parserMagnetUrl(url)
        elif bt_type in [PROTROL_TYEP.BT]:
            raise Exception('BT (torrent) is unsupported by now !')
        return normalize_url

    def getTitle(self, url):
        title = 'unnamed_file'
        bt_type = self.detectProtrolType(url)
        if bt_type in [PROTROL_TYEP.HTTP, PROTROL_TYEP.FTP]:
            last_slash = url.rfind('/')
            if last_slash != -1:
                title = url[last_slash + 1:].strip()
        if title.count('%') > 1:
            title = parse.unquote(title)
        return title

    def _showDownloadProgress(self, file, percent):
        base_file = os.path.basename(file)
        if(percent > 100):
            percent = 100
        message = '\r  Downloading %s ...... %2.f%%' % (base_file, percent)
        print(message, end='')
        return

    def _download_http(self, url, dest_file):
        res = requests.get(url, stream=True)
        max_file_bytes = int(res.headers['Content-Length'])

        chunk_size = 1024*1024*4
        downloaded_size = 0
        f = open(dest_file, 'wb')
        for data in res.iter_content(chunk_size):
            downloaded_size += len(data)
            percent = downloaded_size / max_file_bytes * 100
            self._showDownloadProgress(dest_file, percent)
            f.write(data)
        f.close()
    
    def _download_ftp(self, url, dest_file):
        def _report(blocknum, blocksize, totalsize):
            if not totalsize:
                return
            percent = 100.0 * blocknum * blocksize / totalsize
            self._showDownloadProgress(dest_file, percent)
        url = parse.quote(url, safe=':/@')
        request.urlretrieve(url, dest_file, _report)

    def download(self):
        print('Start downloading %s' % self.origin_url)
        normalize_url = self.parseUrlProtrol(self.origin_url)
        print('Parse real url %s' % normalize_url)
        title = self.getTitle(normalize_url)
        dest_file = title
        if self.dest_path:
            if not os.path.exists(self.dest_path):
                os.makedirs(self.dest_path)
            dest_file = os.path.join(self.dest_path, title)
        if os.path.exists(dest_file):
            os.remove(dest_file)

        bt_type = self.detectProtrolType(normalize_url)
        if bt_type in [PROTROL_TYEP.HTTP]:
            self._download_http(normalize_url, dest_file)
        elif bt_type in [PROTROL_TYEP.FTP]:
            self._download_ftp(normalize_url, dest_file)
        else:
            raise Exception('Unknown protrol type detected !')
        print('\nSaved file: %s' % dest_file)
        return

def main():
    if len(sys.argv) not in [2, 3]:
        usage()
    url = sys.argv[1]
    path = None
    if len(sys.argv) > 2:
        path = sys.argv[2]
    bt = BtDown(url, path)
    bt.download()
    print('------------------ Well done ------------------')

if __name__ == '__main__':
    main()
