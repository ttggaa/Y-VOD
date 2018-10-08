# -*- coding: utf-8 -*-

'''app/tasks.py'''

from . import db
from .models import UserLog


def add_user_log(user, event, category):
    '''add_user_log(user, event, category)'''
    user_log = UserLog(user_id=user.id, event=event, category=category)
    db.session.add(user_log)
