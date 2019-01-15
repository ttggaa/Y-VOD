# -*- coding: utf-8 -*-

'''app/views/main.py'''

from htmlmin import minify
from flask import Blueprint, render_template, jsonify, redirect, request, url_for, abort, current_app
from flask_login import current_user
from flask_sqlalchemy import get_debug_queries
from flask_wtf.csrf import CSRFError


main = Blueprint('main', __name__)


@main.app_errorhandler(403)
def forbidden(e):
    '''main.forbidden(e)'''
    if request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html:
        response = jsonify({'error': 'forbidden'})
        response.status_code = 403
        return response
    return minify(render_template('error/403.html')), 403


@main.app_errorhandler(404)
def page_not_found(e):
    '''main.page_not_found(e)'''
    if request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html:
        response = jsonify({'error': 'not found'})
        response.status_code = 404
        return response
    return minify(render_template('error/404.html')), 404


@main.app_errorhandler(500)
def internal_server_error(e):
    '''main.internal_server_error(e)'''
    if request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html:
        response = jsonify({'error': 'internal server error'})
        response.status_code = 500
        return response
    return minify(render_template('error/500.html')), 500


@main.app_errorhandler(CSRFError)
def csrf_error(e):
    '''main.csrf_error(e)'''
    if request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html:
        response = jsonify({'error': 'csrf error'})
        response.status_code = 400
        return response
    return render_template('error/csrf.html'), 400


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
