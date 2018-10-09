# -*- coding: utf-8 -*-

'''app/status/views.py'''

from htmlmin import minify
from flask import render_template, redirect, request, url_for, abort, current_app
from flask_login import login_required, current_user
from . import status
from ..decorators import permission_required


@status.route('/')
@login_required
@permission_required('管理')
def home():
    '''status.home()'''
    return minify(render_template('status/home.html'))
