# -*- coding: utf-8 -*-

'''app/models.py'''

import os
import io
from datetime import datetime, timedelta
from flask import current_app, url_for
from flask_login import UserMixin, AnonymousUserMixin
from . import db, login_manager
from .utils import CSVReader, CSVWriter, load_yaml, get_video_duration, to_pinyin


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

    @staticmethod
    def insert_entries(data, basedir, verbose=False):
        '''Permission.insert_entries(data, basedir, verbose=False)'''
        yaml_file = os.path.join(basedir, 'data', data, 'permissions.yml')
        entries = load_yaml(yaml_file=yaml_file)
        if entries is not None:
            print('---> Read: {}'.format(yaml_file))
            for entry in entries:
                permission = Permission(
                    name=entry['name'],
                    category=entry['category']
                )
                db.session.add(permission)
                if verbose:
                    print('导入用户权限信息', entry['name'], entry['category'])
            db.session.commit()
        else:
            print('文件不存在', yaml_file)

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

    def add_permission(self, permission):
        '''Role.add_permission(self, permission)'''
        if not self.has_permission(permission=permission):
            role_permission = RolePermission(role_id=self.id, permission_id=permission.id)
            db.session.add(role_permission)

    def remove_permission(self, permission):
        '''Role.remove_permission(self, permission)'''
        role_permission = self.permissions.filter_by(permission_id=permission.id).first()
        if role_permission is not None:
            db.session.delete(role_permission)

    def has_permission(self, permission):
        '''Role.has_permission(self, permission)'''
        return self.permissions.filter_by(permission_id=permission.id).first() is not None

    def permissions_alias(self, category=None, formatted=False):
        '''Role.permissions_alias(self, category=None, formatted=False)'''
        if category is not None:
            permissions = Permission.query\
                .join(RolePermission, RolePermission.permission_id == Permission.id)\
                .filter(RolePermission.role_id == self.id)\
                .filter(Permission.category == category)\
                .order_by(Permission.id.asc())
        else:
            permissions = Permission.query\
                .join(RolePermission, RolePermission.permission_id == Permission.id)\
                .filter(RolePermission.role_id == self.id)\
                .order_by(Permission.id.asc())
        if formatted:
            if permissions.count() == 0:
                return '无'
            if permissions.count() == 1:
                return permissions.first().name
            return ' · '.join([permission.name for permission in permissions.all()])
        return permissions

    def permissions_num(self, category=None):
        '''Role.permissions_num(self, category=None)'''
        if category is not None:
            return Permission.query\
                .join(RolePermission, RolePermission.permission_id == Permission.id)\
                .filter(RolePermission.role_id == self.id)\
                .filter(Permission.category == category)\
                .count()
        return self.permissions.count()

    def is_superior_than(self, role):
        '''Role.is_superior_than(self, role)'''
        return self.level > role.level

    @staticmethod
    def insert_entries(data, basedir, verbose=False):
        '''Role.insert_entries(data, basedir, verbose=False)'''
        yaml_file = os.path.join(basedir, 'data', data, 'roles.yml')
        entries = load_yaml(yaml_file=yaml_file)
        if entries is not None:
            print('---> Read: {}'.format(yaml_file))
            for entry in entries:
                role = Role(
                    name=entry['name'],
                    category=entry['category'],
                    level=entry['level']
                )
                db.session.add(role)
                db.session.commit()
                if verbose:
                    print('导入用户角色信息', entry['name'], entry['category'])
                for permission in entry['permissions']:
                    role.add_permission(permission=Permission.query.filter_by(name=permission).first())
                    if verbose:
                        print('赋予权限', entry['name'], permission)
                db.session.commit()
        else:
            print('文件不存在', yaml_file)

    def __repr__(self):
        return '<Role {}>'.format(self.name)


