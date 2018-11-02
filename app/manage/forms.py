# -*- coding: utf-8 -*-

'''app/manage/forms.py'''

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import InputRequired, Length


class ImportUserForm(FlaskForm):
    '''manage.forms.ImportUserForm(FlaskForm)'''
    token = StringField('用户信息码', validators=[InputRequired()])
    submit = SubmitField('提交')
