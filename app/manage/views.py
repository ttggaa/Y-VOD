# -*- coding: utf-8 -*-

'''app/manage/views.py'''

from htmlmin import minify
from flask import render_template, redirect, request, make_response, url_for, abort, current_app
from flask_login import login_required, current_user
from . import manage
from ..models import Role, User
from ..models import DeviceType, Device
from ..decorators import permission_required, role_required


@manage.route('/student')
@login_required
@permission_required('管理学生')
def student():
    '''manage.student()'''
    show_vb_students = True
    show_y_gre_students = False
    show_suspended_students = False
    if current_user.is_authenticated:
        show_vb_students = bool(request.cookies.get('show_vb_students', '1'))
        show_y_gre_students = bool(request.cookies.get('show_y_gre_students', ''))
        show_suspended_students = bool(request.cookies.get('show_suspended_students', ''))
    if show_vb_students:
        header = 'VB研修'
        query = User.query\
            .join(Role, Role.id == User.role_id)\
            .filter(Role.name == 'VB研修')\
            .filter(User.suspended == False)\
            .order_by(User.last_seen_at.desc())
    if show_y_gre_students:
        header = 'Y-GRE研修'
        query = User.query\
            .join(Role, Role.id == User.role_id)\
            .filter(Role.name == 'Y-GRE研修')\
            .filter(User.suspended == False)\
            .order_by(User.last_seen_at.desc())
    if show_suspended_students:
        header = '挂起'
        query = User.query\
            .join(Role, Role.id == User.role_id)\
            .filter(Role.category == 'student')\
            .filter(User.suspended == True)\
            .order_by(User.last_seen_at.desc())
    page = request.args.get('page', 1, type=int)
    try:
        pagination = query.paginate(page, per_page=current_app.config['RECORD_PER_PAGE'], error_out=False)
    except NameError:
        return redirect(url_for('manage.vb_students'))
    users = pagination.items
    return minify(render_template(
        'manage/student.html',
        header=header,
        show_vb_students=show_vb_students,
        show_y_gre_students=show_y_gre_students,
        show_suspended_students=show_suspended_students,
        pagination=pagination,
        users=users
    ))


@manage.route('/student/vb')
@login_required
@permission_required('管理学生')
def vb_students():
    '''manage.vb_students()'''
    resp = make_response(redirect(url_for('manage.student')))
    resp.set_cookie('show_vb_students', '1', max_age=current_app.config['COOKIE_MAX_AGE'])
    resp.set_cookie('show_y_gre_students', '', max_age=current_app.config['COOKIE_MAX_AGE'])
    resp.set_cookie('show_suspended_students', '', max_age=current_app.config['COOKIE_MAX_AGE'])
    return resp


@manage.route('/student/y-gre')
@login_required
@permission_required('管理学生')
def y_gre_students():
    '''manage.y_gre_students()'''
    resp = make_response(redirect(url_for('manage.student')))
    resp.set_cookie('show_vb_students', '', max_age=current_app.config['COOKIE_MAX_AGE'])
    resp.set_cookie('show_y_gre_students', '1', max_age=current_app.config['COOKIE_MAX_AGE'])
    resp.set_cookie('show_suspended_students', '', max_age=current_app.config['COOKIE_MAX_AGE'])
    return resp


@manage.route('/student/suspended')
@login_required
@permission_required('管理学生')
def suspended_students():
    '''manage.suspended_students()'''
    resp = make_response(redirect(url_for('manage.student')))
    resp.set_cookie('show_vb_students', '', max_age=current_app.config['COOKIE_MAX_AGE'])
    resp.set_cookie('show_y_gre_students', '', max_age=current_app.config['COOKIE_MAX_AGE'])
    resp.set_cookie('show_suspended_students', '1', max_age=current_app.config['COOKIE_MAX_AGE'])
    return resp


