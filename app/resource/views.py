# -*- coding: utf-8 -*-

'''app/resource/views.py'''

import os
from htmlmin import minify
from flask import send_file, abort, current_app
from flask_login import login_required, current_user
from . import resource
from ..models import Video
from ..decorators import permission_required


@resource.route('/video/<int:id>')
@login_required
@permission_required('研修')
def video(id):
    '''resource.video(id)'''
    video = Video.query.get_or_404(id)
    if not current_user.can_play(video=video):
        abort(403)
    video_file = os.path.join(current_app.config['VIDEO_DIR'], video.file_name)
    return send_file(video_file, mimetype='video/mp4')
