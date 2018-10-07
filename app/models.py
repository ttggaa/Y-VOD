# -*- coding: utf-8 -*-

'''app/models.py'''

import os
import io
from datetime import datetime
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

    @staticmethod
    def on_changed_name(target, value, oldvalue, initiator):
        '''User.on_changed_name(target, value, oldvalue, initiator)'''
        name_pinyin = '{} {}'.format(to_pinyin(value), to_pinyin(value, initials=True))
        if name_pinyin != ' ':
            target.name_pinyin = name_pinyin

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
    client_devices = db.relationship('ClientDevice', backref='room', lazy='dynamic')

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


class ClientDevice(db.Model):
    '''Table: client_devices'''
    __tablename__ = 'client_devices'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Unicode(64), unique=True, index=True)

    def __repr__(self):
        return '<Client Device {}>'.format(self.name)


class LessonType(db.Model):
    '''Table: lesson_types'''
    __tablename__ = 'lesson_types'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Unicode(64), unique=True, index=True)
    lessons = db.relationship('Lesson', backref='type', lazy='dynamic')

    @staticmethod
    def insert_entries(data, basedir, verbose=False):
        '''LessonType.insert_entries(data, basedir, verbose=False)'''
        datafile = os.path.join(basedir, 'data', data, 'lesson_types.yml')
        entries = load_yaml(datafile=datafile)
        if entries is not None:
            print('---> Read: {}'.format(datafile))
            for entry in entries:
                lesson_type = LessonType(name=entry['name'])
                db.session.add(lesson_type)
                if verbose:
                    print('导入课程类型信息', entry['name'])
            db.session.commit()
        else:
            print('文件不存在', datafile)

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
        datafile = os.path.join(basedir, 'data', data, 'lessons.yml')
        entries = load_yaml(datafile=datafile)
        if entries is not None:
            print('---> Read: {}'.format(datafile))
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
            print('文件不存在', datafile)

    def __repr__(self):
        return '<Lesson {}>'.format(self.name)


class Video(db.Model):
    '''Table: videos'''
    __tablename__ = 'videos'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Unicode(64), unique=True, index=True)
    description = db.Column(db.Unicode(64))
    lesson_id = db.Column(db.Integer, db.ForeignKey('lessons.id'))
    duration = db.Column(db.Interval, default=timedelta(milliseconds=0))
    file_name = db.Column(db.Unicode(64))

    @staticmethod
    def insert_entries(data, basedir, verbose=False):
        '''Video.insert_entries(data, basedir, verbose=False)'''
        datafile = os.path.join(basedir, 'data', data, 'videos.yml')
        entries = load_yaml(datafile=datafile)
        if entries is not None:
            print('---> Read: {}'.format(datafile))
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
            print('文件不存在', datafile)

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
            self.timestamp.strftime('%Y-%m-%dT%H:%M:%S'),
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
                            timestamp=datetime.strptime(entry[4], '%Y-%m-%dT%H:%M:%S')
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