@manage.route('/staff')
@login_required
@permission_required('管理员工')
def staff():
    '''manage.staff()'''
    show_clerks = True
    show_assistants = False
    show_consultants = False
    show_coordinators = False
    show_moderators = False
    show_administrators = False
    show_developers = False
    show_suspended_staffs = False
    if current_user.is_authenticated:
        show_clerks = bool(request.cookies.get('show_clerks', '1'))
        show_assistants = bool(request.cookies.get('show_assistants', ''))
        show_consultants = bool(request.cookies.get('show_consultants', ''))
        show_coordinators = bool(request.cookies.get('show_coordinators', ''))
        show_moderators = bool(request.cookies.get('show_moderators', ''))
        show_administrators = bool(request.cookies.get('show_administrators', ''))
        show_developers = bool(request.cookies.get('show_developers', ''))
        show_suspended_staffs = bool(request.cookies.get('show_suspended_staffs', ''))
    if show_clerks:
        header = '值守'
        query = User.query\
            .join(Role, Role.id == User.role_id)\
            .filter(Role.name == '值守')\
            .filter(User.suspended == False)\
            .order_by(User.last_seen_at.desc())
    if show_assistants:
        header = '行政辅助'
        query = User.query\
            .join(Role, Role.id == User.role_id)\
            .filter(Role.name == '行政辅助')\
            .filter(User.suspended == False)\
            .order_by(User.last_seen_at.desc())
    if show_consultants:
        header = '学术答疑'
        query = User.query\
            .join(Role, Role.id == User.role_id)\
            .filter(Role.name == '学术答疑')\
            .filter(User.suspended == False)\
            .order_by(User.last_seen_at.desc())
    if show_coordinators:
        header = '协调员'
        query = User.query\
            .join(Role, Role.id == User.role_id)\
            .filter(Role.name == '协调员')\
            .filter(User.suspended == False)\
            .order_by(User.last_seen_at.desc())
    if show_moderators:
        header = '协管员'
        query = User.query\
            .join(Role, Role.id == User.role_id)\
            .filter(Role.name == '协管员')\
            .filter(User.suspended == False)\
            .order_by(User.last_seen_at.desc())
    if show_administrators:
        if current_user.plays('管理员'):
            header = '管理员'
            query = User.query\
                .join(Role, Role.id == User.role_id)\
                .filter(Role.name == '管理员')\
                .filter(User.suspended == False)\
                .order_by(User.last_seen_at.desc())
        else:
            return redirect(url_for('manage.clerks'))
    if show_developers:
        if current_user.is_developer:
            header = '开发人员'
            query = User.query\
                .join(Role, Role.id == User.role_id)\
                .filter(Role.name == '开发人员')\
                .filter(User.suspended == False)\
                .order_by(User.last_seen_at.desc())
        else:
            return redirect(url_for('manage.clerks'))
    if show_suspended_staffs:
        header = '挂起'
        query = User.query\
            .join(Role, Role.id == User.role_id)\
            .filter(Role.category == 'staff')\
            .filter(User.suspended == True)\
            .filter(Role.level <= current_user.role.level)\
            .order_by(User.last_seen_at.desc())
    page = request.args.get('page', 1, type=int)
    try:
        pagination = query.paginate(page, per_page=current_app.config['RECORD_PER_PAGE'], error_out=False)
    except NameError:
        return redirect(url_for('manage.clerks'))
    users = pagination.items
    return minify(render_template(
        'manage/staff.html',
        header=header,
        show_clerks=show_clerks,
        show_assistants=show_assistants,
        show_consultants=show_consultants,
        show_coordinators=show_coordinators,
        show_moderators=show_moderators,
        show_administrators=show_administrators,
        show_developers=show_developers,
        show_suspended_staffs=show_suspended_staffs,
        pagination=pagination,
        users=users
    ))


