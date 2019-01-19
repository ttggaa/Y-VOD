# -*- coding: utf-8 -*-

'''app/views/study.py'''

from htmlmin import minify
from flask import Blueprint
from flask import render_template, jsonify, redirect, request, url_for, abort, flash
from flask_login import login_required, current_user
from app import db
from app.models import Device
from app.models import LessonType, Lesson, Video
from app.decorators import permission_required
from app.utils import get_mac_address_from_ip
from app.utils import y_system_api_request
from app.utils2 import add_user_log


study = Blueprint('study', __name__)


@study.route('/vb')
@login_required
@permission_required('研修VB')
def vb():
    '''study.vb()'''
    mac_address = get_mac_address_from_ip(ip_address=request.headers\
        .get('X-Forwarded-For', request.remote_addr))
    if mac_address is None:
        flash('无法获取设备信息', category='error')
        return redirect(url_for('auth.login'))
    device = Device.query.filter_by(mac_address=mac_address).first()
    if device is None:
        flash('设备未授权（MAC地址：{}）'.format(mac_address), category='error')
        return redirect(url_for('auth.login'))
    lesson_type = 'VB'
    if not device.can_access_lesson_type(lesson_type=lesson_type):
        flash('该设备无法访问“{}”资源'.format(lesson_type), category='error')
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


@study.route('/y-gre')
@login_required
@permission_required('研修Y-GRE')
def y_gre():
    '''study.y_gre()'''
    mac_address = get_mac_address_from_ip(ip_address=request.headers\
        .get('X-Forwarded-For', request.remote_addr))
    if mac_address is None:
        flash('无法获取设备信息', category='error')
        return redirect(url_for('auth.login'))
    device = Device.query.filter_by(mac_address=mac_address).first()
    if device is None:
        flash('设备未授权（MAC地址：{}）'.format(mac_address), category='error')
        return redirect(url_for('auth.login'))
    lesson_type = 'Y-GRE'
    if not device.can_access_lesson_type(lesson_type=lesson_type):
        flash('该设备无法访问“{}”资源'.format(lesson_type), category='error')
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


@study.route('/y-gre-aw')
@login_required
@permission_required('研修Y-GRE')
def y_gre_aw():
    '''study.y_gre_aw()'''
    mac_address = get_mac_address_from_ip(ip_address=request.headers\
        .get('X-Forwarded-For', request.remote_addr))
    if mac_address is None:
        flash('无法获取设备信息', category='error')
        return redirect(url_for('auth.login'))
    device = Device.query.filter_by(mac_address=mac_address).first()
    if device is None:
        flash('设备未授权（MAC地址：{}）'.format(mac_address), category='error')
        return redirect(url_for('auth.login'))
    lesson_type = 'Y-GRE AW'
    if not device.can_access_lesson_type(lesson_type=lesson_type):
        flash('该设备无法访问“{}”资源'.format(lesson_type), category='error')
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


@study.route('/test-review')
@login_required
@permission_required('研修Y-GRE')
def test_review():
    '''study.test_review()'''
    mac_address = get_mac_address_from_ip(ip_address=request.headers\
        .get('X-Forwarded-For', request.remote_addr))
    if mac_address is None:
        flash('无法获取设备信息', category='error')
        return redirect(url_for('auth.login'))
    device = Device.query.filter_by(mac_address=mac_address).first()
    if device is None:
        flash('设备未授权（MAC地址：{}）'.format(mac_address), category='error')
        return redirect(url_for('auth.login'))
    lesson_type = '考试讲解'
    if not device.can_access_lesson_type(lesson_type=lesson_type):
        flash('该设备无法访问“{}”资源'.format(lesson_type), category='error')
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
        add_user_log(
            user=current_user._get_current_object(),
            event='视频研修：{}'.format(video.name),
            category='study'
        )
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
    if not current_user.can('研修{}'.format(video.lesson.type.name)) or \
        not current_user.can_study(lesson=video.lesson):
        abort(403)
    if request.json is None:
        abort(500)
    current_user.punch(video=video, play_time=request.json.get('play_time'))
    db.session.commit()
    if video.lesson.type.name in ['VB', 'Y-GRE', 'Y-GRE AW']:
        y_system_api_request(api='punch', token_data={
            'user_id': current_user.id,
            'section': video.name if video.lesson.type.name == 'VB' \
                else '{} 视频研修'.format(video.lesson.name),
            'progress': current_user.video_progress(video=video) \
                if video.lesson.type.name == 'VB' \
                else current_user.lesson_progress(lesson=video.lesson),
        })
    return jsonify(current_user.video_punch(video=video).to_json())