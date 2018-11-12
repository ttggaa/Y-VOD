# -*- coding: utf-8 -*-

'''config.py'''

import os
import sys
from datetime import datetime


basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    '''Config'''

    # Directories
    BASE_DIR = basedir
    DATA_DIR = os.path.join(BASE_DIR, 'data')
    VIDEO_DIR = os.path.join(DATA_DIR, 'videos')

    # SSL
    SSL_DISABLE = True

    # Security
    AUTH_TOKEN_SECRET_KEY = os.getenv('YVOD_AUTH_TOKEN_SECRET_KEY')

    # SQLAlchemy
    SQLALCHEMY_RECORD_QUERIES = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SLOW_DB_QUERY_TIME = 0.5 # seconds

    # Query
    RECORD_PER_PAGE = 20
    RECORD_PER_PAGE_FEWER = 10
    RECORD_PER_QUERY = 50

    # Time
    DATETIME_FORMAT = '%Y-%m-%dT%H:%M:%S'
    DATETIME_FORMAT_ISO = '%Y-%m-%dT%H:%M:%SZ'
    UTC_OFFSET = 8 # hours
    COOKIE_MAX_AGE = 30 * 24 * 60 * 60 # 30 days
    STATUS_EXPIRATION_CHECK_INTERVAL = 1000 # milliseconds (1 second)

    # Video Analytics
    VIDEO_ANALYTICS_GRANULARITY = 100 # milliseconds (0.1 seconds)
    VIDEO_ANALYTICS_UPDATE_PUNCH_INTERVAL = 60 * 1000 # 1 minute
    VIDEO_ANALYTICS_STATUS_EXPIRATION = 300 # seconds (5 minutes)

    # Video Streaming

    # Version
    PYTHON_VERSION = '{0.major}.{0.minor}.{0.micro}'.format(sys.version_info)
    VERSION = '1.0.0'
    ESTABLISHED_AT = '2018-08-05T00:00:00+08:00'
    UPDATED_AT = datetime.utcnow().strftime(DATETIME_FORMAT_ISO)
    RENDERED_AT = datetime.utcnow

    @staticmethod
    def init_app(app):
        '''init_app(app)'''
        pass


class DevelopmentConfig(Config):
    '''DevelopmentConfig(Config)'''

    ENV = 'development'
    DEBUG = True

    # Security
    SECRET_KEY = os.getenv('YVOD_DEV_SECRET_KEY')

    # Database
    SQLALCHEMY_DATABASE_URI = 'sqlite:///{}'.format(os.path.join(basedir, 'yvod-dev.sqlite'))

    # Development
    SYSTEM_OPERATOR_NAME = os.getenv('YVOD_DEV_SYSTEM_OPERATOR_NAME')
    SYSTEM_OPERATOR_TOKEN = os.getenv('YVOD_DEV_SYSTEM_OPERATOR_TOKEN')
    DEVELOPMENT_MACHINE_SERIAL = os.getenv('YVOD_DEV_DEVELOPMENT_MACHINE_SERIAL')
    DEVELOPMENT_MACHINE_MAC_ADDRESS = os.getenv('YVOD_DEV_DEVELOPMENT_MACHINE_MAC_ADDRESS')

    # Video Streaming
    VIDEO_STREAMING_DISABLE = True


class ProductionConfig(Config):
    '''ProductionConfig(Config)'''

    ENV = 'production'

    # Security
    SECRET_KEY = os.getenv('YVOD_PROD_SECRET_KEY')

    # Database
    SQLALCHEMY_DATABASE_URI = os.getenv('YVOD_PROD_DATABASE_URL')

    # Development
    SYSTEM_OPERATOR_NAME = os.getenv('YVOD_PROD_SYSTEM_OPERATOR_NAME')
    SYSTEM_OPERATOR_TOKEN = os.getenv('YVOD_PROD_SYSTEM_OPERATOR_TOKEN')
    DEVELOPMENT_MACHINE_SERIAL = os.getenv('YVOD_PROD_DEVELOPMENT_MACHINE_SERIAL')
    DEVELOPMENT_MACHINE_MAC_ADDRESS = os.getenv('YVOD_PROD_DEVELOPMENT_MACHINE_MAC_ADDRESS')

    # Video Streaming
    VIDEO_STREAMING_DISABLE = False


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,

    'default': DevelopmentConfig,
}
