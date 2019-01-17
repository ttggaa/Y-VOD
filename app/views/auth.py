# -*- coding: utf-8 -*-

'''app/views/auth.py'''

import operator
from functools import reduce
import requests
from requests.exceptions import RequestException
from itsdangerous import TimedJSONWebSignatureSerializer
from htmlmin import minify
from flask import Blueprint, render_template, redirect, request, url_for, flash, current_app
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models import Role, User
from app.models import IDType, Gender
from app.models import Device
from app.models import LessonType, Lesson, Video
from app.utils import get_mac_address_from_ip
from app.utils2 import get_device_info, add_user_log
from app.forms.auth import LoginForm


auth = Blueprint('auth', __name__)


@auth.before_app_request
def before_request():
    '''auth.before_request()'''
    if current_user.is_authenticated:
        current_user.ping()
        mac_address = get_mac_address_from_ip(ip_address=request.headers.get('X-Forwarded-For', request.remote_addr))
        if mac_address is not None and mac_address != current_user.last_seen_mac:
            current_user.update_mac(mac_address=mac_address)
            add_user_log(user=current_user._get_current_object(), event='请求访问（来源：{}）'.format(get_device_info(mac_address=mac_address, show_mac=True)), category='access')
        db.session.commit()


@auth.route('/login', methods=['GET', 'POST'])
def login():
    '''auth.login()'''
    if current_user.is_authenticated:
        return redirect(request.args.get('next') or current_user.index_url)
    form = LoginForm(auth_token_length=current_app.config['AUTH_TOKEN_LENGTH'])
    if form.validate_on_submit():
        mac_address = get_mac_address_from_ip(ip_address=request.headers.get('X-Forwarded-For', request.remote_addr))
        if mac_address is None:
            flash('无法获取设备信息', category='error')
            return redirect(url_for('auth.login', next=request.args.get('next')))
        device = Device.query.filter_by(mac_address=mac_address).first()
        if device is None:
            flash('设备未授权（MAC地址：{}）'.format(mac_address), category='error')
            return redirect(url_for('auth.login', next=request.args.get('next')))
        users = User.query\
            .filter(User.name == form.name.data)\
            .filter(User.id_number.endswith(form.id_number.data.upper()))
        if users.count():
            for user in users.all():
                if user.verify_auth_token(token=form.auth_token.data):
                    login_user(user, remember=current_app.config['AUTH_REMEMBER_LOGIN'])
                    add_user_log(user=user, event='登录系统', category='auth')
                    db.session.commit()
                    return redirect(request.args.get('next') or user.index_url)
        # migrate user from Y-System
        serial = TimedJSONWebSignatureSerializer(
            secret_key=current_app.config['AUTH_TOKEN_SECRET_KEY'],
            expires_in=current_app.config['TOKEN_EXPIRATION']
        )
        try:
            migration_request = requests.get(
                '{}/api/user/migrate/{}'.format(current_app.config['YSYS_URI'], serial.dumps({
                    'name': form.name.data,
                    'id_number': form.id_number.data.upper(),
                    'auth_token': form.auth_token.data.lower(),
                }).decode('ascii')),
                timeout=current_app.config['REQUEST_TIMEOUT']
            )
            data = migration_request.json()
        except RequestException:
            flash('网络通信故障', category='error')
            return redirect(url_for('auth.login', next=request.args.get('next')))
        if data is None or reduce(operator.or_, [data.get(key) is None for key in ['id', 'role', 'name', 'id_type', 'id_number']]):
            flash('登录失败：用户信息无效', category='error')
            flash('初次登录时，请确认Y-System账号已经激活。', category='info')
            return redirect(url_for('auth.login', next=request.args.get('next')))
        role = Role.query.filter_by(name=data.get('role')).first()
        if role is None:
            flash('登录失败：无效的用户角色“{}”'.format(data.get('role')), category='error')
            return redirect(url_for('auth.login', next=request.args.get('next')))
        user = User(
            id=data.get('id'),
            role_id=role.id,
            name=data.get('name'),
            id_type_id=IDType.query.filter_by(name=data.get('id_type')).first().id,
            id_number=data.get('id_number')
        )
        if data.get('gender') is not None:
            user.gender_id = Gender.query.filter_by(name=data.get('gender')).first().id
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
        login_user(user, remember=current_app.config['AUTH_REMEMBER_LOGIN'])
        add_user_log(user=user, event='导入用户信息', category='auth')
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