class IDType(db.Model):
    '''Table: id_types'''
    __tablename__ = 'id_types'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Unicode(64), unique=True, index=True)
    users = db.relationship('User', backref='id_type', lazy='dynamic')

    @staticmethod
    def insert_entries(data, basedir, verbose=False):
        '''IDType.insert_entries(data, basedir, verbose=False)'''
        yaml_file = os.path.join(basedir, 'data', data, 'id_types.yml')
        entries = load_yaml(yaml_file=yaml_file)
        if entries is not None:
            print('---> Read: {}'.format(yaml_file))
            for entry in entries:
                id_type = IDType(name=entry['name'])
                db.session.add(id_type)
                if verbose:
                    print('导入ID类型信息', entry['name'])
            db.session.commit()
        else:
            print('文件不存在', yaml_file)

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
        '''Gender.insert_entries(data, basedir, verbose=False)'''
        yaml_file = os.path.join(basedir, 'data', data, 'genders.yml')
        entries = load_yaml(yaml_file=yaml_file)
        if entries is not None:
            print('---> Read: {}'.format(yaml_file))
            for entry in entries:
                gender = Gender(name=entry['name'])
                db.session.add(gender)
                if verbose:
                    print('导入性别类型信息', entry['name'])
            db.session.commit()
        else:
            print('文件不存在', yaml_file)

    def __repr__(self):
        return '<Gender {}>'.format(self.name)


