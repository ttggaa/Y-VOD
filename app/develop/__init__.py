# -*- coding: utf-8 -*-

from flask import Blueprint


develop = Blueprint('develop', __name__)


from . import views
