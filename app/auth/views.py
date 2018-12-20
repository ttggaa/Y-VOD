# -*- coding: utf-8 -*-

'''app/auth/views.py'''

from htmlmin import minify
from flask import render_template, redirect, request, url_for, flash, current_app
from flask_login import login_user, logout_user, login_required, current_user
from . import auth
from .forms import LoginForm
from .. import db
from ..models import User
from ..models import Device
from ..utils import get_mac_address_from_ip
from ..utils2 import get_device_info, add_user_log


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
                    login_user(user, remember=False)
                    add_user_log(user=user, event='登录系统', category='auth')
                    db.session.commit()
                    return redirect(request.args.get('next') or user.index_url)
            flash('登录失败：授权码错误', category='error')
            return redirect(url_for('auth.login', next=request.args.get('next')))
        else:
            flash('登录失败：用户信息无效', category='error')
            flash('初次登录时，请联系工作人员确认用户信息已被导入。', category='info')
            return redirect(url_for('auth.login', next=request.args.get('next')))
    return minify(render_template('auth/login.html', form=form))


@auth.route('/logout')
@login_required
def logout():
    '''auth.logout()'''
    add_user_log(user=current_user._get_current_object(), event='登出系统', category='auth')
    db.session.commit()
    logout_user()
    return redirect(url_for('auth.login'))
