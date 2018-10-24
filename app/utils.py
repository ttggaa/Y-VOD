# -*- coding: utf-8 -*-

'''app/utils.py'''

import os
import io
from datetime import datetime, timedelta
import csv
import yaml
from pymediainfo import MediaInfo
from flask import stream_with_context, Response
from pypinyin import slug, Style


def datetime_now(utc_offset=0):
    return datetime.utcnow() + timedelta(hours=utc_offset)


def date_now(utc_offset=0):
    return datetime_now(utc_offset=utc_offset).date()


class CSVReader:
    '''CSVReader'''
    def __init__(self, f, dialect=csv.excel, **kwds):
        self.reader = csv.reader(f, dialect=dialect, **kwds)

    def __next__(self):
        row = self.reader.__next__()
        return [(None if v == '' else v) for v in row]

    def __iter__(self):
        return self


class CSVWriter:
    '''CSVWriter'''
    def __init__(self, f, dialect=csv.excel, **kwds):
        self.writer = csv.writer(f, dialect=dialect, **kwds)

    def writerow(self, row):
        '''writerow(self, row)'''
        self.writer.writerow([('' if v is None else v) for v in row])

    def writerows(self, rows):
        '''writerows(self, rows)'''
        for row in rows:
            self.writerow(row)


def load_yaml(yaml_file):
    '''load_yaml(yaml_file)'''
    if os.path.exists(yaml_file):
        with io.open(yaml_file, 'rt', newline='') as f:
            return yaml.load(f)
    return '{} does not exist.'.format(yaml_file)


def get_video_duration(video_file):
    '''get_video_duration(video_file)'''
    if os.path.exists(video_file):
        media_info = MediaInfo.parse(video_file)
        return timedelta(milliseconds=media_info.tracks[0].duration)
    return '{} does not exist.'.format(video_file)


def stream_video(video_file, mimetype='video/mp4', chunk_size=1024*1024):
    '''stream_video(video_file, mimetype='video/mp4', chunk_size=1024*1024)'''
    def generator():
        with io.open(video_file, 'rb') as f:
            while True:
                chunk = f.read(chunk_size)
                if chunk:
                    yield chunk
                else:
                    break
    return Response(stream_with_context(generator()), mimetype=mimetype, direct_passthrough=True)


def format_duration(duration):
    '''format_duration(duration)'''
    hours, duration = divmod(duration, timedelta(hours=1))
    minutes, duration = divmod(duration, timedelta(minutes=1))
    return '{:02.0f}:{:02.0f}:{:02.0f}'.format(hours, minutes, duration.total_seconds())


def to_pinyin(hans, initials=False):
    '''to_pinyin(hans, initials=False)'''
    if initials:
        return slug(hans=hans, style=Style.FIRST_LETTER, separator='', errors='ignore')
    return slug(hans=hans, style=Style.NORMAL, separator='', errors='ignore')
