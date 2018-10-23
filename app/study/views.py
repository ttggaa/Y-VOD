# -*- coding: utf-8 -*-

'''app/study/views.py'''

from htmlmin import minify
from flask import render_template, redirect, request, url_for, abort, current_app
from flask_login import login_required, current_user
from . import study
from ..models import LessonType, Lesson, Video
from ..decorators import permission_required


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
    return minify(render_template(
        'study/video.html',
        video=video
    ))
