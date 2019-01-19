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
    CACHE_DIR = os.path.join(BASE_DIR, 'cache')
    HLS_DIR = os.path.join(CACHE_DIR, 'hls')

    # SSL
    SSL_DISABLE = True

    # Security
    SECRET_KEY = os.getenv('YVOD_SECRET_KEY')
    AUTH_TOKEN_SECRET_KEY = os.getenv('YVOD_AUTH_TOKEN_SECRET_KEY')
    AUTH_REMEMBER_LOGIN = True

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
    TOKEN_EXPIRATION = 3600 # seconds
    REQUEST_TIMEOUT = 15 # seconds

    # Video Analytics
    VIDEO_ANALYTICS_ACCELERATING_FACTOR = 1.25 # speedup
    VIDEO_ANALYTICS_GRANULARITY = 100 # milliseconds (0.1 seconds)
    VIDEO_ANALYTICS_UPDATE_PUNCH_INTERVAL = 15 * 1000 # milliseconds (15 seconds)
    VIDEO_ANALYTICS_STATUS_EXPIRATION = 300 # seconds (5 minutes)

    # Y-System
    YSYS_URI = os.getenv('YVOD_YSYS_URL')

    # Development
    SYSTEM_OPERATOR_NAME = os.getenv('YVOD_SYSTEM_OPERATOR_NAME')
    SERVER_SERIAL = os.getenv('YVOD_SERVER_SERIAL')
    SERVER_MAC_ADDRESS = os.getenv('YVOD_SERVER_MAC_ADDRESS')

    # Version
    PYTHON_VERSION = '{0.major}.{0.minor}.{0.micro}'.format(sys.version_info)
    VERSION = '1.0.1'
    ESTABLISHED_AT = '2018-08-05T00:00:00+08:00'
    UPDATED_AT = datetime.utcnow().strftime(DATETIME_FORMAT_ISO)
    RENDERED_AT = datetime.utcnow

    @staticmethod
    def init_app(app):
        '''Config.init_app(app)'''
        pass


class DevelopmentConfig(Config):
    '''DevelopmentConfig(Config)'''

    ENV = 'development'
    DEBUG = True

    # Database
    SQLALCHEMY_DATABASE_URI = 'sqlite:///{}'.format(os.path.join(basedir, 'yvod-dev.sqlite'))

    # HLS
    HLS_ENABLE = False


class ProductionConfig(Config):
    '''ProductionConfig(Config)'''

    ENV = 'production'

    # Database
    SQLALCHEMY_DATABASE_URI = os.getenv('YVOD_PROD_DATABASE_URL')

    # Mail
    MAIL_SERVER = 'smtp.exmail.qq.com'
    MAIL_PORT = 587
    MAIL_USE_TSL = True
    MAIL_USERNAME = os.getenv('YVOD_MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('YVOD_MAIL_PASSWORD')
    MAIL_SUBJECT_PREFIX = os.getenv('YVOD_MAIL_SUBJECT_PREFIX')
    MAIL_SENDER = os.getenv('YVOD_MAIL_SENDER')
    SYSTEM_OPERATOR_MAIL = os.getenv('YVOD_SYSTEM_OPERATOR_MAIL')

    # HLS
    HLS_ENABLE = True

    @classmethod
    def init_app(cls, app):
        '''ProductionConfig.init_app(cls, app)'''
        Config.init_app(app)
        # email errors to the system operator
        import logging
        from logging.handlers import SMTPHandler
        credentials = None
        secure = None
        if getattr(cls, 'MAIL_USERNAME', None) is not None:
            credentials = (cls.MAIL_USERNAME, cls.MAIL_PASSWORD)
            if getattr(cls, 'MAIL_USE_TSL', None):
                secure = ()
        mail_handler = SMTPHandler(
            mailhost=(cls.MAIL_SERVER, cls.MAIL_PORT),
            fromaddr=cls.MAIL_SENDER,
            toaddrs=[cls.SYSTEM_OPERATOR_MAIL],
            subject='{} Application Error'.format(cls.MAIL_SUBJECT_PREFIX),
            credentials=credentials,
            secure=secure
        )
        mail_handler.setLevel(logging.ERROR)
        app.logger.addHandler(mail_handler)


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,

    'default': DevelopmentConfig,
}