@manage.route('/staff/clerk')
@login_required
@permission_required('管理员工')
def clerks():
    '''manage.clerks()'''
    resp = make_response(redirect(url_for('manage.staff')))
    resp.set_cookie('show_clerks', '1', max_age=current_app.config['COOKIE_MAX_AGE'])
    resp.set_cookie('show_assistants', '', max_age=current_app.config['COOKIE_MAX_AGE'])
    resp.set_cookie('show_consultants', '', max_age=current_app.config['COOKIE_MAX_AGE'])
    resp.set_cookie('show_coordinators', '', max_age=current_app.config['COOKIE_MAX_AGE'])
    resp.set_cookie('show_moderators', '', max_age=current_app.config['COOKIE_MAX_AGE'])
    resp.set_cookie('show_administrators', '', max_age=current_app.config['COOKIE_MAX_AGE'])
    resp.set_cookie('show_developers', '', max_age=current_app.config['COOKIE_MAX_AGE'])
    resp.set_cookie('show_suspended_staffs', '', max_age=current_app.config['COOKIE_MAX_AGE'])
    return resp


@manage.route('/staff/assistant')
@login_required
@permission_required('管理员工')
def assistants():
    '''manage.assistants()'''
    resp = make_response(redirect(url_for('manage.staff')))
    resp.set_cookie('show_clerks', '', max_age=current_app.config['COOKIE_MAX_AGE'])
    resp.set_cookie('show_assistants', '1', max_age=current_app.config['COOKIE_MAX_AGE'])
    resp.set_cookie('show_consultants', '', max_age=current_app.config['COOKIE_MAX_AGE'])
    resp.set_cookie('show_coordinators', '', max_age=current_app.config['COOKIE_MAX_AGE'])
    resp.set_cookie('show_moderators', '', max_age=current_app.config['COOKIE_MAX_AGE'])
    resp.set_cookie('show_administrators', '', max_age=current_app.config['COOKIE_MAX_AGE'])
    resp.set_cookie('show_developers', '', max_age=current_app.config['COOKIE_MAX_AGE'])
    resp.set_cookie('show_suspended_staffs', '', max_age=current_app.config['COOKIE_MAX_AGE'])
    return resp


@manage.route('/staff/consultant')
@login_required
@permission_required('管理员工')
def consultants():
    '''manage.consultants()'''
    resp = make_response(redirect(url_for('manage.staff')))
    resp.set_cookie('show_clerks', '', max_age=current_app.config['COOKIE_MAX_AGE'])
    resp.set_cookie('show_assistants', '', max_age=current_app.config['COOKIE_MAX_AGE'])
    resp.set_cookie('show_consultants', '1', max_age=current_app.config['COOKIE_MAX_AGE'])
    resp.set_cookie('show_coordinators', '', max_age=current_app.config['COOKIE_MAX_AGE'])
    resp.set_cookie('show_moderators', '', max_age=current_app.config['COOKIE_MAX_AGE'])
    resp.set_cookie('show_administrators', '', max_age=current_app.config['COOKIE_MAX_AGE'])
    resp.set_cookie('show_developers', '', max_age=current_app.config['COOKIE_MAX_AGE'])
    resp.set_cookie('show_suspended_staffs', '', max_age=current_app.config['COOKIE_MAX_AGE'])
    return resp


@manage.route('/staff/coordinator')
@login_required
@permission_required('管理员工')
def coordinators():
    '''manage.coordinators()'''
    resp = make_response(redirect(url_for('manage.staff')))
    resp.set_cookie('show_clerks', '', max_age=current_app.config['COOKIE_MAX_AGE'])
    resp.set_cookie('show_assistants', '', max_age=current_app.config['COOKIE_MAX_AGE'])
    resp.set_cookie('show_consultants', '', max_age=current_app.config['COOKIE_MAX_AGE'])
    resp.set_cookie('show_coordinators', '1', max_age=current_app.config['COOKIE_MAX_AGE'])
    resp.set_cookie('show_moderators', '', max_age=current_app.config['COOKIE_MAX_AGE'])
    resp.set_cookie('show_administrators', '', max_age=current_app.config['COOKIE_MAX_AGE'])
    resp.set_cookie('show_developers', '', max_age=current_app.config['COOKIE_MAX_AGE'])
    resp.set_cookie('show_suspended_staffs', '', max_age=current_app.config['COOKIE_MAX_AGE'])
    return resp


