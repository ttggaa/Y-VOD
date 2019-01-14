# -*- coding: utf-8 -*-

'''app/manage/views.py'''

from htmlmin import minify
from flask import render_template, redirect, request, make_response, url_for, abort, flash, current_app
from flask_login import login_required, current_user
from app import db
from app.models import Role, User
from app.models import DeviceType, Device
from app.models import LessonType, Lesson, Video
from app.decorators import permission_required, role_required
from app.utils2 import add_user_log
from . import manage
from .forms import NewDeviceForm, EditDeviceForm


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


# @manage.route('/user/import', methods=['GET', 'POST'])
# @login_required
# @permission_required('管理用户')
# def import_user():
#     '''manage.import_user()'''
#     form = ImportUserForm()
#     if form.validate_on_submit():
#         data = User.import_user(token=form.token.data)
#         if data is None or reduce(operator.or_, [data.get(key) is None for key in ['id', 'role', 'name', 'id_type', 'id_number']]):
#             flash('用户信息码有误', category='error')
#             return redirect(url_for('manage.import_user', next=request.args.get('next')))
#         if User.query.get(data.get('id')) is not None:
#             flash('该用户已存在', category='error')
#             return redirect(url_for('manage.import_user', next=request.args.get('next')))
#         role = Role.query.filter_by(name=data.get('role')).first()
#         if role is None:
#             flash('用户角色信息有误：{}'.format(data.get('role')), category='error')
#             return redirect(url_for('manage.import_user', next=request.args.get('next')))
#         if not current_user.role.can_manage(role=role):
#             flash('您无法创建该用户', category='error')
#             return redirect(url_for('manage.import_user', next=request.args.get('next')))
#         id_type = IDType.query.filter_by(name=data.get('id_type')).first()
#         if id_type is None:
#             flash('证件类型信息有误：{}'.format(data.get('id_type')), category='error')
#             return redirect(url_for('manage.import_user', next=request.args.get('next')))
#         user = User(
#             id=data.get('id'),
#             role_id=role.id,
#             name=data.get('name'),
#             id_type_id=id_type.id,
#             id_number=data.get('id_number')
#         )
#         if data.get('gender') is not None:
#             gender = Gender.query.filter_by(name=data.get('gender')).first()
#             if gender is None:
#                 flash('性别信息有误：{}'.format(data.get('gender')), category='error')
#                 return redirect(url_for('manage.import_user', next=request.args.get('next')))
#             user.gender_id = gender.id
#         db.session.add(user)
#         db.session.commit()
#         current_user.create_user(user=user)
#         if user.is_student:
#             if data.get('vb_progress') is not None:
#                 vb_lesson = Lesson.query.filter_by(name=data.get('vb_progress')).first()
#                 if vb_lesson is not None:
#                     user.punch_through(lesson=vb_lesson)
#             if data.get('y_gre_progress') is not None:
#                 y_gre_lesson = Lesson.query.filter_by(name=data.get('y_gre_progress')).first()
#                 if y_gre_lesson is not None:
#                     user.punch_through(lesson=y_gre_lesson)
#         flash('已导入用户：{}'.format(user.name_with_role), category='success')
#         add_user_log(user=user, event='用户信息被导入', category='auth')
#         add_user_log(user=current_user._get_current_object(), event='导入用户：{}'.format(user.name_with_role), category='manage')
#         db.session.commit()
#         return redirect(request.args.get('next') or url_for('manage.{}'.format(role.category)))
#     return minify(render_template(
#         'manage/user/import.html',
#         form=form
#     ))


@manage.route('/user/suspend/<int:id>')
@login_required
@permission_required('管理用户')
def suspend_user(id):
    '''manage.suspend_user(id)'''
    user = User.query.get_or_404(id)
    if not current_user.can_manage(user=user):
        abort(403)
    if user.suspended:
        flash('“{}”已处于挂起状态'.format(user.name_with_role), category='warning')
        return redirect(request.args.get('next') or url_for('profile.overview', id=user.id))
    user.suspend()
    flash('已挂起用户：{}'.format(user.name_with_role), category='success')
    add_user_log(user=user, event='用户被挂起', category='auth')
    add_user_log(user=current_user._get_current_object(), event='挂起用户：{}'.format(user.name_with_role), category='manage')
    db.session.commit()
    return redirect(request.args.get('next') or url_for('profile.overview', id=user.id))


