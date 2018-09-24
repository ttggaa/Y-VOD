# -*- coding: utf-8 -*-

import os
import io
import csv
import yaml
from pypinyin import slug, Style
from . import db
from .models import UserLog


class CSVReader:
    def __init__(self, f, dialect=csv.excel, **kwds):
        self.reader = csv.reader(f, dialect=dialect, **kwds)

    def __next__(self):
        row = self.reader.__next__()
        return [(None if v == '' else v) for v in row]

    def __iter__(self):
        return self


class CSVWriter:
    def __init__(self, f, dialect=csv.excel, **kwds):
        self.writer = csv.writer(f, dialect=dialect, **kwds)

    def writerow(self, row):
        self.writer.writerow([('' if v is None else v) for v in row])

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)


def load_yaml(datafile):
    if os.path.exists(datafile):
        with io.open(datafile, 'rt', newline='') as f:
            return yaml.load(f)


def add_user_log(user, event, category):
    user_log = UserLog(user_id=user.id, event=event, category=category)
    db.session.add(user_log)


def to_pinyin(hans, initials=False):
    if initials:
        return slug(hans=hans, style=Style.FIRST_LETTER, separator='', errors='ignore')
    return slug(hans=hans, style=Style.NORMAL, separator='', errors='ignore')