@manage.route('/staff/moderator')
@login_required
@role_required('协管员')
def moderators():
    '''manage.moderators()'''
    resp = make_response(redirect(url_for('manage.staff')))
    resp.set_cookie('show_clerks', '', max_age=current_app.config['COOKIE_MAX_AGE'])
    resp.set_cookie('show_assistants', '', max_age=current_app.config['COOKIE_MAX_AGE'])
    resp.set_cookie('show_consultants', '', max_age=current_app.config['COOKIE_MAX_AGE'])
    resp.set_cookie('show_coordinators', '', max_age=current_app.config['COOKIE_MAX_AGE'])
    resp.set_cookie('show_moderators', '1', max_age=current_app.config['COOKIE_MAX_AGE'])
    resp.set_cookie('show_administrators', '', max_age=current_app.config['COOKIE_MAX_AGE'])
    resp.set_cookie('show_developers', '', max_age=current_app.config['COOKIE_MAX_AGE'])
    resp.set_cookie('show_suspended_staffs', '', max_age=current_app.config['COOKIE_MAX_AGE'])
    return resp


@manage.route('/staff/administrator')
@login_required
@role_required('管理员')
def administrators():
    '''manage.administrators()'''
    resp = make_response(redirect(url_for('manage.staff')))
    resp.set_cookie('show_clerks', '', max_age=current_app.config['COOKIE_MAX_AGE'])
    resp.set_cookie('show_assistants', '', max_age=current_app.config['COOKIE_MAX_AGE'])
    resp.set_cookie('show_consultants', '', max_age=current_app.config['COOKIE_MAX_AGE'])
    resp.set_cookie('show_coordinators', '', max_age=current_app.config['COOKIE_MAX_AGE'])
    resp.set_cookie('show_moderators', '', max_age=current_app.config['COOKIE_MAX_AGE'])
    resp.set_cookie('show_administrators', '1', max_age=current_app.config['COOKIE_MAX_AGE'])
    resp.set_cookie('show_developers', '', max_age=current_app.config['COOKIE_MAX_AGE'])
    resp.set_cookie('show_suspended_staffs', '', max_age=current_app.config['COOKIE_MAX_AGE'])
    return resp


@manage.route('/staff/developer')
@login_required
@role_required('开发人员')
def developers():
    '''manage.developers()'''
    resp = make_response(redirect(url_for('manage.staff')))
    resp.set_cookie('show_clerks', '', max_age=current_app.config['COOKIE_MAX_AGE'])
    resp.set_cookie('show_assistants', '', max_age=current_app.config['COOKIE_MAX_AGE'])
    resp.set_cookie('show_consultants', '', max_age=current_app.config['COOKIE_MAX_AGE'])
    resp.set_cookie('show_coordinators', '', max_age=current_app.config['COOKIE_MAX_AGE'])
    resp.set_cookie('show_moderators', '', max_age=current_app.config['COOKIE_MAX_AGE'])
    resp.set_cookie('show_administrators', '', max_age=current_app.config['COOKIE_MAX_AGE'])
    resp.set_cookie('show_developers', '1', max_age=current_app.config['COOKIE_MAX_AGE'])
    resp.set_cookie('show_suspended_staffs', '', max_age=current_app.config['COOKIE_MAX_AGE'])
    return resp


