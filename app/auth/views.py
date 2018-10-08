# -*- coding: utf-8 -*-

'''app/auth/views.py'''

from htmlmin import minify
from flask import render_template, redirect, request, url_for, flash, current_app
from flask_login import login_user, logout_user, login_required, current_user
from . import auth
from .forms import LoginForm
from .. import db
from ..models import User
from ..utils2 import get_device_info, add_user_log


@auth.before_app_request
def before_request():
    if current_user.is_authenticated:
        current_user.ping()
        ip_address = request.headers.get('X-Forwarded-For', request.remote_addr)
        if ip_address != current_user.last_seen_ip:
            current_user.update_ip(ip_address=ip_address)
            add_user_log(user=current_user._get_current_object(), event='请求访问（来源：{}）'.format(get_device_info(ip_address=ip_address, show_ip=True)), category='access')
        db.session.commit()


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(request.args.get('next') or current_user.index_url)
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.strip().lower(), created=True, deleted=False).first()
        if user is not None:
            if not user.locked:
                if user.verify_password(form.password.data):
                    user.reset_invalid_login_count()
                    login_user(user, remember=form.remember_me.data)
                    if not current_app.debug and user.plays('协管员'):
                        send_email(user.email, '登录提醒', 'auth/mail/login', user=user, timestamp=datetime_now(utc_offset=current_app.config['UTC_OFFSET']))
                    get_announcements(type_name='登录通知', flash_first=True)
                    add_feed(user=user, event='登录系统', category='access')
                    db.session.commit()
                    return redirect(request.args.get('next') or user.index_url)
                else:
                    user.increase_invalid_login_count()
                    db.session.commit()
                    if user.locked:
                        send_emails(
                            recipients=[staff.email for staff in User.users_can('管理用户').all() if staff.has_inner_domain_email],
                            subject='锁定用户：{}'.format(user.name_alias),
                            template='auth/mail/locked_user',
                            user=user
                        )
                    flash('登录失败：密码错误（第{}次）'.format(user.invalid_login_count), category='error')
                    add_feed(user=user, event='登录失败：密码错误（第{}次，来源：{}）'.format(user.invalid_login_count, get_device_info(ip_address=request.headers.get('X-Forwarded-For', request.remote_addr), show_ip=True)), category='access')
                    db.session.commit()
                    return redirect(url_for('auth.login'))
            else:
                flash('登录失败：您的账户已被锁定', category='error')
                return redirect(url_for('auth.login'))
        flash('登录失败：无效的用户名或密码', category='error')
    return minify(render_template('auth/login.html', form=form))


@auth.route('/logout')
@login_required
def logout():
    add_feed(user=current_user._get_current_object(), event='登出系统', category='access')
    db.session.commit()
    logout_user()
    return redirect(url_for('auth.login'))
