# -*- coding: utf-8 -*-

'''app/manage/views.py'''

from htmlmin import minify
from flask import render_template, redirect, request, url_for, abort, current_app
from flask_login import login_required, current_user
from . import manage
from ..decorators import permission_required


@manage.route('/student')
@login_required
@permission_required('管理学生')
def student():
    '''manage.student()'''
    return minify(render_template('manage/student.html'))


@manage.route('/staff')
@login_required
@permission_required('管理员工')
def staff():
    '''manage.staff()'''
    return minify(render_template('manage/staff.html'))


@manage.route('/device')
@login_required
@permission_required('管理设备')
def device():
    '''manage.device()'''
    return minify(render_template('manage/device.html'))
