# -*- coding: utf-8 -*-

'''app/forms/manage.py'''

from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, SelectField, SelectMultipleField, SubmitField
from wtforms.validators import InputRequired, Optional, MacAddress
from app.models import Room, DeviceType
from app.models import LessonType


class DeviceForm(FlaskForm):
    '''manage.DeviceForm(FlaskForm)'''
    alias = StringField('设备名', validators=[InputRequired()])
    serial = StringField('序列号', validators=[InputRequired()])
    device_type = SelectField('设备类型', coerce=str, validators=[InputRequired()])
    room = SelectField('所属场地', coerce=str, validators=[InputRequired()])
    mac_address = StringField('MAC地址', validators=[Optional(), MacAddress()])
    lesson_types = SelectMultipleField('授权课程类型', coerce=str)
    development_machine = BooleanField('开发用机器')
    submit = SubmitField('提交')

    def __init__(self, is_developer, *args, **kwargs):
        super(DeviceForm, self).__init__(*args, **kwargs)
        if is_developer:
            self.device_type.choices = [('', '选择设备类型')] + \
                [(str(device_type.id), device_type.name) \
                for device_type in DeviceType.query.order_by(DeviceType.id.asc()).all()]
        else:
            self.device_type.choices = [('', '选择设备类型')] + \
                [(str(device_type.id), device_type.name) for device_type in DeviceType.query\
                    .filter(DeviceType.name != 'Server')\
                    .order_by(DeviceType.id.asc())\
                    .all()]
        self.room.choices = [('', '选择所属场地')] + [('0', '无')] + \
            [(str(room.id), room.name) for room in Room.query.order_by(Room.id.asc()).all()]
        self.lesson_types.choices = [('', '选择授权课程类型')] + \
            [(str(lesson_type.id), lesson_type.name) for lesson_type in LessonType.query.all()]
