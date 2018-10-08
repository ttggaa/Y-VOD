# -*- coding: utf-8 -*-

'''app/manage/__init__.py'''

from flask import Blueprint


manage = Blueprint('manage', __name__)


from . import views