@manage.route('/user/restore/<int:id>')
@login_required
@permission_required('管理用户')
def restore_user(id):
    '''manage.restore_user(id)'''
    user = User.query.get_or_404(id)
    if not current_user.can_manage(user=user):
        abort(403)
    if not user.suspended:
        flash('“{}”未处于挂起状态'.format(user.name_with_role), category='warning')
        return redirect(request.args.get('next') or url_for('profile.overview', id=user.id))
    user.restore()
    flash('已恢复用户：{}'.format(user.name_with_role), category='success')
    add_user_log(user=user, event='用户被恢复', category='auth')
    add_user_log(user=current_user._get_current_object(), event='恢复用户：{}'.format(user.name_with_role), category='manage')
    db.session.commit()
    return redirect(request.args.get('next') or url_for('profile.overview', id=user.id))


@manage.route('/device', methods=['GET', 'POST'])
@login_required
@permission_required('管理设备')
def device():
    '''manage.device()'''
    form = NewDeviceForm(current_user=current_user._get_current_object())
    if form.validate_on_submit():
        serial = form.serial.data.upper()
        if Device.query.filter_by(serial=serial).first() is not None:
            flash('已存在序列号为“{}”的设备'.format(serial), category='error')
            return redirect(url_for('manage.device'))
        device = Device(
            serial=serial,
            alias=form.alias.data,
            type_id=int(form.device_type.data),
            room_id=(None if int(form.room.data) == 0 else int(form.room.data)),
            mac_address=(None if form.mac_address.data == '' else form.mac_address.data),
            category=('development' if form.development_machine.data and current_user.is_developer else 'production'),
            modified_by_id=current_user.id
        )
        db.session.add(device)
        db.session.commit()
        for lesson_type_id in form.lesson_types.data:
            device.add_lesson_type(lesson_type=LessonType.query.get(int(lesson_type_id)))
        db.session.commit()
        flash('已添加设备：{} [{}]'.format(device.alias, device.serial), category='success')
        add_user_log(user=current_user._get_current_object(), event='添加设备：{} [{}]'.format(device.alias, device.serial), category='manage')
        db.session.commit()
        return redirect(url_for('manage.device'))
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
        form=form,
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


