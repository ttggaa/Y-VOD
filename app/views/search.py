# -*- coding: utf-8 -*-

'''app/views/search.py'''

from sqlalchemy import or_
from flask import Blueprint, request, current_app, jsonify
from flask_login import login_required, current_user
from app.models import User
from app.decorators import permission_required


search = Blueprint('search', __name__)


@search.route('/profile')
@login_required
@permission_required('管理')
def profile():
    '''search.profile()'''
    users = []
    keyword = request.args.get('keyword')
    if keyword:
        users = User.query\
            .filter(or_(
                User.name.like('%' + keyword + '%'),
                User.name_pinyin.like('%' + keyword + '%')
            ))\
            .order_by(User.last_seen_at.desc())\
            .limit(current_app.config['RECORD_PER_QUERY'])\
            .all()
    tab = request.args.get('tab')
    return jsonify({'results': [user.profile_json(url_tab=tab) for user in users if not user.is_superior_than(user=current_user._get_current_object())]})
