# -*- coding: utf-8 -*-

'''app/forms/auth.py'''

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import InputRequired, Length


class LoginForm(FlaskForm):
    '''auth.LoginForm(FlaskForm)'''
    name = StringField('姓名', validators=[InputRequired(), Length(1, 64)])
    id_number = StringField('证件号码（后6位）', validators=[InputRequired(), Length(6, 6)])
    auth_token = StringField('授权码', validators=[InputRequired()])
    submit = SubmitField('登录')

    def __init__(self, auth_token_length, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)
        self.auth_token.label.text = '授权码（{}位）'.format(auth_token_length)
        self.auth_token.validators = [InputRequired(), Length(auth_token_length, auth_token_length)]
