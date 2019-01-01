# -*- coding: utf-8 -*-

'''app/study/views.py'''

from htmlmin import minify
from flask import render_template, jsonify, redirect, request, url_for, abort, flash, current_app
from flask_login import login_required, current_user
from . import study
from .. import db
from ..models import Device
from ..models import LessonType, Lesson, Video
from ..models import VideoCollection, Collection
from ..models import Punch
from ..decorators import permission_required
from ..utils import get_mac_address_from_ip
from ..utils2 import add_user_log


@study.route('/collection')
def collection():
    '''study.collection()'''
    mac_address = get_mac_address_from_ip(ip_address=request.headers.get('X-Forwarded-For', request.remote_addr))
    if mac_address is None:
        flash('无法获取设备信息', category='error')
        return redirect(url_for('auth.login'))
    device = Device.query.filter_by(mac_address=mac_address).first()
    if device is None:
        flash('设备未授权（MAC地址：{}）'.format(mac_address), category='error')
        return redirect(url_for('auth.login'))
    if not device.restricted_permit:
        flash('该设备无法访问受限资源', category='error')
        return redirect(url_for('auth.login'))
    collection_name = request.args.get('name')
    if collection_name is None:
        abort(404)
    collection = Collection.query.filter_by(name=collection_name).first()
    if collection is None:
        abort(404)
    query = Video.query\
        .join(VideoCollection, VideoCollection.video_id == Video.id)\
        .join(Collection, Collection.id == VideoCollection.collection_id)\
        .filter(Collection.name == collection.name)\
        .order_by(Video.id.asc())
    video_id = request.args.get('video_id')
    if video_id is not None:
        video = Video.query.get_or_404(video_id)
        if not collection.has_video(video=video):
            abort(403)
    else:
        video = query.first()
    videos = query.all()
    return minify(render_template(
        'study/collection.html',
        collection=collection,
        video=video,
        videos=videos
    ))


@study.route('/vb')
@login_required
@permission_required('研修VB')
def vb():
    '''study.vb()'''
    header = 'VB研修'
    lessons = Lesson.query\
        .join(LessonType, LessonType.id == Lesson.type_id)\
        .filter(LessonType.name == 'VB')\
        .order_by(Lesson.id.asc())
    return minify(render_template(
        'study/lesson.html',
        header=header,
        lessons=lessons
    ))


@study.route('/y-gre')
@login_required
@permission_required('研修Y-GRE')
def y_gre():
    '''study.y_gre()'''
    header = 'Y-GRE研修'
    lessons = Lesson.query\
        .join(LessonType, LessonType.id == Lesson.type_id)\
        .filter(LessonType.name == 'Y-GRE')\
        .order_by(Lesson.id.asc())
    return minify(render_template(
        'study/lesson.html',
        header=header,
        lessons=lessons
    ))


@study.route('/video/<int:id>')
@login_required
@permission_required('研修')
def video(id):
    '''study.video(id)'''
    video = Video.query.get_or_404(id)
    if video.restricted:
        abort(403)
    if not current_user.can('研修{}'.format(video.lesson.type.name)):
        abort(403)
    if not current_user.can_study(lesson=video.lesson):
        flash('请先完成本课程的前序内容！', category='warning')
        return redirect(url_for('study.{}'.format(video.lesson.type.name_snake_case)))
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
    if video.restricted:
        abort(403)
    if not current_user.can('研修{}'.format(video.lesson.type.name)) or not current_user.can_study(lesson=video.lesson):
        abort(403)
    if request.json is None:
        abort(500)
    current_user.punch(video=video, play_time=request.json.get('play_time'))
    db.session.commit()
    return jsonify(current_user.video_punch(video=video).to_json())
