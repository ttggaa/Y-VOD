# -*- coding: utf-8 -*-

'''app/utils.py'''

import os
import io
import re
import operator
from functools import reduce
from shutil import rmtree
from datetime import datetime, timedelta
from json import JSONDecodeError
import csv
import yaml
from getmac import get_mac_address
from pymediainfo import MediaInfo
import requests
from requests.exceptions import RequestException
from itsdangerous import TimedJSONWebSignatureSerializer
from flask import Response
from flask import current_app
from pypinyin import slug, Style


def makedirs(path, overwrite=False):
    '''utils.makedirs(path, overwrite=False)'''
    if overwrite and os.path.exists(path):
        rmtree(path)
    if not os.path.exists(path):
        os.makedirs(path)


def datetime_now(utc_offset=0):
    '''utils.datetime_now(utc_offset=0)'''
    return datetime.utcnow() + timedelta(hours=utc_offset)


def date_now(utc_offset=0):
    '''utils.date_now(utc_offset=0)'''
    return datetime_now(utc_offset=utc_offset).date()


def datetime_then(timestamp, utc_offset=0):
    '''utils.datetime_then(timestamp, utc_offset=0)'''
    return timestamp + timedelta(hours=utc_offset)


def date_then(timestamp, utc_offset=0):
    '''utils.date_then(timestamp, utc_offset=0)'''
    return datetime_then(timestamp=timestamp, utc_offset=utc_offset).date()


class CSVReader:
    '''utils.CSVReader'''
    def __init__(self, f, dialect=csv.excel, **kwds):
        self.reader = csv.reader(f, dialect=dialect, **kwds)

    def __next__(self):
        row = self.reader.__next__()
        return [(None if v == '' else v) for v in row]

    def __iter__(self):
        return self


class CSVWriter:
    '''utils.CSVWriter'''
    def __init__(self, f, dialect=csv.excel, **kwds):
        self.writer = csv.writer(f, dialect=dialect, **kwds)

    def writerow(self, row):
        '''CSVWriter.writerow(self, row)'''
        self.writer.writerow([('' if v is None else v) for v in row])

    def writerows(self, rows):
        '''CSVWriter.writerows(self, rows)'''
        for row in rows:
            self.writerow(row)


def load_yaml(yaml_file):
    '''utils.load_yaml(yaml_file)'''
    if os.path.exists(yaml_file):
        with io.open(yaml_file, 'rt', newline='') as f:
            return yaml.load(f)
    return None


def get_mac_address_from_ip(ip_address):
    '''utils.get_mac_address_from_ip(ip_address)'''
    if ip_address is None:
        return None
    if ip_address == '127.0.0.1':
        mac_address = get_mac_address()
    else:
        mac_address = get_mac_address(ip=ip_address)
    if mac_address is not None:
        return mac_address.upper()
    return None


def get_video_duration(video_file):
    '''utils.get_video_duration(video_file)'''
    if os.path.exists(video_file):
        media_info = MediaInfo.parse(video_file)
        return timedelta(milliseconds=media_info.tracks[0].duration)
    return None


def send_video_file(video_file, request, mimetype='video/mp4'):
    '''utils.send_video_file(video_file, request, mimetype='video/mp4')'''
    file_size = os.path.getsize(video_file)
    m = re.match(r'bytes=(?P<start>\d+)-(?P<end>\d+)?', request.headers.get('Range'))
    if m:
        start = m.group('start')
        end = m.group('end')
        start = int(start)
        end = (file_size - 1) if end is None else min(int(end), file_size - 1)
    else:
        start = 0
        end = file_size - 1
    length = end - start + 1
    with open(video_file, 'rb') as f:
        f.seek(start)
        video_file_chunk = f.read(length)
    resp = Response(
        response=video_file_chunk,
        status=206,
        mimetype=mimetype,
        direct_passthrough=True
    )
    resp.headers['Content-Range'] = 'bytes {}-{}/{}'.format(start, end, file_size)
    resp.headers['Accept-Ranges'] = 'bytes'
    return resp


def format_duration(duration):
    '''utils.format_duration(duration)'''
    hours, duration = divmod(duration, timedelta(hours=1))
    minutes, duration = divmod(duration, timedelta(minutes=1))
    return '{:02.0f}:{:02.0f}:{:02.0f}'.format(hours, minutes, duration.total_seconds())


def y_system_api_request(api, token_data):
    '''utils.y_system_api_request(api, token_data)'''
    serial = TimedJSONWebSignatureSerializer(
        secret_key=current_app.config['AUTH_TOKEN_SECRET_KEY'],
        expires_in=current_app.config['TOKEN_EXPIRATION']
    )
    try:
        api_request = requests.get('{}/api/{}/{}'.format(
            current_app.config['YSYS_URI'],
            api,
            serial.dumps(token_data).decode('ascii')
        ), timeout=current_app.config['REQUEST_TIMEOUT'])
        data = api_request.json()
    except (RequestException, JSONDecodeError):
        data = None
    return data


def verify_data_keys(data, keys):
    '''utils.verify_data_keys(data, keys)'''
    return data is not None and \
        reduce(operator.and_, [data.get(key) is not None for key in keys])


def to_pinyin(hans, initials=False):
    '''utils.to_pinyin(hans, initials=False)'''
    if initials:
        return slug(hans=hans, style=Style.FIRST_LETTER, separator='', errors='ignore')
    return slug(hans=hans, style=Style.NORMAL, separator='', errors='ignore')
