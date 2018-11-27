# -*- coding: utf-8 -*-

'''app/resource/views.py'''

import os
from htmlmin import minify
from flask import send_file, redirect, request, url_for, abort, current_app
from flask_login import login_required, current_user
from . import resource
from ..models import Video
from ..utils import send_video_file, hls_wrapper
from ..decorators import permission_required


@resource.route('/video/<int:id>')
@login_required
@permission_required('研修')
def video(id):
    '''resource.video(id)'''
    video = Video.query.get_or_404(id)
    if not current_user.can_play(video=video):
        return redirect(url_for('resource.video_forbidden'))
    video_file = os.path.join(current_app.config['VIDEO_DIR'], video.file_name)
    if not os.path.exists(video_file):
        abort(404)
    if current_app.config['HLS_ENABLE']:
        return hls_wrapper(video_file=video_file)
    if 'Range' in request.headers:
        return send_video_file(video_file=video_file, request=request)
    return send_file(video_file, mimetype='video/mp4')


@resource.route('/video/forbidden')
@login_required
@permission_required('研修')
def video_forbidden():
    '''resource.video_forbidden()'''
    video_file = os.path.join(current_app.config['VIDEO_DIR'], 'forbidden.mp4')
    if not os.path.exists(video_file):
        abort(404)
    if current_app.config['HLS_ENABLE']:
        return hls_wrapper(video_file=video_file)
    if 'Range' in request.headers:
        return send_video_file(video_file=video_file, request=request)
    return send_file(video_file, mimetype='video/mp4')
