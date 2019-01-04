# -*- coding: utf-8 -*-

'''app/study/views.py'''

from htmlmin import minify
from flask import render_template, jsonify, redirect, request, url_for, abort, flash, current_app
from flask_login import login_required, current_user
from . import study
from .. import db
from ..models import Device
from ..models import LessonType, Lesson, Video
from ..models import Punch
from ..decorators import permission_required
from ..utils import get_mac_address_from_ip
from ..utils2 import add_user_log


@study.route('/vb')
@login_required
@permission_required('研修VB')
def vb():
    '''study.vb()'''
    lesson_type = 'VB'
    lessons = Lesson.query\
        .join(LessonType, LessonType.id == Lesson.type_id)\
        .filter(LessonType.name == lesson_type)\
        .order_by(Lesson.id.asc())
    return minify(render_template(
        'study/lesson.html',
        header=lesson_type,
        lessons=lessons
    ))


@study.route('/y-gre')
@login_required
@permission_required('研修Y-GRE')
def y_gre():
    '''study.y_gre()'''
    lesson_type = 'Y-GRE'
    lessons = Lesson.query\
        .join(LessonType, LessonType.id == Lesson.type_id)\
        .filter(LessonType.name == lesson_type)\
        .order_by(Lesson.id.asc())
    return minify(render_template(
        'study/lesson.html',
        header=lesson_type,
        lessons=lessons
    ))


@study.route('/y-gre-aw')
@login_required
@permission_required('研修Y-GRE')
def y_gre_aw():
    '''study.y_gre_aw()'''
    lesson_type = 'Y-GRE AW'
    lessons = Lesson.query\
        .join(LessonType, LessonType.id == Lesson.type_id)\
        .filter(LessonType.name == lesson_type)\
        .order_by(Lesson.id.asc())
    return minify(render_template(
        'study/lesson.html',
        header=lesson_type,
        lessons=lessons
    ))


@study.route('/test-review')
@login_required
@permission_required('研修Y-GRE')
def test_review():
    '''study.test_review()'''
    lesson_type = '考试讲解'
    lessons = Lesson.query\
        .join(LessonType, LessonType.id == Lesson.type_id)\
        .filter(LessonType.name == lesson_type)\
        .order_by(Lesson.id.asc())
    return minify(render_template(
        'study/lesson.html',
        header=lesson_type,
        lessons=lessons
    ))


@study.route('/demo')
def demo():
    '''study.demo()'''
    mac_address = get_mac_address_from_ip(ip_address=request.headers.get('X-Forwarded-For', request.remote_addr))
    if mac_address is None:
        flash('无法获取设备信息', category='error')
        return redirect(url_for('auth.login'))
    device = Device.query.filter_by(mac_address=mac_address).first()
    if device is None:
        flash('设备未授权（MAC地址：{}）'.format(mac_address), category='error')
        return redirect(url_for('auth.login'))
    lesson_type = '体验课程'
    if not device.can_access_lesson_type(lesson_type_name=lesson_type):
        flash('该设备无法访问受限资源', category='error')
        return redirect(url_for('auth.login'))
    lessons = Lesson.query\
        .join(LessonType, LessonType.id == Lesson.type_id)\
        .filter(LessonType.name == lesson_type)\
        .order_by(Lesson.id.asc())
    return minify(render_template(
        'study/lesson.html',
        header=lesson_type,
        lessons=lessons
    ))


@study.route('/video/<int:id>')
@login_required
@permission_required('研修')
def video(id):
    '''study.video(id)'''
    video = Video.query.get_or_404(id)
    if not current_user.can_study(lesson=video.lesson):
        flash('请先完成本课程的前序内容！', category='warning')
        return redirect(url_for('study.{}'.format(video.lesson.type.view_point)))
    if not current_user.punched(video=video):
        add_user_log(user=current_user._get_current_object(), event='视频研修：{}'.format(video.name), category='study')
        db.session.commit()
    return minify(render_template(
        'study/video.html',
        video=video
    ))


@study.route('/punch/<int:id>', methods=['POST'])
@login_required
@permission_required('研修')
def punch(id):
    '''study.punch(id)'''
    video = Video.query.get_or_404(id)
    if not current_user.can('研修{}'.format(video.lesson.type.name)) or not current_user.can_study(lesson=video.lesson):
        abort(403)
    if request.json is None:
        abort(500)
    current_user.punch(video=video, play_time=request.json.get('play_time'))
    db.session.commit()
    return jsonify(current_user.video_punch(video=video).to_json())
