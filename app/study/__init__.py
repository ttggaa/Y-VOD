# -*- coding: utf-8 -*-

'''app/study/__init__.py'''

from flask import Blueprint


study = Blueprint('study', __name__)


from . import views
