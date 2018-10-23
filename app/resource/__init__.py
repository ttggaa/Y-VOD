# -*- coding: utf-8 -*-

'''app/resource/__init__.py'''

from flask import Blueprint


resource = Blueprint('resource', __name__)


from . import views
