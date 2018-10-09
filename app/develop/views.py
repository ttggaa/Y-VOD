# -*- coding: utf-8 -*-

'''app/develop/views.py'''

from htmlmin import minify
from flask import render_template, redirect, request, url_for, abort, current_app
from flask_login import login_required, current_user
from . import develop
from ..decorators import role_required


@develop.route('/configuration')
@login_required
@role_required('开发人员')
def configuration():
    return minify(render_template('develop/configuration.html'))