class User(UserMixin, db.Model):
    '''Table: users'''
    __tablename__ = 'users'
    # basic properties
    id = db.Column(db.Integer, primary_key=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
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
    # management properties
    modified_devices = db.relationship('Device', backref='modified_by', lazy='dynamic')
    # user logs
    user_logs = db.relationship('UserLog', backref='user', lazy='dynamic')

    def ping(self):
        '''User.ping(self)'''
        self.last_seen_at = datetime.utcnow()
        db.session.add(self)

    def update_ip(self, ip_address):
        '''User.update_ip(self, ip_address)'''
        self.last_seen_ip = ip_address
        db.session.add(self)

    @property
    def last_login_device(self):
        return Device.query.filter_by(ip_address=self.last_seen_ip).first()

    @property
    def last_login_device_with_ip(self):
        if self.last_login_device is not None:
            device_info = self.last_login_device.alias
        else:
            device_info = '未授权设备'
        return '{} ({})'.format(device_info, self.last_seen_ip)

    def increase_invalid_login_count(self):
        '''User.increase_invalid_login_count(self)'''
        self.invalid_login_count += 1
        db.session.add(self)

    def reset_invalid_login_count(self):
        '''User.reset_invalid_login_count(self)'''
        self.invalid_login_count = 0
        db.session.add(self)

    @property
    def locked(self):
        '''User.locked(self)'''
        return self.invalid_login_count >= current_app.config['MAX_INVALID_LOGIN_COUNT']

    def delete(self):
        '''User.delete(self)'''
        for user_log in self.user_logs:
            db.session.delete(user_log)
        db.session.delete(self)

    def safe_delete(self):
        '''User.safe_delete(self)'''
        self.role_id = Role.query.filter_by(name='挂起').first().id
        self.deleted = True
        db.session.add(self)

    def restore(self, role):
        '''User.restore(self, role)'''
        self.role_id = role.id
        self.deleted = False
        db.session.add(self)

    def can(self, permission_name):
        '''User.can(self, permission_name)'''
        permission = Permission.query.filter_by(name=permission_name).first()
        return permission is not None and \
            self.role is not None and \
            self.role.has_permission(permission=permission)

    def plays(self, role_name):
        '''User.plays(self, role_name)'''
        role = Role.query.filter_by(name=role_name).first()
        return role is not None and \
            self.role is not None and \
            (self.role.id == role.id or self.role.is_superior_than(role=role))

    @property
    def is_suspended(self):
        '''User.is_suspended(self)'''
        return self.role.name == '挂起'

    @property
    def is_student(self):
        '''User.is_student(self)'''
        return self.role.category == 'student'

    @property
    def is_staff(self):
        '''User.is_staff(self)'''
        return self.role.category == 'staff'

    @property
    def is_moderator(self):
        '''User.is_moderator(self)'''
        return self.role.name == '协管员'

    @property
    def is_administrator(self):
        '''User.is_administrator(self)'''
        return self.role.name == '管理员'

    @property
    def is_developer(self):
        '''User.is_developer(self)'''
        return self.role.name == '开发人员'

    def is_superior_than(self, user):
        '''User.is_superior_than(self, user)'''
        return self.role.is_superior_than(role=user.role)

    @staticmethod
    def on_changed_name(target, value, oldvalue, initiator):
        '''User.on_changed_name(target, value, oldvalue, initiator)'''
        name_pinyin = '{} {}'.format(to_pinyin(value), to_pinyin(value, initials=True))
        if name_pinyin != ' ':
            target.name_pinyin = name_pinyin

    @property
    def url(self):
        '''User.url(self)'''
        return url_for('profile.overview', id=self.id)

    @property
    def index_url(self):
        '''User.index_url(self)'''
        if self.can('管理'):
            return url_for('status.home')
        return self.url

    def profile_url(self, tab=None):
        '''User.profile_url(self, tab=None)'''
        if tab is not None:
            try:
                return url_for('profile.{}'.format(tab), id=self.id)
            except:
                return self.url
        return self.url

    @property
    def id_number_censored(self):
        '''User.id_number_censored(self)'''
        if self.id_number is not None:
            if len(self.id_number) > 1:
                return '{}{}{}'.format(self.id_number[:1], ''.join(['*' for x in self.id_number[1:-1]]), self.id_number[-1:])
            else:
                return ''.join(['*' for x in self.id_number])

    def to_csv(self):
        '''User.to_csv(self)'''
        last_seen_at = ''
        if self.last_seen_at is not None:
            last_seen_at = self.last_seen_at.strftime(current_app.config['DATETIME_FORMAT'])
        gender = ''
        if self.gender_id is not None:
            gender = self.gender.name
        entry_csv = [
            str(self.id),
            self.role.name,
            self.created_at.strftime(current_app.config['DATETIME_FORMAT']),
            last_seen_at,
            self.last_seen_ip,
            str(self.invalid_login_count),
            str(int(self.deleted)),
            self.name,
            self.id_type.name,
            self.id_number,
            gender,
        ]
        return entry_csv

    @staticmethod
    def insert_entries(data, basedir, verbose=False):
        '''User.insert_entries(data, basedir, verbose=False)'''
        if data == 'initial':
            system_operator = User(
                role_id=Role.query.filter_by(name='开发人员').first().id,
                id_type_id=IDType.query.filter_by(name='其它').first().id,
                id_number=current_app.config['SYSTEM_OPERATOR_TOKEN'],
                name='SysOp'
            )
            db.session.add(system_operator)
            db.session.commit()
            if verbose:
                print('初始化系统管理员信息')
        else:
            csv_file = os.path.join(basedir, 'data', data, 'users.csv')
            if os.path.exists(csv_file):
                print('---> Read: {}'.format(csv_file))
                with io.open(csv_file, 'rt', newline='') as f:
                    reader = CSVReader(f)
                    line_num = 0
                    for entry in reader:
                        if line_num >= 1:
                            if entry[3] is not None:
                                entry[3] = datetime.strptime(entry[3], current_app.config['DATETIME_FORMAT'])
                            if entry[10] is not None:
                                entry[10] = Gender.query.filter_by(name=entry[10]).first().id
                            user = User(
                                id=int(entry[0]),
                                role_id=Role.query.filter_by(name=entry[1]).first().id,
                                created_at=datetime.strptime(entry[2], current_app.config['DATETIME_FORMAT']),
                                last_seen_at=entry[3],
                                last_seen_ip=entry[4],
                                invalid_login_count=int(entry[5]),
                                deleted=bool(int(entry[6])),
                                name=entry[7],
                                id_type_id=entry[8],
                                id_number=entry[9],
                                gender_id=entry[10]
                            )
                            db.session.add(user)
                            if verbose:
                                print('导入用户信息', entry[1], entry[7])
                        line_num += 1
                    db.session.commit()
            else:
                print('文件不存在', csv_file)

    @staticmethod
    def backup_entries(data, basedir):
        '''User.backup_entries(data, basedir)'''
        csv_file = os.path.join(basedir, 'data', data, 'users.csv')
        if os.path.exists(csv_file):
            os.remove(csv_file)
        with io.open(csv_file, 'wt', newline='') as f:
            writer = CSVWriter(f)
            writer.writerow([
                'id',
                'role',
                'created_at',
                'last_seen_at',
                'last_seen_ip',
                'invalid_login_count',
                'deleted',
                'name',
                'id_type',
                'id_number',
                'gender',
            ])
            for entry in User.query.all():
                writer.writerow(entry.to_csv())
            print('---> Write: {}'.format(csv_file))

    def __repr__(self):
        return '<User {}>'.format(self.name)


db.event.listen(User.name, 'set', User.on_changed_name)


class AnonymousUser(AnonymousUserMixin):
    '''AnonymousUser(AnonymousUserMixin)'''

    def can(self, permission_name):
        '''AnonymousUser.can(self, permission_name)'''
        return False

    def plays(self, role_name):
        '''AnonymousUser.plays(self, role_name)'''
        return False

    @property
    def is_suspended(self):
        '''AnonymousUser.is_suspended(self)'''
        return False

    @property
    def is_student(self):
        '''AnonymousUser.is_student(self)'''
        return False

    @property
    def is_staff(self):
        '''AnonymousUser.is_staff(self)'''
        return False

    @property
    def is_moderator(self):
        '''AnonymousUser.is_moderator(self)'''
        return False

    @property
    def is_administrator(self):
        '''AnonymousUser.is_administrator(self)'''
        return False

    @property
    def is_developer(self):
        '''AnonymousUser.is_developer(self)'''
        return False

    def is_superior_than(self, user):
        '''AnonymousUser.is_superior_than(self, user)'''
        return False


login_manager.anonymous_user = AnonymousUser


@login_manager.user_loader
def load_user(user_id):
    '''load_user(user_id)'''
    return User.query.get(int(user_id))


class Room(db.Model):
    '''Table: rooms'''
    __tablename__ = 'rooms'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Unicode(64), unique=True, index=True)
    devices = db.relationship('Device', backref='room', lazy='dynamic')

    @staticmethod
    def insert_entries(data, basedir, verbose=False):
        '''Room.insert_entries(data, basedir, verbose=False)'''
        yaml_file = os.path.join(basedir, 'data', data, 'rooms.yml')
        entries = load_yaml(yaml_file=yaml_file)
        if entries is not None:
            print('---> Read: {}'.format(yaml_file))
            for entry in entries:
                room = Room(name=entry['name'])
                db.session.add(room)
                if verbose:
                    print('导入房间信息', entry['name'])
            db.session.commit()
        else:
            print('文件不存在', yaml_file)

    def __repr__(self):
        return '<Room {}>'.format(self.name)


