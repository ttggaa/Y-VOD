# -*- coding: utf-8 -*-

'''app/utils.py'''

import os
import io
from datetime import timedelta
import csv
import yaml
from pymediainfo import MediaInfo
from pypinyin import slug, Style
from . import db
from .models import UserLog


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


def to_pinyin(hans, initials=False):
    '''to_pinyin(hans, initials=False)'''
    if initials:
        return slug(hans=hans, style=Style.FIRST_LETTER, separator='', errors='ignore')
    return slug(hans=hans, style=Style.NORMAL, separator='', errors='ignore')


def add_user_log(user, event, category):
    '''add_user_log(user, event, category)'''
    user_log = UserLog(user_id=user.id, event=event, category=category)
    db.session.add(user_log)
