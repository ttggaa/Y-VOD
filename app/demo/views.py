# -*- coding: utf-8 -*-

'''app/demo/views.py'''

from htmlmin import minify
from flask import render_template, redirect, request, url_for, flash
from . import demo
from ..models import Device
from ..models import LessonType, Lesson, Video
from ..utils import get_mac_address_from_ip


@demo.route('/')
def lesson():
    '''demo.lesson()'''
    mac_address = get_mac_address_from_ip(ip_address=request.headers.get('X-Forwarded-For', request.remote_addr))
    if mac_address is None:
        flash('无法获取设备信息', category='error')
        return redirect(url_for('auth.login'))
    device = Device.query.filter_by(mac_address=mac_address).first()
    if device is None:
        flash('设备未授权（MAC地址：{}）'.format(mac_address), category='error')
        return redirect(url_for('auth.login'))
    lesson_type = '体验课程'
    if not device.can_access_lesson_type(lesson_type=lesson_type):
        flash('该设备无法访问“{}”资源'.format(lesson_type), category='error')
        return redirect(url_for('auth.login'))
    lessons = Lesson.query\
        .join(LessonType, LessonType.id == Lesson.type_id)\
        .filter(LessonType.name == lesson_type)\
        .order_by(Lesson.id.asc())
    return minify(render_template(
        'demo/lesson.html',
        header=lesson_type,
        lessons=lessons
    ))


@demo.route('/video/<int:id>')
def video(id):
    '''demo.video(id)'''
    mac_address = get_mac_address_from_ip(ip_address=request.headers.get('X-Forwarded-For', request.remote_addr))
    if mac_address is None:
        flash('无法获取设备信息', category='error')
        return redirect(url_for('auth.login'))
    device = Device.query.filter_by(mac_address=mac_address).first()
    if device is None:
        flash('设备未授权（MAC地址：{}）'.format(mac_address), category='error')
        return redirect(url_for('auth.login'))
    video = Video.query.get_or_404(id)
    if not device.can_access_lesson_type(lesson_type=video.lesson.type):
        flash('该设备无法访问“{}”资源'.format(video.lesson.type.name), category='error')
        return redirect(url_for('auth.login'))
    return minify(render_template(
        'demo/video.html',
        video=video
    ))