class DeviceType(db.Model):
    '''Table: device_types'''
    __tablename__ = 'device_types'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Unicode(64), unique=True, index=True)
    devices = db.relationship('Device', backref='type', lazy='dynamic')

    @staticmethod
    def insert_entries(data, basedir, verbose=False):
        '''DeviceType.insert_entries(data, basedir, verbose=False)'''
        yaml_file = os.path.join(basedir, 'data', data, 'device_types.yml')
        entries = load_yaml(yaml_file=yaml_file)
        if entries is not None:
            print('---> Read: {}'.format(yaml_file))
            for entry in entries:
                device_type = DeviceType(name=entry['name'])
                db.session.add(device_type)
                if verbose:
                    print('导入设备类型信息', entry['name'])
            db.session.commit()
        else:
            print('文件不存在', yaml_file)

    def __repr__(self):
        return '<Device Type {}>'.format(self.name)


class Device(db.Model):
    '''Table: devices'''
    __tablename__ = 'devices'
    id = db.Column(db.Integer, primary_key=True)
    serial = db.Column(db.Unicode(64), unique=True, index=True)
    alias = db.Column(db.Unicode(64))
    type_id = db.Column(db.Integer, db.ForeignKey('device_types.id'))
    room_id = db.Column(db.Integer, db.ForeignKey('rooms.id'))
    ip_address = db.Column(db.Unicode(64))
    category = db.Column(db.Unicode(64), index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    modified_at = db.Column(db.DateTime, default=datetime.utcnow)
    modified_by_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    def ping(self, modified_by):
        '''Device.ping(self, modified_by)'''
        self.modified_at = datetime.utcnow()
        self.modified_by_id = modified_by.id
        db.session.add(self)

    @property
    def alias2(self):
        '''Device.alias2(self)'''
        return '{}（{}）'.format(self.alias, self.serial)

    def to_csv(self):
        '''Device.to_csv(self)'''
        room = ''
        if self.room_id is not None:
            room = self.room.name
        entry_csv = [
            str(self.id),
            self.serial,
            self.alias,
            self.type.name,
            room,
            self.ip_address,
            self.category,
            self.created_at.strftime(current_app.config['DATETIME_FORMAT']),
            self.modified_at.strftime(current_app.config['DATETIME_FORMAT']),
            str(self.modified_by_id),
        ]
        return entry_csv

    @staticmethod
    def insert_entries(data, basedir, verbose=False):
        '''Device.insert_entries(data, basedir, verbose=False)'''
        csv_file = os.path.join(basedir, 'data', data, 'devices.csv')
        if data == 'initial':
            development_machine = Device(
                serial=current_app.config['DEVELOPMENT_MACHINE_SERIAL'],
                alias='Development Machine',
                type_id=DeviceType.query.filter_by(name='Desktop').first().id,
                ip_address=current_app.config['DEVELOPMENT_MACHINE_IP_ADDRESS'],
                category='development',
                modified_by_id=User.query.get(1).id
            )
            db.session.add(development_machine)
            db.session.commit()
            if verbose:
                print('初始化开发人员设备信息')
        if os.path.exists(csv_file):
            print('---> Read: {}'.format(csv_file))
            with io.open(csv_file, 'rt', newline='') as f:
                reader = CSVReader(f)
                line_num = 0
                for entry in reader:
                    if line_num >= 1:
                        if data == 'initial':
                            device = Device(
                                serial=entry[1].upper(),
                                alias=entry[0],
                                type_id=DeviceType.query.filter_by(name=entry[2]).first().id,
                                room_id=Room.query.filter_by(name=entry[3]).first().id,
                                ip_address=entry[4],
                                category='production',
                                modified_by_id=User.query.get(1).id
                            )
                            db.session.add(device)
                            if verbose:
                                print('导入设备信息', entry[0], entry[1], entry[2], entry[3], entry[4])
                        else:
                            if entry[4] is not None:
                                entry[4] = Room.query.filter_by(name=entry[4]).first().id
                            device = Device(
                                id=int(entry[0]),
                                serial=entry[1],
                                alias=entry[2],
                                type_id=DeviceType.query.filter_by(name=entry[3]).first().id,
                                room_id=entry[4],
                                ip_address=entry[5],
                                category=entry[6],
                                created_at=datetime.strptime(entry[7], current_app.config['DATETIME_FORMAT']),
                                modified_at=datetime.strptime(entry[8], current_app.config['DATETIME_FORMAT']),
                                modified_by_id=int(entry[9])
                            )
                            db.session.add(device)
                            if verbose:
                                print('导入设备信息', entry[2], entry[1], entry[3], entry[4], entry[5], entry[6])
                    line_num += 1
                db.session.commit()
        else:
            print('文件不存在', csv_file)

    @staticmethod
    def backup_entries(data, basedir):
        '''Device.backup_entries(data, basedir)'''
        csv_file = os.path.join(basedir, 'data', data, 'devices.csv')
        if os.path.exists(csv_file):
            os.remove(csv_file)
        with io.open(csv_file, 'wt', newline='') as f:
            writer = CSVWriter(f)
            writer.writerow([
                'id',
                'serial',
                'alias',
                'type',
                'room',
                'ip_address',
                'category',
                'created_at',
                'modified_at',
                'modified_by_id',
            ])
            for entry in Device.query.all():
                writer.writerow(entry.to_csv())
            print('---> Write: {}'.format(csv_file))

    def __repr__(self):
        return '<Device {} {} {}>'.format(self.serial, self.alias, self.type.name)


class LessonType(db.Model):
    '''Table: lesson_types'''
    __tablename__ = 'lesson_types'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Unicode(64), unique=True, index=True)
    lessons = db.relationship('Lesson', backref='type', lazy='dynamic')

    @staticmethod
    def insert_entries(data, basedir, verbose=False):
        '''LessonType.insert_entries(data, basedir, verbose=False)'''
        yaml_file = os.path.join(basedir, 'data', data, 'lesson_types.yml')
        entries = load_yaml(yaml_file=yaml_file)
        if entries is not None:
            print('---> Read: {}'.format(yaml_file))
            for entry in entries:
                lesson_type = LessonType(name=entry['name'])
                db.session.add(lesson_type)
                if verbose:
                    print('导入课程类型信息', entry['name'])
            db.session.commit()
        else:
            print('文件不存在', yaml_file)

    def __repr__(self):
        return '<Lesson Type {}>'.format(self.name)


