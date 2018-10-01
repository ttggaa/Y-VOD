# -*- coding: utf-8 -*-

'''app/decorators.py'''

from functools import wraps
from flask import abort
from flask_login import current_user


def permission_required(permission_name):
    '''permission_required(permission_name)'''
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.can(permission_name):
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def role_required(role_name):
    '''role_required(role_name)'''
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.plays(role_name):
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator
