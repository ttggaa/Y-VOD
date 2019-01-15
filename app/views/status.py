# -*- coding: utf-8 -*-

'''app/views/status.py'''

from datetime import datetime, timedelta
from htmlmin import minify
from flask import Blueprint, render_template, current_app
from flask_login import login_required, current_user
from app.models import Role, User
from app.models import Punch
from app.decorators import permission_required


status = Blueprint('status', __name__)


@status.route('/')
@login_required
@permission_required('管理')
def home():
    '''status.home()'''
    if current_user.is_developer:
        user_ids = list({punch.user_id for punch in Punch.query\
            .filter(Punch.timestamp >= datetime.utcnow() - timedelta(seconds=current_app.config['VIDEO_ANALYTICS_STATUS_EXPIRATION']))\
            .order_by(Punch.timestamp.desc())\
            .all()})
    else:
        user_ids = list({punch.user_id for punch in Punch.query\
            .join(User, User.id == Punch.user_id)\
            .join(Role, Role.id == User.role_id)\
            .filter(Role.category == 'student')\
            .filter(Punch.timestamp >= datetime.utcnow() - timedelta(seconds=current_app.config['VIDEO_ANALYTICS_STATUS_EXPIRATION']))\
            .order_by(Punch.timestamp.desc())\
            .all()})
    users = User.query.filter(User.id.in_(user_ids))
    return minify(render_template(
        'status/home.html',
        users=users
    ))
