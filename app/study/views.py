# -*- coding: utf-8 -*-

'''app/study/views.py'''

from htmlmin import minify
from flask import render_template, redirect, request, url_for, abort, current_app
from flask_login import login_required, current_user
from . import study
from ..decorators import permission_required


@study.route('/')
@login_required
def home():
    '''study.home()'''
    return minify(render_template('study/home.html'))
