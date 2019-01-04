# -*- coding: utf-8 -*-

'''app/resource/views.py'''

import os
from flask import send_file, redirect, request, url_for, abort, current_app
from flask_login import login_required, current_user
from . import resource
from ..models import Device
from ..models import Video
from ..utils import get_mac_address_from_ip, send_video_file
from ..decorators import permission_required


@resource.route('/video/<int:id>')
@login_required
@permission_required('研修')
def video(id):
    '''resource.video(id)'''
    if current_app.config['HLS_ENABLE']:
        abort(403)
    video = Video.query.get_or_404(id)
    if not current_user.can_play(video=video):
        return redirect(url_for('resource.video_forbidden'))
    video_file = os.path.join(current_app.config['VIDEO_DIR'], video.file_name)
    if not os.path.exists(video_file):
        abort(404)
    if 'Range' in request.headers:
        return send_video_file(video_file=video_file, request=request)
    return send_file(video_file, mimetype='video/mp4')


@resource.route('/demo/video/<int:id>')
def demo_video(id):
    '''resource.demo_video(id)'''
    mac_address = get_mac_address_from_ip(ip_address=request.headers.get('X-Forwarded-For', request.remote_addr))
    if mac_address is None:
        abort(403)
    device = Device.query.filter_by(mac_address=mac_address).first()
    if device is None:
        abort(403)
    if current_app.config['HLS_ENABLE']:
        abort(403)
    video = Video.query.get_or_404(id)
    lesson_type_name = video.lesson.type.name
    if not device.can_access_lesson_type(lesson_type_name=lesson_type_name):
        abort(403)
    video_file = os.path.join(current_app.config['VIDEO_DIR'], video.file_name)
    if not os.path.exists(video_file):
        abort(404)
    if 'Range' in request.headers:
        return send_video_file(video_file=video_file, request=request)
    return send_file(video_file, mimetype='video/mp4')


@resource.route('/video/forbidden')
def video_forbidden():
    '''resource.video_forbidden()'''
    if current_app.config['HLS_ENABLE']:
        abort(403)
    video_file = os.path.join(current_app.config['VIDEO_DIR'], 'forbidden.mp4')
    if not os.path.exists(video_file):
        abort(404)
    if 'Range' in request.headers:
        return send_video_file(video_file=video_file, request=request)
    return send_file(video_file, mimetype='video/mp4')
