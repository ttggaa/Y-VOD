# -*- coding: utf-8 -*-

'''app/develop/__init___.py'''

from flask import Blueprint


develop = Blueprint('develop', __name__)


from . import views