@manage.route('/device/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@permission_required('管理设备')
def edit_device(id):
    '''manage.edit_device(id)'''
    device = Device.query.get_or_404(id)
    if device.category == 'development' and not current_user.is_developer:
        abort(403)
    form = EditDeviceForm(current_user=current_user._get_current_object())
    if form.validate_on_submit():
        serial = form.serial.data.upper()
        if Device.query\
            .filter(Device.id != device.id)\
            .filter(Device.serial == serial)\
            .first() is not None:
            flash('已存在序列号为“{}”的设备'.format(serial), category='error')
            return redirect(request.args.get('next') or url_for('manage.device'))
        device.serial = serial
        device.alias = form.alias.data
        device.type_id = int(form.device_type.data)
        device.room_id = (None if int(form.room.data) == 0 else int(form.room.data))
        device.mac_address = (None if form.mac_address.data == '' else form.mac_address.data)
        device.category = ('development' if form.development_machine.data and current_user.is_developer else 'production')
        db.session.add(device)
        device.remove_all_lesson_types()
        for lesson_type_id in form.lesson_types.data:
            device.add_lesson_type(lesson_type=LessonType.query.get(int(lesson_type_id)))
        db.session.commit()
        flash('已更新设备信息：{}'.format(device.alias_serial), category='success')
        add_user_log(user=current_user._get_current_object(), event='更新设备信息：{}'.format(device.alias_serial), category='manage')
        db.session.commit()
        return redirect(request.args.get('next') or url_for('manage.device'))
    form.alias.data = device.alias
    form.serial.data = device.serial
    form.device_type.data = str(device.type_id)
    form.room.data = ('0' if device.room_id == None else str(device.room_id))
    form.mac_address.data = device.mac_address
    form.lesson_types.data = [str(item.lesson_type_id) for item in device.lesson_type_authorizations]
    form.development_machine.data = (device.category == 'development')
    return minify(render_template(
        'manage/edit_device.html',
        device=device,
        form=form
    ))


@manage.route('/device/toggle-obsolete/<int:id>')
@login_required
@permission_required('管理设备')
def toggle_device_obsolete(id):
    '''manage.toggle_device_obsolete(id)'''
    device = Device.query.get_or_404(id)
    if device.category == 'development' and not current_user.is_developer:
        abort(403)
    device.toggle_obsolete(modified_by=current_user._get_current_object())
    if device.obsolete:
        flash('已标记报废设备：{}'.format(device.alias_serial), category='success')
        add_user_log(user=current_user._get_current_object(), event='标记报废设备：{}'.format(device.alias_serial), category='manage')
    else:
        flash('已恢复使用设备：{}'.format(device.alias_serial), category='success')
        add_user_log(user=current_user._get_current_object(), event='恢复使用设备：{}'.format(device.alias_serial), category='manage')
    db.session.commit()
    return redirect(request.args.get('next') or url_for('manage.device'))


@manage.route('/device/delete/<int:id>')
@login_required
@permission_required('管理设备')
def delete_device(id):
    '''manage.delete_device(id)'''
    device = Device.query.get_or_404(id)
    if device.category == 'development' and not current_user.is_developer:
        abort(403)
    device.remove_all_lesson_types()
    db.session.delete(device)
    flash('已删除设备：{}'.format(device.alias_serial), category='success')
    add_user_log(user=current_user._get_current_object(), event='删除设备：{}'.format(device.alias_serial), category='manage')
    db.session.commit()
    return redirect(request.args.get('next') or url_for('manage.device'))


@manage.route('/lesson')
@login_required
@permission_required('管理')
def lesson():
    '''manage.lesson()'''
    show_vb_lessons = True
    show_y_gre_lessons = False
    show_y_gre_aw_lessons = False
    show_test_review_lessons = False
    show_demo_lessons = False
    if current_user.is_authenticated:
        show_vb_lessons = bool(request.cookies.get('show_vb_lessons', '1'))
        show_y_gre_lessons = bool(request.cookies.get('show_y_gre_lessons', ''))
        show_y_gre_aw_lessons = bool(request.cookies.get('show_y_gre_aw_lessons', ''))
        show_test_review_lessons = bool(request.cookies.get('show_test_review_lessons', ''))
        show_demo_lessons = bool(request.cookies.get('show_demo_lessons', ''))
    if show_vb_lessons:
        lesson_type = 'VB'
    if show_y_gre_lessons:
        lesson_type = 'Y-GRE'
    if show_y_gre_aw_lessons:
        lesson_type = 'Y-GRE AW'
    if show_test_review_lessons:
        lesson_type = '考试讲解'
    if show_demo_lessons:
        lesson_type = '体验课程'
    page = request.args.get('page', 1, type=int)
    try:
        query = Lesson.query\
            .join(LessonType, LessonType.id == Lesson.type_id)\
            .filter(LessonType.name == lesson_type)\
            .order_by(Lesson.id.asc())
        pagination = query.paginate(page, per_page=current_app.config['RECORD_PER_PAGE'], error_out=False)
    except NameError:
        return redirect(url_for('manage.vb_lessons'))
    lessons = pagination.items
    return minify(render_template(
        'manage/lesson.html',
        header=lesson_type,
        show_vb_lessons=show_vb_lessons,
        show_y_gre_lessons=show_y_gre_lessons,
        show_y_gre_aw_lessons=show_y_gre_aw_lessons,
        show_test_review_lessons=show_test_review_lessons,
        show_demo_lessons=show_demo_lessons,
        pagination=pagination,
        lessons=lessons
    ))


@manage.route('/lesson/vb')
@login_required
@permission_required('管理')
def vb_lessons():
    '''manage.vb_lessons()'''
    resp = make_response(redirect(url_for('manage.lesson')))
    resp.set_cookie('show_vb_lessons', '1', max_age=current_app.config['COOKIE_MAX_AGE'])
    resp.set_cookie('show_y_gre_lessons', '', max_age=current_app.config['COOKIE_MAX_AGE'])
    resp.set_cookie('show_y_gre_aw_lessons', '', max_age=current_app.config['COOKIE_MAX_AGE'])
    resp.set_cookie('show_test_review_lessons', '', max_age=current_app.config['COOKIE_MAX_AGE'])
    resp.set_cookie('show_demo_lessons', '', max_age=current_app.config['COOKIE_MAX_AGE'])
    return resp


@manage.route('/lesson/y-gre')
@login_required
@permission_required('管理')
def y_gre_lessons():
    '''manage.y_gre_lessons()'''
    resp = make_response(redirect(url_for('manage.lesson')))
    resp.set_cookie('show_vb_lessons', '', max_age=current_app.config['COOKIE_MAX_AGE'])
    resp.set_cookie('show_y_gre_lessons', '1', max_age=current_app.config['COOKIE_MAX_AGE'])
    resp.set_cookie('show_y_gre_aw_lessons', '', max_age=current_app.config['COOKIE_MAX_AGE'])
    resp.set_cookie('show_test_review_lessons', '', max_age=current_app.config['COOKIE_MAX_AGE'])
    resp.set_cookie('show_demo_lessons', '', max_age=current_app.config['COOKIE_MAX_AGE'])
    return resp


@manage.route('/lesson/y-gre-aw')
@login_required
@permission_required('管理')
def y_gre_aw_lessons():
    '''manage.y_gre_aw_lessons()'''
    resp = make_response(redirect(url_for('manage.lesson')))
    resp.set_cookie('show_vb_lessons', '', max_age=current_app.config['COOKIE_MAX_AGE'])
    resp.set_cookie('show_y_gre_lessons', '', max_age=current_app.config['COOKIE_MAX_AGE'])
    resp.set_cookie('show_y_gre_aw_lessons', '1', max_age=current_app.config['COOKIE_MAX_AGE'])
    resp.set_cookie('show_test_review_lessons', '', max_age=current_app.config['COOKIE_MAX_AGE'])
    resp.set_cookie('show_demo_lessons', '', max_age=current_app.config['COOKIE_MAX_AGE'])
    return resp


@manage.route('/lesson/test-review')
@login_required
@permission_required('管理')
def test_review_lessons():
    '''manage.test_review_lessons()'''
    resp = make_response(redirect(url_for('manage.lesson')))
    resp.set_cookie('show_vb_lessons', '', max_age=current_app.config['COOKIE_MAX_AGE'])
    resp.set_cookie('show_y_gre_lessons', '', max_age=current_app.config['COOKIE_MAX_AGE'])
    resp.set_cookie('show_y_gre_aw_lessons', '', max_age=current_app.config['COOKIE_MAX_AGE'])
    resp.set_cookie('show_test_review_lessons', '1', max_age=current_app.config['COOKIE_MAX_AGE'])
    resp.set_cookie('show_demo_lessons', '', max_age=current_app.config['COOKIE_MAX_AGE'])
    return resp


@manage.route('/lesson/demo')
@login_required
@permission_required('管理')
def demo_lessons():
    '''manage.demo_lessons()'''
    resp = make_response(redirect(url_for('manage.lesson')))
    resp.set_cookie('show_vb_lessons', '', max_age=current_app.config['COOKIE_MAX_AGE'])
    resp.set_cookie('show_y_gre_lessons', '', max_age=current_app.config['COOKIE_MAX_AGE'])
    resp.set_cookie('show_y_gre_aw_lessons', '', max_age=current_app.config['COOKIE_MAX_AGE'])
    resp.set_cookie('show_test_review_lessons', '', max_age=current_app.config['COOKIE_MAX_AGE'])
    resp.set_cookie('show_demo_lessons', '1', max_age=current_app.config['COOKIE_MAX_AGE'])
    return resp


@manage.route('/lesson/<int:lesson_id>/video')
@login_required
@permission_required('管理')
def video(lesson_id):
    '''manage.video(lesson_id)'''
    lesson = Lesson.query.get_or_404(lesson_id)
    query = Video.query\
        .filter(Video.lesson_id == lesson.id)\
        .order_by(Video.id.asc())
    page = request.args.get('page', 1, type=int)
    pagination = query.paginate(page, per_page=current_app.config['RECORD_PER_PAGE'], error_out=False)
    videos = pagination.items
    return minify(render_template(
        'manage/video.html',
        lesson=lesson,
        pagination=pagination,
        videos=videos
    ))
