# -*- coding: utf-8 -*-

'''app/status/__init___.py'''

from flask import Blueprint


status = Blueprint('status', __name__)


from . import views