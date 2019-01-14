# -*- coding: utf-8 -*-

'''app/main/errors.py'''

from htmlmin import minify
from flask import render_template, request, jsonify
from flask_wtf.csrf import CSRFError
from . import main


@main.app_errorhandler(403)
def forbidden(e):
    '''errors.forbidden(e)'''
    if request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html:
        response = jsonify({'error': 'forbidden'})
        response.status_code = 403
        return response
    return minify(render_template('error/403.html')), 403


@main.app_errorhandler(404)
def page_not_found(e):
    '''errors.page_not_found(e)'''
    if request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html:
        response = jsonify({'error': 'not found'})
        response.status_code = 404
        return response
    return minify(render_template('error/404.html')), 404


@main.app_errorhandler(500)
def internal_server_error(e):
    '''errors.internal_server_error(e)'''
    if request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html:
        response = jsonify({'error': 'internal server error'})
        response.status_code = 500
        return response
    return minify(render_template('error/500.html')), 500


@main.app_errorhandler(CSRFError)
def csrf_error(e):
    '''errors.csrf_error(e)'''
    if request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html:
        response = jsonify({'error': 'csrf error'})
        response.status_code = 400
        return response
    return render_template('error/csrf.html'), 400
