# -*- coding: utf-8 -*-

'''app/study/views.py'''

from htmlmin import minify
from flask import render_template, redirect, request, url_for, abort, flash, current_app
from flask_login import login_required, current_user
from . import study
from .. import db
from ..models import LessonType, Lesson, Video
from ..decorators import permission_required
from ..utils2 import add_user_log


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
    if not current_user.can('研修{}'.format(video.lesson.type.name)):
        abort(403)
    if not current_user.can_study(lesson=video.lesson):
        flash('请先完成本课程的前序内容！', category='warning')
        return redirect(url_for('study.{}'.format(video.lesson.type.snake_case)))
    current_user.punch(video=video)
    add_user_log(user=current_user._get_current_object(), event='视频研修：{}'.format(video.name), category='study')
    db.session.commit()
    return minify(render_template(
        'study/video.html',
        video=video
    ))
