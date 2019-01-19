# -*- coding: utf-8 -*-

'''app/views/auth.py'''

from htmlmin import minify
from flask import Blueprint
from flask import render_template, redirect, request, url_for, flash
from flask import current_app
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models import Role, User
from app.models import Device
from app.models import LessonType, Lesson, Video
from app.utils import get_mac_address_from_ip, y_system_api_request, verify_data_keys
from app.utils2 import get_device_info, add_user_log
from app.forms.auth import LoginForm


auth = Blueprint('auth', __name__)


@auth.before_app_request
def before_request():
    '''auth.before_request()'''
    if current_user.is_authenticated:
        current_user.ping()
        mac_address = get_mac_address_from_ip(ip_address=request.headers\
            .get('X-Forwarded-For', request.remote_addr))
        if mac_address is not None and mac_address != current_user.last_seen_mac:
            current_user.update_mac(mac_address=mac_address)
            add_user_log(
                user=current_user._get_current_object(),
                event='请求访问（来源：{}）'.format(get_device_info(
                    mac_address=mac_address,
                    show_mac=True
                )),
                category='access'
            )
        db.session.commit()


@auth.route('/login', methods=['GET', 'POST'])
def login():
    '''auth.login()'''
    if current_user.is_authenticated:
        return redirect(request.args.get('next') or current_user.index_url)
    form = LoginForm()
    if form.validate_on_submit():
        mac_address = get_mac_address_from_ip(ip_address=request.headers\
            .get('X-Forwarded-For', request.remote_addr))
        if mac_address is None:
            flash('无法获取设备信息', category='error')
            return redirect(url_for('auth.login', next=request.args.get('next')))
        device = Device.query.filter_by(mac_address=mac_address).first()
        if device is None:
            flash('设备未授权（MAC地址：{}）'.format(mac_address), category='error')
            return redirect(url_for('auth.login', next=request.args.get('next')))
        # authenticate user via Y-System
        data = y_system_api_request(api='login-user', token_data={
            'email': form.email.data.strip().lower(),
            'password': form.password.data,
            'device': device.alias,
        })
        print(data)
        if data is None:
            flash('网络通信故障', category='error')
            return redirect(url_for('auth.login', next=request.args.get('next')))
        if verify_data_keys(data=data, keys=['error']):
            flash('登录失败：{}'.format(data.get('error')), category='error')
            return redirect(url_for('auth.login', next=request.args.get('next')))
        if not verify_data_keys(data=data, keys=['user_id']):
            flash('登录失败：用户信息无效', category='error')
            flash('初次登录时，请确认Y-System账号已经激活。', category='info')
            return redirect(url_for('auth.login', next=request.args.get('next')))
        user = User.query.get(data.get('user_id'))
        if user is None:
            # migrate user from Y-System
            data = y_system_api_request(api='migrate-user', token_data={
                'user_id': data.get('user_id'),
            })
            if data is None:
                flash('网络通信故障', category='error')
                return redirect(url_for('auth.login', next=request.args.get('next')))
            if verify_data_keys(data=data, keys=['error']):
                flash('登录失败：{}'.format(data.get('error')), category='error')
                return redirect(url_for('auth.login', next=request.args.get('next')))
            if not verify_data_keys(data=data, keys=['user_id', 'role', 'name']):
                flash('登录失败：用户信息无效', category='error')
                flash('初次登录时，请确认Y-System账号已经激活。', category='info')
                return redirect(url_for('auth.login', next=request.args.get('next')))
            role = Role.query.filter_by(name=data.get('role')).first()
            if role is None:
                flash('登录失败：无效的用户角色“{}”'.format(data.get('role')), category='error')
                return redirect(url_for('auth.login', next=request.args.get('next')))
            user = User(
                id=data.get('user_id'),
                role_id=role.id,
                name=data.get('name')
            )
            db.session.add(user)
            db.session.commit()
            if data.get('vb_progress') is not None:
                vb_video = Video.query.filter_by(name=data.get('vb_progress')).first()
                if vb_video is not None:
                    for video in Video.query\
                        .join(Lesson, Lesson.id == Video.lesson_id)\
                        .join(LessonType, LessonType.id == Lesson.type_id)\
                        .filter(LessonType.name == 'VB')\
                        .filter(Video.id <= vb_video.id)\
                        .order_by(Video.id.asc())\
                        .all():
                        user.punch(video=video, play_time=video.duration)
            if data.get('y_gre_progress') is not None:
                y_gre_lesson = Lesson.query.filter_by(name=data.get('y_gre_progress')).first()
                if y_gre_lesson is not None:
                    for video in Video.query\
                        .join(Lesson, Lesson.id == Video.lesson_id)\
                        .join(LessonType, LessonType.id == Lesson.type_id)\
                        .filter(LessonType.name == 'Y-GRE')\
                        .filter(Lesson.id <= y_gre_lesson.id)\
                        .order_by(Video.id.asc())\
                        .all():
                        user.punch(video=video, play_time=video.duration)
            add_user_log(user=user, event='从Y-System导入用户信息', category='auth')
        login_user(user, remember=current_app.config['AUTH_REMEMBER_LOGIN'])
        add_user_log(user=user, event='登录系统', category='auth')
        db.session.commit()
        return redirect(request.args.get('next') or user.index_url)
    return minify(render_template(
        'auth/login.html',
        form=form
    ))


@auth.route('/logout')
@login_required
def logout():
    '''auth.logout()'''
    add_user_log(user=current_user._get_current_object(), event='登出系统', category='auth')
    db.session.commit()
    logout_user()
    return redirect(url_for('auth.login'))
