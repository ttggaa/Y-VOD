# -*- coding: utf-8 -*-

'''app/main/views.py'''

from htmlmin import minify
from flask import render_template, redirect, request, url_for, abort, current_app
from flask_login import current_user
from flask_sqlalchemy import get_debug_queries
from . import main


@main.after_app_request
def after_request(response):
    '''main.after_request(response)'''
    for query in get_debug_queries():
        if query.duration >= current_app.config['SLOW_DB_QUERY_TIME']:
            current_app.logger.warning('Slow query: {}\nParameters: {}\nDuration: {:f}s\nContext: {}\n'.format(query.statement, query.parameters, query.duration, query.context))
    return response


@main.route('/shutdown')
def server_shutdown():
    '''main.server_shutdown()'''
    if not current_app.testing:
        abort(404)
    shutdown = request.environ.get('werkzeug.server.shutdown')
    if not shutdown:
        abort(500)
    shutdown()
    return 'Shutting down...'


@main.route('/')
def home():
    '''main.home()'''
    if current_user.is_authenticated:
        if current_user.is_staff:
            return redirect(request.args.get('next') or url_for('status.home'))
        return redirect(request.args.get('next') or url_for('profile.overview', id=current_user.id))
    return redirect(url_for('auth.login'))


@main.route('/terms')
def terms():
    '''main.terms()'''
    return minify(render_template('terms.html'))
