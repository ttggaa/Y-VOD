# -*- coding: utf-8 -*-

'''app/profile/views.py'''

from htmlmin import minify
from flask import render_template, redirect, request, url_for, abort, current_app
from flask_login import login_required, current_user
from . import profile
from ..models import User
from ..decorators import permission_required


@profile.route('/<int:id>/overview')
@login_required
def overview(id):
    '''profile.overview(id)'''
    tab = 'overview'
    user = User.query.get_or_404(id)
    if (user.id != current_user.id and not current_user.can('管理')) or user.is_superior_than(user=current_user._get_current_object()):
        abort(403)
    return minify(render_template(
        'profile/overview.html',
        profile_tab=tab,
        user=user
    ))
