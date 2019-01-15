# -*- coding: utf-8 -*-

'''app/views/develop.py'''

from htmlmin import minify
from flask import Blueprint, render_template, redirect, request, make_response, url_for, current_app
from flask_login import login_required, current_user
from app.models import Role
from app.models import Permission
from app.models import UserLog
from app.decorators import role_required


develop = Blueprint('develop', __name__)


@develop.route('/role')
@login_required
@role_required('开发人员')
def role():
    '''develop.role()'''
    query = Role.query.order_by(Role.id.asc())
    page = request.args.get('page', 1, type=int)
    pagination = query.paginate(page, per_page=current_app.config['RECORD_PER_PAGE'], error_out=False)
    roles = pagination.items
    return minify(render_template(
        'develop/role.html',
        pagination=pagination,
        roles=roles
    ))


@develop.route('/permission')
@login_required
@role_required('开发人员')
def permission():
    '''develop.permission()'''
    query = Permission.query.order_by(Permission.id.asc())
    page = request.args.get('page', 1, type=int)
    pagination = query.paginate(page, per_page=current_app.config['RECORD_PER_PAGE'], error_out=False)
    permissions = pagination.items
    return minify(render_template(
        'develop/permission.html',
        pagination=pagination,
        permissions=permissions
    ))


@develop.route('/log')
@login_required
@role_required('开发人员')
def log():
    '''develop.log()'''
    show_all_logs = True
    show_study_logs = False
    show_manage_logs = False
    show_auth_logs = False
    show_access_logs = False
    if current_user.is_authenticated:
        show_all_logs = bool(request.cookies.get('show_all_logs', '1'))
        show_study_logs = bool(request.cookies.get('show_study_logs', ''))
        show_manage_logs = bool(request.cookies.get('show_manage_logs', ''))
        show_auth_logs = bool(request.cookies.get('show_auth_logs', ''))
        show_access_logs = bool(request.cookies.get('show_access_logs', ''))
    if show_all_logs:
        query = UserLog.query\
            .order_by(UserLog.timestamp.desc())
    if show_study_logs:
        query = UserLog.query\
            .filter(UserLog.category == 'study')\
            .order_by(UserLog.timestamp.desc())
    if show_manage_logs:
        query = UserLog.query\
            .filter(UserLog.category == 'manage')\
            .order_by(UserLog.timestamp.desc())
    if show_auth_logs:
        query = UserLog.query\
            .filter(UserLog.category == 'auth')\
            .order_by(UserLog.timestamp.desc())
    if show_access_logs:
        query = UserLog.query\
            .filter(UserLog.category == 'access')\
            .order_by(UserLog.timestamp.desc())
    page = request.args.get('page', 1, type=int)
    try:
        pagination = query.paginate(page, per_page=current_app.config['RECORD_PER_PAGE'], error_out=False)
    except NameError:
        return redirect(url_for('develop.all_logs'))
    logs = pagination.items
    return minify(render_template(
        'develop/log.html',
        show_all_logs=show_all_logs,
        show_study_logs=show_study_logs,
        show_manage_logs=show_manage_logs,
        show_auth_logs=show_auth_logs,
        show_access_logs=show_access_logs,
        pagination=pagination,
        logs=logs
    ))


@develop.route('/log/all')
@login_required
@role_required('开发人员')
def all_logs():
    '''develop.all_logs()'''
    resp = make_response(redirect(url_for('develop.log')))
    resp.set_cookie('show_all_logs', '1', max_age=current_app.config['COOKIE_MAX_AGE'])
    resp.set_cookie('show_study_logs', '', max_age=current_app.config['COOKIE_MAX_AGE'])
    resp.set_cookie('show_manage_logs', '', max_age=current_app.config['COOKIE_MAX_AGE'])
    resp.set_cookie('show_auth_logs', '', max_age=current_app.config['COOKIE_MAX_AGE'])
    resp.set_cookie('show_access_logs', '', max_age=current_app.config['COOKIE_MAX_AGE'])
    return resp


@develop.route('/log/study')
@login_required
@role_required('开发人员')
def study_logs():
    '''develop.study_logs()'''
    resp = make_response(redirect(url_for('develop.log')))
    resp.set_cookie('show_all_logs', '', max_age=current_app.config['COOKIE_MAX_AGE'])
    resp.set_cookie('show_study_logs', '1', max_age=current_app.config['COOKIE_MAX_AGE'])
    resp.set_cookie('show_manage_logs', '', max_age=current_app.config['COOKIE_MAX_AGE'])
    resp.set_cookie('show_auth_logs', '', max_age=current_app.config['COOKIE_MAX_AGE'])
    resp.set_cookie('show_access_logs', '', max_age=current_app.config['COOKIE_MAX_AGE'])
    return resp


@develop.route('/log/manage')
@login_required
@role_required('开发人员')
def manage_logs():
    '''develop.manage_logs()'''
    resp = make_response(redirect(url_for('develop.log')))
    resp.set_cookie('show_all_logs', '', max_age=current_app.config['COOKIE_MAX_AGE'])
    resp.set_cookie('show_study_logs', '', max_age=current_app.config['COOKIE_MAX_AGE'])
    resp.set_cookie('show_manage_logs', '1', max_age=current_app.config['COOKIE_MAX_AGE'])
    resp.set_cookie('show_auth_logs', '', max_age=current_app.config['COOKIE_MAX_AGE'])
    resp.set_cookie('show_access_logs', '', max_age=current_app.config['COOKIE_MAX_AGE'])
    return resp


@develop.route('/log/auth')
@login_required
@role_required('开发人员')
def auth_logs():
    '''develop.auth_logs()'''
    resp = make_response(redirect(url_for('develop.log')))
    resp.set_cookie('show_all_logs', '', max_age=current_app.config['COOKIE_MAX_AGE'])
    resp.set_cookie('show_study_logs', '', max_age=current_app.config['COOKIE_MAX_AGE'])
    resp.set_cookie('show_manage_logs', '', max_age=current_app.config['COOKIE_MAX_AGE'])
    resp.set_cookie('show_auth_logs', '1', max_age=current_app.config['COOKIE_MAX_AGE'])
    resp.set_cookie('show_access_logs', '', max_age=current_app.config['COOKIE_MAX_AGE'])
    return resp


@develop.route('/log/access')
@login_required
@role_required('开发人员')
def access_logs():
    '''develop.access_logs()'''
    resp = make_response(redirect(url_for('develop.log')))
    resp.set_cookie('show_all_logs', '', max_age=current_app.config['COOKIE_MAX_AGE'])
    resp.set_cookie('show_study_logs', '', max_age=current_app.config['COOKIE_MAX_AGE'])
    resp.set_cookie('show_manage_logs', '', max_age=current_app.config['COOKIE_MAX_AGE'])
    resp.set_cookie('show_auth_logs', '', max_age=current_app.config['COOKIE_MAX_AGE'])
    resp.set_cookie('show_access_logs', '1', max_age=current_app.config['COOKIE_MAX_AGE'])
    return resp


@develop.route('/configuration')
@login_required
@role_required('开发人员')
def configuration():
    '''develop.configuration()'''
    return minify(render_template('develop/configuration.html'))
