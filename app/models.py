# -*- coding: utf-8 -*-

'''app/models.py'''

from flask_login import UserMixin, AnonymousUserMixin
from . import db


class RolePermission(db.Model):
    '''Table: role_permissions'''
    __tablename__ = 'role_permissions'
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'), primary_key=True)
    permission_id = db.Column(db.Integer, db.ForeignKey('permissions.id'), primary_key=True)


class Permission(db.Model):
    '''Table: permissions'''
    __tablename__ = 'permissions'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Unicode(64), unique=True, index=True)
    category = db.Column(db.Unicode(64), index=True)
    roles = db.relationship(
        'RolePermission',
        foreign_keys=[RolePermission.permission_id],
        backref=db.backref('permission', lazy='joined'),
        lazy='dynamic',
        cascade='all, delete-orphan'
    )

    def __repr__(self):
        return '<Permission {}>'.format(self.name)


class Role(db.Model):
    '''Table: roles'''
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Unicode(64), unique=True, index=True)
    category = db.Column(db.Unicode(64), index=True)
    level = db.Column(db.Integer, nullable=False)
    permissions = db.relationship(
        'RolePermission',
        foreign_keys=[RolePermission.role_id],
        backref=db.backref('role', lazy='joined'),
        lazy='dynamic',
        cascade='all, delete-orphan'
    )
    users = db.relationship('User', backref='role', lazy='dynamic')

    def __repr__(self):
        return '<Role {}>'.format(self.name)


class IDType(object):
    '''Table: id_types'''
    __tablename__ = 'id_types'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Unicode(64), unique=True, index=True)
    users = db.relationship('User', backref='id_type', lazy='dynamic')

    @staticmethod
    def insert_entries(data, basedir, verbose=False):
        datafile = os.path.join(basedir, 'data', data, 'id_types.yml')
        entries = load_yaml(datafile=datafile)
        if entries is not None:
            print('---> Read: {}'.format(datafile))
            for entry in entries:
                id_type = IDType(name=entry['name'])
                db.session.add(id_type)
                if verbose:
                    print('导入ID类型信息', entry['name'])
            db.session.commit()
        else:
            print('文件不存在', datafile)

    def __repr__(self):
        return '<ID Type {}>'.format(self.name)


class Gender(db.Model):
    '''Table: genders'''
    __tablename__ = 'genders'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Unicode(64), unique=True, index=True)
    users = db.relationship('User', backref='gender', lazy='dynamic')

    @staticmethod
    def insert_entries(data, basedir, verbose=False):
        datafile = os.path.join(basedir, 'data', data, 'genders.yml')
        entries = load_yaml(datafile=datafile)
        if entries is not None:
            print('---> Read: {}'.format(datafile))
            for entry in entries:
                gender = Gender(name=entry['name'])
                db.session.add(gender)
                if verbose:
                    print('导入性别类型信息', entry['name'])
            db.session.commit()
        else:
            print('文件不存在', datafile)

    def __repr__(self):
        return '<Gender {}>'.format(self.name)


class User(UserMixin, db.Model):
    '''Table: users'''
    __tablename__ = 'users'
    # basic properties
    id = db.Column(db.Integer, primary_key=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    created_at = db.Column(db.DateTime)
    last_seen_at = db.Column(db.DateTime)
    last_seen_ip = db.Column(db.Unicode(64))
    invalid_login_count = db.Column(db.Integer, default=0)
    deleted = db.Column(db.Boolean, default=False)
    # profile properties
    name = db.Column(db.Unicode(64), index=True)
    name_pinyin = db.Column(db.Unicode(64), index=True)
    id_type_id = db.Column(db.Integer, db.ForeignKey('id_types.id'))
    id_number = db.Column(db.Unicode(64), index=True)
    gender_id = db.Column(db.Integer, db.ForeignKey('genders.id'))
    # study properties
    time_factor = db.Column(db.Float, default=1.0)

    def ping(self):
        self.last_seen_at = datetime.utcnow()
        db.session.add(self)

    def update_ip(self, ip_address):
        self.last_seen_ip = ip_address
        db.session.add(self)

    def increase_invalid_login_count(self):
        self.invalid_login_count += 1
        db.session.add(self)

    def reset_invalid_login_count(self):
        self.invalid_login_count = 0
        db.session.add(self)

    @property
    def locked(self):
        return self.invalid_login_count >= current_app.config['MAX_INVALID_LOGIN_COUNT']


class Room(db.Model):
    '''Table: rooms'''
    __tablename__ = 'rooms'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Unicode(64), unique=True, index=True)
    client_devices = db.relationship('ClientDevice', backref='room', lazy='dynamic')

    @staticmethod
    def insert_entries(data, basedir, verbose=False):
        datafile = os.path.join(basedir, 'data', data, 'rooms.yml')
        entries = load_yaml(datafile=datafile)
        if entries is not None:
            print('---> Read: {}'.format(datafile))
            for entry in entries:
                room = Room(name=entry['name'])
                db.session.add(room)
                if verbose:
                    print('导入房间信息', entry['name'])
            db.session.commit()
        else:
            print('文件不存在', datafile)

    def __repr__(self):
        return '<Room {}>'.format(self.name)


class ClientDevice(db.Model):
    '''Table: client_devices'''
    __tablename__ = 'client_devices'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Unicode(64), unique=True, index=True)

    def __repr__(self):
        return '<Client Device {}>'.format(self.name)


class Lesson(db.Model):
    '''Table: lessons'''
    __tablename__ = 'lessons'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Unicode(64), unique=True, index=True)

    def __repr__(self):
        return '<Lesson {}>'.format(self.name)


class Video(db.Model):
    '''Table: videos'''
    __tablename__ = 'videos'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Unicode(64), unique=True, index=True)

    def __repr__(self):
        return '<Video {}>'.format(self.name)
