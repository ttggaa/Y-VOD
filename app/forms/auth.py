# -*- coding: utf-8 -*-

'''app/forms/auth.py'''

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, Email


class LoginForm(FlaskForm):
    '''auth.LoginForm(FlaskForm)'''
    email = StringField('邮箱', validators=[
        InputRequired(message='请输入您的电子邮箱地址'),
        Length(1, 64),
        Email(message='请输入一个有效的电子邮箱地址'),
    ])
    password = PasswordField('密码', validators=[InputRequired(message='请输入您的密码')])
    submit = SubmitField('登录')
