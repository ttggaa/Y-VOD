# -*- coding: utf-8 -*-

'''app/profile/__init___.py'''

from flask import Blueprint


profile = Blueprint('profile', __name__)


from . import views
