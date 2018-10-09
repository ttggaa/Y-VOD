# -*- coding: utf-8 -*-

'''app/auth/views.py'''

from htmlmin import minify
from flask import render_template, redirect, request, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from . import auth
from .forms import LoginForm
from .. import db
from ..models import User
from ..models import Device
from ..utils2 import get_device_info, add_user_log


@auth.before_app_request
def before_request():
    '''auth.before_request()'''
    if current_user.is_authenticated:
        current_user.ping()
        ip_address = request.headers.get('X-Forwarded-For', request.remote_addr)
        if ip_address != current_user.last_seen_ip:
            current_user.update_ip(ip_address=ip_address)
            add_user_log(user=current_user._get_current_object(), event='请求访问（来源：{}）'.format(get_device_info(ip_address=ip_address, show_ip=True)), category='access')
        db.session.commit()


@auth.route('/login', methods=['GET', 'POST'])
def login():
    '''auth.login()'''
    if current_user.is_authenticated:
        return redirect(request.args.get('next') or current_user.index_url)
    form = LoginForm()
    if form.validate_on_submit():
        ip_address = request.headers.get('X-Forwarded-For', request.remote_addr)
        device = Device.query.filter_by(ip_address=ip_address).first()
        if device is None:
            flash('设备未授权', category='error')
            return redirect(url_for('auth.login', next=request.args.get('next')))
        user = User.query.filter_by(name=form.name.data, id_number=form.id_number.data, deleted=False).first()
        if user is not None:
            login_user(user, remember=False)
            add_user_log(user=user, event='登录系统', category='access')
            db.session.commit()
            return redirect(request.args.get('next') or user.index_url)
        else:
            flash('登录失败：无效的用户信息', category='error')
            return redirect(url_for('auth.login', next=request.args.get('next')))
    return minify(render_template('auth/login.html', form=form))


@auth.route('/logout')
@login_required
def logout():
    '''auth.logout()'''
    add_user_log(user=current_user._get_current_object(), event='登出系统', category='access')
    db.session.commit()
    logout_user()
    return redirect(url_for('auth.login'))
