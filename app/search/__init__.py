# -*- coding: utf-8 -*-

'''app/search/__init__.py'''

from flask import Blueprint


search = Blueprint('search', __name__)


from . import views