class Lesson(db.Model):
    '''Table: lessons'''
    __tablename__ = 'lessons'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Unicode(64), unique=True, index=True)
    abbr = db.Column(db.Unicode(64))
    type_id = db.Column(db.Integer, db.ForeignKey('lesson_types.id'))
    videos = db.relationship('Video', backref='lesson', lazy='dynamic')

    @staticmethod
    def insert_entries(data, basedir, verbose=False):
        '''Lesson.insert_entries(data, basedir, verbose=False)'''
        yaml_file = os.path.join(basedir, 'data', data, 'lessons.yml')
        entries = load_yaml(yaml_file=yaml_file)
        if entries is not None:
            print('---> Read: {}'.format(yaml_file))
            for entry in entries:
                lesson = Lesson(
                    name=entry['name'],
                    abbr=entry['abbr'],
                    type_id=LessonType.query.filter_by(name=entry['lesson_type_name']).first().id
                )
                db.session.add(lesson)
                if verbose:
                    print('导入课程信息', entry['name'])
            db.session.commit()
        else:
            print('文件不存在', yaml_file)

    def __repr__(self):
        return '<Lesson {}>'.format(self.name)


class Video(db.Model):
    '''Table: videos'''
    __tablename__ = 'videos'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Unicode(64), index=True)
    description = db.Column(db.Unicode(64))
    lesson_id = db.Column(db.Integer, db.ForeignKey('lessons.id'))
    duration = db.Column(db.Interval, default=timedelta(milliseconds=0))
    file_name = db.Column(db.Unicode(64))

    @staticmethod
    def insert_entries(data, basedir, verbose=False):
        '''Video.insert_entries(data, basedir, verbose=False)'''
        yaml_file = os.path.join(basedir, 'data', data, 'videos.yml')
        entries = load_yaml(yaml_file=yaml_file)
        if entries is not None:
            print('---> Read: {}'.format(yaml_file))
            for entry in entries:
                video_file = os.path.join(basedir, 'data', 'videos', entry['file_name'])
                if os.path.exists(video_file):
                    video = Video(
                        name=entry['name'],
                        description=entry['description'],
                        lesson_id=Lesson.query.filter_by(name=entry['lesson_name']).first().id,
                        duration=get_video_duration(video_file),
                        file_name=entry['file_name']
                    )
                    db.session.add(video)
                    if verbose:
                        print('导入视频信息', entry['name'], entry['file_name'])
                else:
                    if verbose:
                        print('视频文件不存在', entry['name'], entry['file_name'])
            db.session.commit()
        else:
            print('文件不存在', yaml_file)

    def __repr__(self):
        return '<Video {}>'.format(self.name)


