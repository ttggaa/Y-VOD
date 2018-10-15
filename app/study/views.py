# -*- coding: utf-8 -*-

'''app/study/views.py'''

from htmlmin import minify
from flask import render_template, redirect, request, url_for, abort, current_app
from flask_login import login_required, current_user
from . import study
from ..decorators import permission_required


@study.route('/vb')
@login_required
def vb():
    '''study.vb()'''
    return minify(render_template('study/vb.html'))


@study.route('/y-gre')
@login_required
def y_gre():
    '''study.y_gre()'''
    return minify(render_template('study/y_gre.html'))