@manage.route('/staff/suspended')
@login_required
@permission_required('管理员工')
def suspended_staffs():
    '''manage.suspended_staffs()'''
    resp = make_response(redirect(url_for('manage.staff')))
    resp.set_cookie('show_clerks', '', max_age=current_app.config['COOKIE_MAX_AGE'])
    resp.set_cookie('show_assistants', '', max_age=current_app.config['COOKIE_MAX_AGE'])
    resp.set_cookie('show_consultants', '', max_age=current_app.config['COOKIE_MAX_AGE'])
    resp.set_cookie('show_coordinators', '', max_age=current_app.config['COOKIE_MAX_AGE'])
    resp.set_cookie('show_moderators', '', max_age=current_app.config['COOKIE_MAX_AGE'])
    resp.set_cookie('show_administrators', '', max_age=current_app.config['COOKIE_MAX_AGE'])
    resp.set_cookie('show_developers', '', max_age=current_app.config['COOKIE_MAX_AGE'])
    resp.set_cookie('show_suspended_staffs', '1', max_age=current_app.config['COOKIE_MAX_AGE'])
    return resp


@manage.route('/device')
@login_required
@permission_required('管理设备')
def device():
    '''manage.device()'''
    show_tablet_devices = True
    show_desktop_devices = False
    show_mobile_devices = False
    show_development_devices = False
    show_obsolete_devices = False
    if current_user.is_authenticated:
        show_tablet_devices = bool(request.cookies.get('show_tablet_devices', '1'))
        show_desktop_devices = bool(request.cookies.get('show_desktop_devices', ''))
        show_mobile_devices = bool(request.cookies.get('show_mobile_devices', ''))
        show_development_devices = bool(request.cookies.get('show_development_devices', ''))
        show_obsolete_devices = bool(request.cookies.get('show_obsolete_devices', ''))
    if show_tablet_devices:
        header = '平板设备'
        query = Device.query\
            .join(DeviceType, DeviceType.id == Device.type_id)\
            .filter(DeviceType.name == 'Tablet')\
            .filter(Device.category == 'production')\
            .filter(Device.obsolete == False)\
            .order_by(Device.alias.asc())
    if show_desktop_devices:
        header = '桌面设备'
        query = Device.query\
            .join(DeviceType, DeviceType.id == Device.type_id)\
            .filter(DeviceType.name == 'Desktop')\
            .filter(Device.category == 'production')\
            .filter(Device.obsolete == False)\
            .order_by(Device.alias.asc())
    if show_mobile_devices:
        header = '移动设备'
        query = Device.query\
            .join(DeviceType, DeviceType.id == Device.type_id)\
            .filter(DeviceType.name == 'Mobile')\
            .filter(Device.category == 'production')\
            .filter(Device.obsolete == False)\
            .order_by(Device.alias.asc())
    if show_development_devices:
        if current_user.is_developer:
            header = '开发设备'
            query = Device.query\
                .filter(Device.category == 'development')\
                .filter(Device.obsolete == False)\
                .order_by(Device.alias.asc())
        else:
            return redirect(url_for('manage.tablet_devices'))
    if show_obsolete_devices:
        header = '报废设备'
        if current_user.is_developer:
            query = Device.query\
                .filter(Device.obsolete == True)\
                .order_by(Device.alias.asc())
        else:
            query = Device.query\
                .filter(Device.category == 'production')\
                .filter(Device.obsolete == True)\
                .order_by(Device.alias.asc())
    page = request.args.get('page', 1, type=int)
    try:
        pagination = query.paginate(page, per_page=current_app.config['RECORD_PER_PAGE'], error_out=False)
    except NameError:
        return redirect(url_for('manage.tablet_devices'))
    devices = pagination.items
    return minify(render_template(
        'manage/device.html',
        header=header,
        show_tablet_devices=show_tablet_devices,
        show_desktop_devices=show_desktop_devices,
        show_mobile_devices=show_mobile_devices,
        show_development_devices=show_development_devices,
        show_obsolete_devices=show_obsolete_devices,
        pagination=pagination,
        devices=devices
    ))


