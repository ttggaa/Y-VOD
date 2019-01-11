# -*- coding: utf-8 -*-

'''app/demo/__init__.py'''

from flask import Blueprint


demo = Blueprint('demo', __name__)


from . import views
