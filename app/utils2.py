# -*- coding: utf-8 -*-

'''app/tasks.py'''

from . import db
from .models import Device, UserLog


def get_device_info(ip_address, show_ip=False):
    '''get_device_info(ip_address, show_ip=False)'''
    if ip_address is not None:
        device = Device.query.filter_by(ip_address=ip_address).first()
        if device is not None:
            device_info = device.alias
        else:
            device_info = '未授权设备'
        if show_ip:
            return '{} {}'.format(device_info, ip_address)
        return device_info
    return 'N/A'


def add_user_log(user, event, category):
    '''add_user_log(user, event, category)'''
    user_log = UserLog(user_id=user.id, event=event, category=category)
    db.session.add(user_log)
