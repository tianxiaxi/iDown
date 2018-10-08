#!/usr/bin/env python3
#-*- coding: utf-8 -*-
#pylint: disable=C0103,C0111,C0325,C0703

'''youtube.py - Download video or playlist from Youtube

Usage: python3 youtube.py <url> <type>

Required:
    url         Video url or playlist url
    type        Video type for download, supports webm, mp4, 3gp, flv

Notice: Python3 required for youtube.py

Author: zanran (wayne@zanran.me)
CreatedAt: Sun Jan 28 14:23:33 CST 2018
'''

import os
import sys
import requests
import time
import re
from urllib.parse import urlparse, parse_qs, urljoin
from html.parser import HTMLParser

def usage(err=None):
    if err:
        print(err)
    print(__doc__)
    sys.exit(0)

class PlaylistParser(HTMLParser):
    def __init__(self):
        super(PlaylistParser, self).__init__()
        self.title = None
        self.playlist_url = []
        self.current_tag = None

    def handle_starttag(self, tag, attrs):
        def _attr(attrlist, attrname):
            for attr in attrlist:
                if attr[0] == attrname:
                    return attr[1]
            return None

        self.current_tag = tag
        if tag == 'a':
            _class = _attr(attrs, 'class')
            _href = _attr(attrs, 'href')
            if _class and _class.find('pl-video-title-link') != -1:
                self.playlist_url.append(_href)

    def handle_data(self, data):
        if self.current_tag == 'title' and not self.title:
            pos = data.find(' - YouTube')
            if pos:
                data = data[:pos]
            self.title = data

class Youtube(object):
    def __init__(self, url, media_type):
        self.url = url
        self.media_type = media_type
        self.cur_path = os.path.dirname(os.path.abspath(__file__))
        self.output_path = os.path.join(self.cur_path, 'youtube_download')

    def _get_video_info(self):
        pass

    def start_downloader(self):
        print('Start youtube downloader from %s' % self.url)

        required_url_list = []
        parser = urlparse(self.url)
        if parser.path.upper() == '/WATCH':
            required_url_list.append(self.url)
        elif parser.path.upper() == '/PLAYLIST':
            title = self._parse_playlist(self.url, required_url_list)
            print('Parsing youtube playlist: %s' % title)
        else:
            usage('Invalid youtube video download url: %s' % self.url)

        video_count = len(required_url_list)
        for i, link in enumerate(required_url_list):
            print('[%d/%d] Parse video link: %s' % (i + 1, video_count, link))
            video_info = self._get_video_info(link)
            if not video_info:
                print('  Error: get video info failed')
            (viedo_title, video_download_url) = video_info
            self.download(viedo_title, video_download_url)
            print()

    def _parse_playlist(self, url, required_url_list):
        title = None
        try:
            f = requests.get(url).text
            parser = PlaylistParser()
            parser.feed(f)
            if parser.title:
                title = parser.title
                self.output_path = os.path.join(self.output_path, parser.title)
            for link  in parser.playlist_url:
                required_url_list.append(urljoin(self.url, link))
        except Exception as e:
            usage(e)
        return title

    def _get_video_info(self, video_url):
        title = None
        downloader_url = None

        new_url = '/get_video_info?'
        parser = urlparse(video_url)
        query = parse_qs(parser.query)
        for k, v in query.items():
            if k.lower() == 'v':
                new_url += 'video_id=%s' % v[0]
                break

        new_url = urljoin(self.url, new_url)
        #print('  Get youtube video info from: %s' % new_url)
        try:
            f = requests.get(new_url).text
            video_info = parse_qs(f)
            title = video_info['title'][0]

            url_encoded_fmt_stream_map = video_info['url_encoded_fmt_stream_map'][0].split(',')
            for item in url_encoded_fmt_stream_map:
                dt = parse_qs(item)
                video_type = str(dt['type'])
                if video_type.find(self.media_type) != -1:
                    downloader_url = dt['url'][0]
                    break
            print('  Title: %s' % title)
            #print('  Download url: %s' % downloader_url)
        except Exception as e:
            usage(e)

        return (title, downloader_url)

    def download(self, title, url):
        if not os.path.exists(self.output_path):
            os.makedirs(self.output_path)

        file_name = title + '.' + self.media_type
        file_name = re.sub(r'/|\\', '-', file_name)
        saved_file = os.path.join(self.output_path, file_name)
        if os.path.exists(saved_file):
            print('  Warning: File exists %s' % saved_file)
            return

        res = requests.get(url, stream=True)
        max_file_bytes = int(res.headers['Content-Length'])
 
        chunk_size = 1024*1024*4
        downloaded_size = 0
        f = open(saved_file, 'wb')
        for data in res.iter_content(chunk_size):
            downloaded_size += len(data)
            message = '\r  Downloading %s .......... %02.f%%' % (file_name, downloaded_size / max_file_bytes * 100)
            print(message)
            f.write(data)
        f.close()
        print('\n  Saved file: %s' % os.path.relpath(saved_file, self.cur_path))


def main():
    if len(sys.argv) != 3:
        usage()

    url = sys.argv[1]
    media_type = sys.argv[2]
    if media_type not in ['webm', 'mp4', '3gp', 'flv']:
        usage('Invalid media type')

    youtube = Youtube(url, media_type)
    youtube.start_downloader()
    print('------------------ Well done ------------------')

if __name__ == '__main__':
    main()
