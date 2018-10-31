# -*- coding: utf-8 -*-

'''app/manage/forms.py'''

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import InputRequired, Length


class ImportUserForm(FlaskForm):
    '''manage.forms.ImportUserForm(FlaskForm)'''
    token = StringField('用户信息码', validators=[InputRequired()])
    submit = SubmitField('提交')

    def __init__(self, category, *args, **kwargs):
        super(ImportUserForm, self).__init__(*args, **kwargs)
        self.token.label.text = '{}用户信息码'.format(category)
