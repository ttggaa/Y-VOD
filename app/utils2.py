# -*- coding: utf-8 -*-

'''app/utils2.py'''

from . import db
from .models import Device, UserLog


def get_device_info(mac_address, show_mac=False):
    '''utils2.get_device_info(mac_address, show_mac=False)'''
    if mac_address is not None:
        device = Device.query.filter_by(mac_address=mac_address).first()
        if device is not None:
            device_info = device.alias
        else:
            device_info = '未授权设备'
        if show_mac:
            return '{} {}'.format(device_info, mac_address)
        return device_info
    return 'N/A'


def add_user_log(user, event, category):
    '''utils2.add_user_log(user, event, category)'''
    user_log = UserLog(user_id=user.id, event=event, category=category)
    db.session.add(user_log)
