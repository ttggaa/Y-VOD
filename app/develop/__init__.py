# -*- coding: utf-8 -*-

'''app/develop/__init__.py'''

from flask import Blueprint


develop = Blueprint('develop', __name__)


from . import views