class UserLog(db.Model):
    '''Table: user_logs'''
    __tablename__ = 'user_logs'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    event = db.Column(db.UnicodeText)
    category = db.Column(db.Unicode(64), index=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def to_csv(self):
        '''to_csv(self)'''
        entry_csv = [
            str(self.id),
            str(self.user_id),
            self.event,
            self.category,
            self.timestamp.strftime(current_app.config['DATETIME_FORMAT']),
        ]
        return entry_csv

    @staticmethod
    def insert_entries(data, basedir, verbose=False):
        '''UserLog.insert_entries(data, basedir, verbose=False)'''
        csv_file = os.path.join(basedir, 'data', data, 'user_logs.csv')
        if os.path.exists(csv_file):
            print('---> Read: {}'.format(csv_file))
            with io.open(csv_file, 'rt', newline='') as f:
                reader = CSVReader(f)
                line_num = 0
                for entry in reader:
                    if line_num >= 1:
                        user_log = UserLog(
                            id=int(entry[0]),
                            user_id=int(entry[1]),
                            event=entry[2],
                            category=entry[3],
                            timestamp=datetime.strptime(entry[4], current_app.config['DATETIME_FORMAT'])
                        )
                        db.session.add(user_log)
                        if verbose:
                            print('导入用户日志信息', entry[1], entry[2], entry[3], entry[4])
                    line_num += 1
                db.session.commit()
        else:
            print('文件不存在', csv_file)

    @staticmethod
    def backup_entries(data, basedir):
        '''UserLog.backup_entries(data, basedir)'''
        csv_file = os.path.join(basedir, 'data', data, 'user_logs.csv')
        if os.path.exists(csv_file):
            os.remove(csv_file)
        with io.open(csv_file, 'wt', newline='') as f:
            writer = CSVWriter(f)
            writer.writerow([
                'id',
                'user_id',
                'event',
                'category',
                'timestamp',
            ])
            for entry in UserLog.query.all():
                writer.writerow(entry.to_csv())
            print('---> Write: {}'.format(csv_file))

    def __repr__(self):
        return '<User Log {}, {}, {}, {}>'.format(self.user.name_alias, self.event, self.category, self.timestamp)
