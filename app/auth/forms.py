# -*- coding: utf-8 -*-

'''app/auth/forms.py'''

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import InputRequired, Length


class LoginForm(FlaskForm):
    '''auth.forms.LoginForm(FlaskForm)'''
    name = StringField('姓名', validators=[InputRequired(), Length(1, 64)])
    id_number = StringField('证件号码（后6位）', validators=[InputRequired(), Length(6, 6)])
    auth_token = StringField('授权码（6位）', validators=[InputRequired(), Length(6, 6)])
    submit = SubmitField('登录')
