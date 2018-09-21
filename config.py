# -*- coding: utf-8 -*-

import os
import sys
from datetime import datetime


basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    # Directories
    BASE_DIR = basedir
    DATA_DIR = os.path.join(BASE_DIR, 'data')

    # Version
    PYTHON_VERSION = '{0.major}.{0.minor}.{0.micro}'.format(sys.version_info)
    VERSION = '1.0.0'
    ESTABLISHED_AT = '2018-08-05T00:00+08:00'
    UPDATED_AT = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
    RENDERED_AT = datetime.utcnow

    # SSL
    SSL_DISABLE = True

    # SQLAlchemy
    SQLALCHEMY_RECORD_QUERIES = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SLOW_DB_QUERY_TIME = 0.5 # seconds

    # Query
    RECORD_PER_PAGE = 20
    RECORD_PER_PAGE_FEWER = 10
    RECORD_PER_QUERY = 50

    # Time
    UTC_OFFSET = 8 # hours
    COOKIE_MAX_AGE = 30 * 24 * 60 * 60 # 30 days

    # Authentication
    MAX_INVALID_LOGIN_COUNT = 10

    # iPad
    LOW_BATTERY_LEVEL = 30

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    ENV = 'development'
    DEBUG = True

    # Security
    SECRET_KEY = os.getenv('YVOD_DEV_SECRET_KEY')

    # Database
    SQLALCHEMY_DATABASE_URI = 'sqlite:///{}'.format(os.path.join(basedir, 'ysys-dev.sqlite'))


class ProductionConfig(Config):
    # Security
    SECRET_KEY = os.getenv('YVOD_PROD_SECRET_KEY')

    # Database
    SQLALCHEMY_DATABASE_URI = os.getenv('YVOD_PROD_DATABASE_URL')

    @classmethod
    def init_app(cls, app):
        Config.init_app(app)


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,

    'default': DevelopmentConfig,
}
