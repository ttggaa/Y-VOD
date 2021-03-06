# -*- coding: utf-8 -*-

'''app/views/profile.py'''

from htmlmin import minify
from flask import Blueprint
from flask import render_template, request, abort
from flask import current_app
from flask_login import login_required, current_user
from app.models import User
from app.models import UserLog
from app.models import LessonType, Lesson


profile = Blueprint('profile', __name__)


@profile.route('/<int:id>/overview')
@login_required
def overview(id):
    '''profile.overview(id)'''
    tab = 'overview'
    user = User.query.get_or_404(id)
    if not current_user.can_access_profile(user=user):
        abort(403)
    lessons = Lesson.query\
        .join(LessonType, LessonType.id == Lesson.type_id)\
        .filter(LessonType.login_required == True)\
        .order_by(Lesson.id.asc())
    return minify(render_template(
        'profile/overview.html',
        profile_tab=tab,
        user=user,
        lessons=lessons
    ))


@profile.route('/<int:id>/timeline')
@login_required
def timeline(id):
    '''profile.timeline(id)'''
    tab = 'timeline'
    user = User.query.get_or_404(id)
    if not current_user.can_access_profile(user=user):
        abort(403)
    if current_user.is_developer:
        query = UserLog.query\
            .filter(UserLog.user_id == user.id)\
            .order_by(UserLog.timestamp.desc())
    else:
        query = UserLog.query\
            .filter(UserLog.user_id == user.id)\
            .filter(UserLog.category.notin_(['auth', 'access']))\
            .order_by(UserLog.timestamp.desc())
    page = request.args.get('page', 1, type=int)
    pagination = query.paginate(
        page,
        per_page=current_app.config['RECORD_PER_PAGE'],
        error_out=False
    )
    logs = pagination.items
    return minify(render_template(
        'profile/timeline.html',
        profile_tab=tab,
        user=user,
        pagination=pagination,
        logs=logs
    ))
