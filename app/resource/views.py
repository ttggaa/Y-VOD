# -*- coding: utf-8 -*-

'''app/resource/views.py'''

import os
from htmlmin import minify
from flask import send_file, redirect, url_for, abort, current_app
from flask_login import login_required, current_user
from . import resource
from ..models import Video
from ..decorators import permission_required
from ..utils import stream_video


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
    return stream_video(video_file, mimetype='video/mp4')


@resource.route('/video/forbidden')
@login_required
@permission_required('研修')
def video_forbidden():
    '''resource.video_forbidden()'''
    video_file = os.path.join(current_app.config['VIDEO_DIR'], 'forbidden.mp4')
    if not os.path.exists(video_file):
        abort(404)
    return stream_video(video_file, mimetype='video/mp4')
