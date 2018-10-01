# -*- coding: utf-8 -*-

'''app/auth/__init___.py'''

from flask import Blueprint


auth = Blueprint('auth', __name__)


from . import views