@manage.route('/device/tablet')
@login_required
@permission_required('管理设备')
def tablet_devices():
    '''manage.tablet_devices()'''
    resp = make_response(redirect(url_for('manage.device')))
    resp.set_cookie('show_tablet_devices', '1', max_age=current_app.config['COOKIE_MAX_AGE'])
    resp.set_cookie('show_desktop_devices', '', max_age=current_app.config['COOKIE_MAX_AGE'])
    resp.set_cookie('show_mobile_devices', '', max_age=current_app.config['COOKIE_MAX_AGE'])
    resp.set_cookie('show_development_devices', '', max_age=current_app.config['COOKIE_MAX_AGE'])
    resp.set_cookie('show_obsolete_devices', '', max_age=current_app.config['COOKIE_MAX_AGE'])
    return resp


@manage.route('/device/desktop')
@login_required
@permission_required('管理设备')
def desktop_devices():
    '''manage.desktop_devices()'''
    resp = make_response(redirect(url_for('manage.device')))
    resp.set_cookie('show_tablet_devices', '', max_age=current_app.config['COOKIE_MAX_AGE'])
    resp.set_cookie('show_desktop_devices', '1', max_age=current_app.config['COOKIE_MAX_AGE'])
    resp.set_cookie('show_mobile_devices', '', max_age=current_app.config['COOKIE_MAX_AGE'])
    resp.set_cookie('show_development_devices', '', max_age=current_app.config['COOKIE_MAX_AGE'])
    resp.set_cookie('show_obsolete_devices', '', max_age=current_app.config['COOKIE_MAX_AGE'])
    return resp


@manage.route('/device/mobile')
@login_required
@permission_required('管理设备')
def mobile_devices():
    '''manage.mobile_devices()'''
    resp = make_response(redirect(url_for('manage.device')))
    resp.set_cookie('show_tablet_devices', '', max_age=current_app.config['COOKIE_MAX_AGE'])
    resp.set_cookie('show_desktop_devices', '', max_age=current_app.config['COOKIE_MAX_AGE'])
    resp.set_cookie('show_mobile_devices', '1', max_age=current_app.config['COOKIE_MAX_AGE'])
    resp.set_cookie('show_development_devices', '', max_age=current_app.config['COOKIE_MAX_AGE'])
    resp.set_cookie('show_obsolete_devices', '', max_age=current_app.config['COOKIE_MAX_AGE'])
    return resp


@manage.route('/device/development')
@login_required
@role_required('开发人员')
def development_devices():
    '''manage.development_devices()'''
    resp = make_response(redirect(url_for('manage.device')))
    resp.set_cookie('show_tablet_devices', '', max_age=current_app.config['COOKIE_MAX_AGE'])
    resp.set_cookie('show_desktop_devices', '', max_age=current_app.config['COOKIE_MAX_AGE'])
    resp.set_cookie('show_mobile_devices', '', max_age=current_app.config['COOKIE_MAX_AGE'])
    resp.set_cookie('show_development_devices', '1', max_age=current_app.config['COOKIE_MAX_AGE'])
    resp.set_cookie('show_obsolete_devices', '', max_age=current_app.config['COOKIE_MAX_AGE'])
    return resp


@manage.route('/device/obsolete')
@login_required
@permission_required('管理设备')
def obsolete_devices():
    '''manage.obsolete_devices()'''
    resp = make_response(redirect(url_for('manage.device')))
    resp.set_cookie('show_tablet_devices', '', max_age=current_app.config['COOKIE_MAX_AGE'])
    resp.set_cookie('show_desktop_devices', '', max_age=current_app.config['COOKIE_MAX_AGE'])
    resp.set_cookie('show_mobile_devices', '', max_age=current_app.config['COOKIE_MAX_AGE'])
    resp.set_cookie('show_development_devices', '', max_age=current_app.config['COOKIE_MAX_AGE'])
    resp.set_cookie('show_obsolete_devices', '1', max_age=current_app.config['COOKIE_MAX_AGE'])
    return resp
