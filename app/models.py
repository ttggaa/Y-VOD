# -*- coding: utf-8 -*-

'''app/models.py'''

import os
import io
import operator
from shutil import copyfile
from datetime import datetime, timedelta
from secrets import token_urlsafe
from functools import reduce
from werkzeug.routing import BuildError
from flask import current_app, url_for
from flask_login import UserMixin, AnonymousUserMixin
from app import db, login_manager
from app.utils import makedirs
from app.utils import date_now, date_then
from app.utils import CSVReader, CSVWriter, load_yaml
from app.utils import get_video_duration, format_duration
from app.utils import to_pinyin


class RolePermission(db.Model):
    '''models.RolePermission(db.Model)'''
    __tablename__ = 'role_permissions'
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'), primary_key=True)
    permission_id = db.Column(db.Integer, db.ForeignKey('permissions.id'), primary_key=True)

    def __repr__(self):
        return '<Role Permission {} {}>'.format(self.role.name, self.permission.name)


class Permission(db.Model):
    '''models.Permission(db.Model)'''
    __tablename__ = 'permissions'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Unicode(64), unique=True, index=True)
    category = db.Column(db.Unicode(64), index=True)
    role_authorizations = db.relationship(
        'RolePermission',
        foreign_keys=[RolePermission.permission_id],
        backref=db.backref('permission', lazy='joined'),
        lazy='dynamic',
        cascade='all, delete-orphan'
    )

    def roles_from_category(self, category):
        '''Permission.roles_from_category(self, category)'''
        return Role.query\
            .join(RolePermission, RolePermission.role_id == Role.id)\
            .filter(RolePermission.permission_id == self.id)\
            .filter(Role.category == category)\
            .order_by(Role.id.asc())

    def role_quantity_from_category(self, category):
        '''Permission.role_quantity_from_category(self, category)'''
        return Role.query\
            .join(RolePermission, RolePermission.role_id == Role.id)\
            .filter(RolePermission.permission_id == self.id)\
            .filter(Role.category == category)\
            .count()

    @staticmethod
    def insert_entries(data, verbose=False):
        '''Permission.insert_entries(data, verbose=False)'''
        yaml_file = os.path.join(current_app.config['DATA_DIR'], data, 'permissions.yml')
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
    '''models.Role(db.Model)'''
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Unicode(64), unique=True, index=True)
    category = db.Column(db.Unicode(64), index=True)
    icon = db.Column(db.Unicode(64))
    level = db.Column(db.Integer, nullable=False)
    permission_authorizations = db.relationship(
        'RolePermission',
        foreign_keys=[RolePermission.role_id],
        backref=db.backref('role', lazy='joined'),
        lazy='dynamic',
        cascade='all, delete-orphan'
    )
    users = db.relationship('User', backref='role', lazy='dynamic')

    def has_permission(self, permission):
        '''Role.has_permission(self, permission)'''
        return self.permission_authorizations\
            .filter_by(permission_id=permission.id)\
            .first() is not None

    def permissions_from_category(self, category):
        '''Role.permissions_from_category(self, category)'''
        return Permission.query\
            .join(RolePermission, RolePermission.permission_id == Permission.id)\
            .filter(RolePermission.role_id == self.id)\
            .filter(Permission.category == category)\
            .order_by(Permission.id.asc())

    def permission_quantity_from_category(self, category):
        '''Role.permission_quantity_from_category(self, category)'''
        return Permission.query\
            .join(RolePermission, RolePermission.permission_id == Permission.id)\
            .filter(RolePermission.role_id == self.id)\
            .filter(Permission.category == category)\
            .count()

    def is_superior_than(self, role):
        '''Role.is_superior_than(self, role)'''
        return self.level > role.level

    def can_manage(self, role):
        '''Role.can_manage(self, role)'''
        if self.name == '开发人员' or \
            (self.name == '管理员' and not role.is_superior_than(role=self)) or \
            (self.name == '协管员' and self.is_superior_than(role=role)) or \
            (self.name == '协调员' and role.category == 'student'):
            return True
        return False

    @staticmethod
    def insert_entries(data, verbose=False):
        '''Role.insert_entries(data, verbose=False)'''
        yaml_file = os.path.join(current_app.config['DATA_DIR'], data, 'roles.yml')
        entries = load_yaml(yaml_file=yaml_file)
        if entries is not None:
            print('---> Read: {}'.format(yaml_file))
            for entry in entries:
                role = Role(
                    name=entry['name'],
                    category=entry['category'],
                    icon=entry['icon'],
                    level=entry['level']
                )
                db.session.add(role)
                db.session.commit()
                if verbose:
                    print('导入用户角色信息', entry['name'], entry['category'])
                for permission in entry['permissions']:
                    role_permission = RolePermission(
                        role_id=role.id,
                        permission_id=Permission.query.filter_by(name=permission).first().id
                    )
                    db.session.add(role_permission)
                    if verbose:
                        print('赋予权限', entry['name'], permission)
                db.session.commit()
        else:
            print('文件不存在', yaml_file)

    def __repr__(self):
        return '<Role {}>'.format(self.name)


class Punch(db.Model):
    '''Table: punches'''
    __tablename__ = 'punches'
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    video_id = db.Column(db.Integer, db.ForeignKey('videos.id'), primary_key=True)
    play_time = db.Column(db.Interval, default=timedelta())
    synchronized = db.Column(db.Boolean, default=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def set_synchronized(self):
        '''Punch.set_synchronized(self)'''
        if self.video.lesson.type.name == 'VB':
            self.synchronized = True
            self.timestamp = datetime.utcnow()
            db.session.add(self)
        elif self.video.lesson.type.name in ['Y-GRE', 'Y-GRE AW']:
            for video in Video.query\
                .filter(Video.lesson_id == self.video.lesson_id)\
                .all():
                self.user.punch(video=video, synchronized=True)

    @property
    def sync_required(self):
        '''Punch.sync_required(self)'''
        if self.video.lesson.type.name == 'VB':
            return not self.synchronized and self.user.complete_video(video=self.video)
        if self.video.lesson.type.name in ['Y-GRE', 'Y-GRE AW']:
            return not self.synchronized and self.user.complete_lesson(lesson=self.video.lesson)
        return False

    @property
    def complete(self):
        '''Punch.complete(self)'''
        return self.play_time >= self.video.duration

    @property
    def play_time_trim(self):
        '''Punch.play_time_trim(self)'''
        if self.complete:
            return self.video.duration
        return self.play_time

    @property
    def progress(self):
        '''Punch.progress(self)'''
        return self.play_time / self.video.duration

    @property
    def progress_trim(self):
        '''Punch.progress_trim(self)'''
        if self.complete:
            return 1.0
        return self.progress

    @property
    def progress_percentage(self):
        '''Punch.progress_percentage(self)'''
        return '{:.0%}'.format(self.progress_trim)

    def to_csv(self):
        '''Punch.to_csv(self)'''
        csv_entry = [
            str(self.user_id),
            str(self.video_id),
            str(self.play_time.total_seconds()),
            str(int(self.synchronized)),
            self.timestamp.strftime(current_app.config['DATETIME_FORMAT']),
        ]
        return csv_entry

    @staticmethod
    def insert_entries(data, verbose=False):
        '''Punch.insert_entries(data, verbose=False)'''
        csv_file = os.path.join(current_app.config['DATA_DIR'], data, 'punches.csv')
        if os.path.exists(csv_file):
            print('---> Read: {}'.format(csv_file))
            with io.open(csv_file, 'rt', newline='') as f:
                reader = CSVReader(f)
                line_num = 0
                for entry in reader:
                    if line_num >= 1:
                        punch = Punch(
                            user_id=int(entry[0]),
                            video_id=int(entry[1]),
                            play_time=timedelta(seconds=float(entry[2])),
                            synchronized=bool(int(entry[3])),
                            timestamp=datetime.strptime(
                                entry[4],
                                current_app.config['DATETIME_FORMAT']
                            )
                        )
                        db.session.add(punch)
                        if verbose:
                            print('导入用户视频播放信息', entry[0], entry[1], entry[2])
                    line_num += 1
                db.session.commit()
        else:
            print('文件不存在', csv_file)

    @staticmethod
    def backup_entries(data):
        '''Punch.backup_entries(data)'''
        csv_file = os.path.join(current_app.config['DATA_DIR'], data, 'punches.csv')
        if os.path.exists(csv_file):
            os.remove(csv_file)
        with io.open(csv_file, 'wt', newline='') as f:
            writer = CSVWriter(f)
            writer.writerow([
                'user_id',
                'video_id',
                'play_time',
                'synchronized',
                'timestamp',
            ])
            for entry in Punch.query.all():
                writer.writerow(entry.to_csv())
            print('---> Write: {}'.format(csv_file))

    def __repr__(self):
        return '<Punch {} {} {}>'.format(self.user.name, self.video.name, self.play_time)


class User(UserMixin, db.Model):
    '''models.User(UserMixin, db.Model)'''
    __tablename__ = 'users'
    # basic properties
    id = db.Column(db.Integer, primary_key=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    imported_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_seen_at = db.Column(db.DateTime)
    last_seen_mac = db.Column(db.Unicode(64))
    suspended = db.Column(db.Boolean, default=False)
    # profile properties
    name = db.Column(db.Unicode(64), index=True)
    name_pinyin = db.Column(db.Unicode(64), index=True)
    # study properties
    punches = db.relationship(
        'Punch',
        foreign_keys=[Punch.user_id],
        backref=db.backref('user', lazy='joined'),
        lazy='dynamic',
        cascade='all, delete-orphan'
    )
    # management properties
    modified_devices = db.relationship('Device', backref='modified_by', lazy='dynamic')
    # user logs
    user_logs = db.relationship('UserLog', backref='user', lazy='dynamic')

    def ping(self):
        '''User.ping(self)'''
        self.last_seen_at = datetime.utcnow()
        db.session.add(self)

    def update_mac(self, mac_address):
        '''User.update_mac(self, mac_address)'''
        self.last_seen_mac = mac_address
        db.session.add(self)

    @property
    def last_login_device(self):
        '''User.last_login_device(self)'''
        return Device.query.filter_by(mac_address=self.last_seen_mac).first()

    @property
    def last_login_device_with_mac(self):
        '''User.last_login_device_with_mac(self)'''
        if self.last_login_device is not None:
            device_info = self.last_login_device.alias
        else:
            device_info = '未授权设备'
        return '{} ({})'.format(device_info, self.last_seen_mac)

    def suspend(self):
        '''User.suspend(self)'''
        self.suspended = True
        db.session.add(self)

    def restore(self):
        '''User.restore(self)'''
        self.suspended = False
        db.session.add(self)

    def can(self, permission_name):
        '''User.can(self, permission_name)'''
        if self.suspended:
            return False
        permission = Permission.query.filter_by(name=permission_name).first()
        return permission is not None and \
            self.role_id is not None and \
            self.role.has_permission(permission=permission)

    def plays(self, role_name):
        '''User.plays(self, role_name)'''
        if self.suspended:
            return False
        role = Role.query.filter_by(name=role_name).first()
        return role is not None and \
            self.role_id is not None and \
            (self.role_id == role.id or self.role.is_superior_than(role=role))

    @property
    def is_student(self):
        '''User.is_student(self)'''
        return not self.suspended and self.role.category == 'student'

    @property
    def is_staff(self):
        '''User.is_staff(self)'''
        return not self.suspended and self.role.category == 'staff'

    @property
    def is_moderator(self):
        '''User.is_moderator(self)'''
        return not self.suspended and self.role.name == '协管员'

    @property
    def is_administrator(self):
        '''User.is_administrator(self)'''
        return not self.suspended and self.role.name == '管理员'

    @property
    def is_developer(self):
        '''User.is_developer(self)'''
        return not self.suspended and self.role.name == '开发人员'

    def is_superior_than(self, user):
        '''User.is_superior_than(self, user)'''
        return not self.suspended and self.role.is_superior_than(role=user.role)

    def can_manage(self, user):
        '''User.can_manage(self, user)'''
        return not self.suspended and self.role.can_manage(role=user.role)

    def can_access_profile(self, user):
        '''User.can_access_profile(self, user)'''
        return user.id == self.id or \
            (self.is_staff and not user.is_superior_than(user=self))

    @staticmethod
    def on_changed_name(target, value, oldvalue, initiator):
        '''User.on_changed_name(target, value, oldvalue, initiator)'''
        name_pinyin = '{} {}'.format(to_pinyin(value), to_pinyin(value, initials=True))
        if name_pinyin != ' ':
            target.name_pinyin = name_pinyin

    @property
    def name_with_role(self):
        '''User.name_with_role(self)'''
        return '[{}] {}'.format(self.role.name, self.name)

    @property
    def role_name(self):
        '''User.role_name(self)'''
        if self.suspended:
            return '[挂起] {}'.format(self.role.name)
        return self.role.name

    @property
    def url(self):
        '''User.url(self)'''
        return url_for('profile.overview', id=self.id)

    @property
    def index_url(self):
        '''User.index_url(self)'''
        if self.is_staff:
            return url_for('status.home')
        return self.url

    def profile_url(self, tab=None):
        '''User.profile_url(self, tab=None)'''
        if tab is not None:
            try:
                return url_for('profile.{}'.format(tab), id=self.id)
            except BuildError:
                return self.url
        return self.url

    def profile_json(self, url_tab=None):
        '''User.profile_json(self, url_tab=None)'''
        json_entry = {
            'title': self.name,
            'url': self.profile_url(tab=url_tab),
            'description': self.role_name,
        }
        return json_entry

    def punch(self, video, play_time=None, synchronized=None):
        '''User.punch(self, video, play_time=None, synchronized=None)'''
        punch = self.get_punch(video=video)
        if punch is not None:
            punch.timestamp = datetime.utcnow()
        else:
            punch = Punch(
                user_id=self.id,
                video_id=video.id
            )
        if play_time is not None:
            if isinstance(play_time, timedelta):
                punch.play_time = play_time
            else:
                punch.play_time = timedelta(seconds=play_time)
        if synchronized is not None:
            punch.synchronized = synchronized
        db.session.add(punch)

    def punched(self, video):
        '''User.punched(self, video)'''
        return self.get_punch(video=video) is not None

    def get_punch(self, video):
        '''User.get_punch(self, video)'''
        return self.punches.filter_by(video_id=video.id).first()

    def sync_punch(self, section):
        '''User.sync_punch(self, section)'''
        if isinstance(section, str):
            if section.startswith('VB'):
                vb_video = Video.query.filter_by(name=section).first()
                if vb_video is not None:
                    for video in Video.query\
                        .join(Lesson, Lesson.id == Video.lesson_id)\
                        .join(LessonType, LessonType.id == Lesson.type_id)\
                        .filter(LessonType.name == 'VB')\
                        .filter(Video.id <= vb_video.id)\
                        .all():
                        if not self.synced_punch(video=video):
                            self.punch(video=video, play_time=video.duration, synchronized=True)
            elif section.startswith('Y-GRE'):
                lesson = Lesson.query.filter_by(name=section).first()
                if lesson is not None:
                    for video in Video.query\
                        .join(Lesson, Lesson.id == Video.lesson_id)\
                        .join(LessonType, LessonType.id == Lesson.type_id)\
                        .filter(LessonType.name == 'Y-GRE')\
                        .filter(Lesson.id <= lesson.id)\
                        .all():
                        if not self.synced_punch(video=video):
                            self.punch(video=video, play_time=video.duration, synchronized=True)
        elif isinstance(section, bool) and section:
            for video in Video.query\
                .join(Lesson, Lesson.id == Video.lesson_id)\
                .join(LessonType, LessonType.id == Lesson.type_id)\
                .filter(LessonType.name == 'Y-GRE AW')\
                .all():
                if not self.synced_punch(video=video):
                    self.punch(video=video, play_time=video.duration, synchronized=True)

    def synced_punch(self, video):
        '''User.synced_punch(self, video)'''
        punch = self.get_punch(video=video)
        return punch is not None and \
            punch.synchronized and \
            punch.progress_trim >= video.lesson.progress_threshold

    @property
    def latest_punch(self):
        '''User.latest_punch(self)'''
        return self.punches.order_by(Punch.timestamp.desc()).first()

    @property
    def last_vb_punch(self):
        '''User.last_vb_punch(self)'''
        return Punch.query\
            .join(Video, Video.id == Punch.video_id)\
            .join(Lesson, Lesson.id == Video.lesson_id)\
            .join(LessonType, LessonType.id == Lesson.type_id)\
            .filter(LessonType.name == 'VB')\
            .filter(Punch.user_id == self.id)\
            .order_by(Video.id.desc())\
            .first()

    @property
    def last_y_gre_punch(self):
        '''User.last_y_gre_punch(self)'''
        return Punch.query\
            .join(Video, Video.id == Punch.video_id)\
            .join(Lesson, Lesson.id == Video.lesson_id)\
            .join(LessonType, LessonType.id == Lesson.type_id)\
            .filter(LessonType.name == 'Y-GRE')\
            .filter(Punch.user_id == self.id)\
            .order_by(Video.id.desc())\
            .first()

    def lesson_play_time(self, lesson):
        '''User.lesson_play_time(self, lesson)'''
        return reduce(operator.add, [punch.play_time_trim for punch in Punch.query\
            .join(Video, Video.id == Punch.video_id)\
            .filter(Video.lesson_id == lesson.id)\
            .filter(Punch.user_id == self.id)\
            .all()], timedelta())

    def lesson_progress(self, lesson):
        '''User.lesson_progress(self, lesson)'''
        return self.lesson_play_time(lesson=lesson) / lesson.duration

    def lesson_progress_percentage(self, lesson):
        '''User.lesson_progress_percentage(self, lesson)'''
        return '{:.0%}'.format(self.lesson_progress(lesson=lesson))

    def complete_lesson(self, lesson, progress_threshold=None):
        '''User.complete_lesson(self, lesson, progress_threshold=None)'''
        if progress_threshold is not None:
            return self.lesson_progress(lesson=lesson) >= progress_threshold
        return self.lesson_progress(lesson=lesson) >= lesson.progress_threshold

    def can_study(self, lesson):
        '''User.can_study(self, lesson)'''
        if lesson.type.name in ['VB', 'Y-GRE', 'Y-GRE AW']:
            return self.plays(role_name='协调员') or \
                reduce(operator.and_, [self.complete_lesson(lesson=lesson) \
                    for lesson in Lesson.query\
                    .join(LessonType, LessonType.id == Lesson.type_id)\
                    .filter(Lesson.type_id == lesson.type_id)\
                    .filter(Lesson.id < lesson.id)\
                    .all()], True)
        return True

    def video_play_time(self, video):
        '''User.video_play_time(self, video)'''
        punch = self.get_punch(video=video)
        if punch is not None:
            return punch.play_time
        return timedelta()

    def video_progress(self, video):
        '''User.video_progress(self, video)'''
        punch = self.get_punch(video=video)
        if punch is not None:
            return punch.progress_trim
        return 0.0

    def video_progress_percentage(self, video):
        '''User.video_progress_percentage(self, video)'''
        return '{:.0%}'.format(self.video_progress(video=video))

    def complete_video(self, video, progress_threshold=None):
        '''User.complete_video(self, video, progress_threshold=None)'''
        if progress_threshold is not None:
            return self.video_progress(video=video) >= progress_threshold
        return self.video_progress(video=video) >= video.lesson.progress_threshold

    def can_play(self, video):
        '''User.can_play(self, video)'''
        if video.lesson.type.name == 'VB':
            return self.plays(role_name='协调员') or \
                reduce(operator.and_, [self.complete_video(video=item) for item in Video.query\
                    .join(Lesson, Lesson.id == Video.lesson_id)\
                    .filter(Lesson.type_id == video.lesson.type_id)\
                    .filter(Video.id < video.id)\
                    .all()], True)
        if video.lesson.type.name in ['Y-GRE', 'Y-GRE AW']:
            return self.can_study(lesson=video.lesson)
        return True

    def to_csv(self):
        '''User.to_csv(self)'''
        csv_entry = [
            str(self.id),
            self.role.name,
            self.imported_at.strftime(current_app.config['DATETIME_FORMAT']),
            '' if self.last_seen_at is None \
                else self.last_seen_at.strftime(current_app.config['DATETIME_FORMAT']),
            self.last_seen_mac,
            str(int(self.suspended)),
            self.name,
        ]
        return csv_entry

    @staticmethod
    def insert_entries(data, verbose=False):
        '''User.insert_entries(data, verbose=False)'''
        if data == 'initial':
            system_operator = User(
                role_id=Role.query.filter_by(name='开发人员').first().id,
                name=current_app.config['SYSTEM_OPERATOR_NAME']
            )
            db.session.add(system_operator)
            db.session.commit()
            if verbose:
                print('初始化系统管理员信息')
        else:
            csv_file = os.path.join(current_app.config['DATA_DIR'], data, 'users.csv')
            if os.path.exists(csv_file):
                print('---> Read: {}'.format(csv_file))
                with io.open(csv_file, 'rt', newline='') as f:
                    reader = CSVReader(f)
                    line_num = 0
                    for entry in reader:
                        if line_num >= 1:
                            user = User(
                                id=int(entry[0]),
                                role_id=Role.query.filter_by(name=entry[1]).first().id,
                                imported_at=datetime.strptime(
                                    entry[2],
                                    current_app.config['DATETIME_FORMAT']
                                ),
                                last_seen_at=(None if entry[3] is None else datetime.strptime(
                                    entry[3],
                                    current_app.config['DATETIME_FORMAT']
                                )),
                                last_seen_mac=entry[4],
                                suspended=bool(int(entry[5])),
                                name=entry[6]
                            )
                            db.session.add(user)
                            if verbose:
                                print('导入用户信息', entry[1], entry[6])
                        line_num += 1
                    db.session.commit()
            else:
                print('文件不存在', csv_file)

    @staticmethod
    def backup_entries(data):
        '''User.backup_entries(data)'''
        csv_file = os.path.join(current_app.config['DATA_DIR'], data, 'users.csv')
        if os.path.exists(csv_file):
            os.remove(csv_file)
        with io.open(csv_file, 'wt', newline='') as f:
            writer = CSVWriter(f)
            writer.writerow([
                'id',
                'role',
                'imported_at',
                'last_seen_at',
                'last_seen_mac',
                'suspended',
                'name',
            ])
            for entry in User.query.all():
                writer.writerow(entry.to_csv())
            print('---> Write: {}'.format(csv_file))

    def __repr__(self):
        return '<User {}>'.format(self.name_with_role)


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

    def can_manage(self, user):
        '''AnonymousUser.can_manage(self, user)'''
        return False


login_manager.anonymous_user = AnonymousUser


@login_manager.user_loader
def load_user(user_id):
    '''models.load_user(user_id)'''
    return User.query.get(int(user_id))


class DeviceLessonType(db.Model):
    '''models.DeviceLessonType(db.Model)'''
    __tablename__ = 'device_lesson_types'
    device_id = db.Column(db.Integer, db.ForeignKey('devices.id'), primary_key=True)
    lesson_type_id = db.Column(db.Integer, db.ForeignKey('lesson_types.id'), primary_key=True)

    def to_csv(self):
        '''DeviceLessonType.to_csv(self)'''
        csv_entry = [
            str(self.device_id),
            self.lesson_type.name,
        ]
        return csv_entry

    @staticmethod
    def insert_entries(data, verbose=False):
        '''DeviceLessonType.insert_entries(data, verbose=False)'''
        csv_file = os.path.join(current_app.config['DATA_DIR'], data, 'device_lesson_types.csv')
        if os.path.exists(csv_file):
            print('---> Read: {}'.format(csv_file))
            with io.open(csv_file, 'rt', newline='') as f:
                reader = CSVReader(f)
                line_num = 0
                for entry in reader:
                    if line_num >= 1:
                        device_lesson_type = DeviceLessonType(
                            device_id=int(entry[0]),
                            lesson_type_id=LessonType.query.filter_by(name=entry[1]).first().id
                        )
                        db.session.add(device_lesson_type)
                        if verbose:
                            print('导入设备课程类型授权信息', entry[0], entry[1])
                    line_num += 1
                db.session.commit()
        else:
            print('文件不存在', csv_file)

    @staticmethod
    def backup_entries(data):
        '''DeviceLessonType.backup_entries(data)'''
        csv_file = os.path.join(current_app.config['DATA_DIR'], data, 'device_lesson_types.csv')
        if os.path.exists(csv_file):
            os.remove(csv_file)
        with io.open(csv_file, 'wt', newline='') as f:
            writer = CSVWriter(f)
            writer.writerow([
                'device_id',
                'lesson_type',
            ])
            for entry in DeviceLessonType.query.all():
                writer.writerow(entry.to_csv())
            print('---> Write: {}'.format(csv_file))

    def __repr__(self):
        return '<Device Lesson Type {} {}>'.format(self.device.alias_serial, self.lesson_type.name)


class Room(db.Model):
    '''models.Room(db.Model)'''
    __tablename__ = 'rooms'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Unicode(64), unique=True, index=True)
    devices = db.relationship('Device', backref='room', lazy='dynamic')

    @staticmethod
    def insert_entries(data, verbose=False):
        '''Room.insert_entries(data, verbose=False)'''
        yaml_file = os.path.join(current_app.config['DATA_DIR'], data, 'rooms.yml')
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
    '''models.DeviceType(db.Model)'''
    __tablename__ = 'device_types'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Unicode(64), unique=True, index=True)
    icon = db.Column(db.Unicode(64))
    devices = db.relationship('Device', backref='type', lazy='dynamic')

    @staticmethod
    def insert_entries(data, verbose=False):
        '''DeviceType.insert_entries(data, verbose=False)'''
        yaml_file = os.path.join(current_app.config['DATA_DIR'], data, 'device_types.yml')
        entries = load_yaml(yaml_file=yaml_file)
        if entries is not None:
            print('---> Read: {}'.format(yaml_file))
            for entry in entries:
                device_type = DeviceType(
                    name=entry['name'],
                    icon=entry['icon']
                )
                db.session.add(device_type)
                if verbose:
                    print('导入设备类型信息', entry['name'], entry['icon'])
            db.session.commit()
        else:
            print('文件不存在', yaml_file)

    def __repr__(self):
        return '<Device Type {}>'.format(self.name)


class Device(db.Model):
    '''models.Device(db.Model)'''
    __tablename__ = 'devices'
    id = db.Column(db.Integer, primary_key=True)
    serial = db.Column(db.Unicode(64), unique=True, index=True)
    alias = db.Column(db.Unicode(64))
    type_id = db.Column(db.Integer, db.ForeignKey('device_types.id'))
    room_id = db.Column(db.Integer, db.ForeignKey('rooms.id'))
    mac_address = db.Column(db.Unicode(64))
    category = db.Column(db.Unicode(64), default='production', index=True)
    obsolete = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    modified_at = db.Column(db.DateTime, default=datetime.utcnow)
    modified_by_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    lesson_type_authorizations = db.relationship(
        'DeviceLessonType',
        foreign_keys=[DeviceLessonType.device_id],
        backref=db.backref('device', lazy='joined'),
        lazy='dynamic',
        cascade='all, delete-orphan'
    )

    def ping(self, modified_by):
        '''Device.ping(self, modified_by)'''
        self.modified_at = datetime.utcnow()
        self.modified_by_id = modified_by.id
        db.session.add(self)

    def toggle_obsolete(self, modified_by):
        '''Device.toggle_obsolete(self, modified_by)'''
        self.obsolete = not self.obsolete
        self.ping(modified_by=modified_by)
        db.session.add(self)

    @property
    def alias_serial(self):
        '''Device.alias_serial(self)'''
        return '{} [{}]'.format(self.alias, self.serial)

    def add_lesson_type(self, lesson_type):
        '''Device.add_lesson_type(self, lesson_type)'''
        if not self.has_lesson_type(lesson_type=lesson_type):
            device_lesson_type = DeviceLessonType(device_id=self.id, lesson_type_id=lesson_type.id)
            db.session.add(device_lesson_type)

    def has_lesson_type(self, lesson_type):
        '''Device.has_lesson_type(self, lesson_type)'''
        return self.lesson_type_authorizations\
            .filter_by(lesson_type_id=lesson_type.id)\
            .first() is not None

    def can_access_lesson_type(self, lesson_type):
        '''Device.can_access_lesson_type(self, lesson_type)'''
        if isinstance(lesson_type, str):
            lesson_type = LessonType.query.filter_by(name=lesson_type).first()
        return lesson_type is not None and self.lesson_type_authorizations\
            .filter_by(lesson_type_id=lesson_type.id)\
            .first() is not None

    def remove_all_lesson_types(self):
        '''Device.remove_all_lesson_types(self)'''
        for item in self.lesson_type_authorizations:
            db.session.delete(item)

    def to_csv(self):
        '''Device.to_csv(self)'''
        csv_entry = [
            str(self.id),
            self.serial,
            self.alias,
            self.type.name,
            '' if self.room_id is None else self.room.name,
            self.mac_address,
            self.category,
            str(int(self.obsolete)),
            self.created_at.strftime(current_app.config['DATETIME_FORMAT']),
            self.modified_at.strftime(current_app.config['DATETIME_FORMAT']),
            str(self.modified_by_id),
        ]
        return csv_entry

    @staticmethod
    def insert_entries(data, verbose=False):
        '''Device.insert_entries(data, verbose=False)'''
        csv_file = os.path.join(current_app.config['DATA_DIR'], data, 'devices.csv')
        if data == 'initial':
            server = Device(
                serial=current_app.config['SERVER_SERIAL'],
                alias='Y-VOD Server',
                type_id=DeviceType.query.filter_by(name='Server').first().id,
                mac_address=current_app.config['SERVER_MAC_ADDRESS'],
                category='development',
                modified_by_id=User.query.get(1).id
            )
            db.session.add(server)
            db.session.commit()
            if verbose:
                print('初始化服务器设备信息')
            for lesson_type in LessonType.query.all():
                server.add_lesson_type(lesson_type=lesson_type)
                if verbose:
                    print('授权课程类型', lesson_type.name)
            db.session.commit()
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
                                room_id=None if entry[3] is None \
                                    else Room.query.filter_by(name=entry[3]).first().id,
                                mac_address=entry[4],
                                category=entry[5],
                                modified_by_id=User.query.get(1).id
                            )
                            db.session.add(device)
                            if verbose:
                                print('导入设备信息', entry[0], entry[1], entry[2], entry[4], entry[5])
                        else:
                            device = Device(
                                id=int(entry[0]),
                                serial=entry[1],
                                alias=entry[2],
                                type_id=DeviceType.query.filter_by(name=entry[3]).first().id,
                                room_id=None if entry[4] is None \
                                    else Room.query.filter_by(name=entry[4]).first().id,
                                mac_address=entry[5],
                                category=entry[6],
                                obsolete=bool(int(entry[7])),
                                created_at=datetime.strptime(
                                    entry[8],
                                    current_app.config['DATETIME_FORMAT']
                                ),
                                modified_at=datetime.strptime(
                                    entry[9],
                                    current_app.config['DATETIME_FORMAT']
                                ),
                                modified_by_id=int(entry[10])
                            )
                            db.session.add(device)
                            if verbose:
                                print('导入设备信息', entry[2], entry[1], entry[3], entry[5], entry[6])
                    line_num += 1
                db.session.commit()
        else:
            print('文件不存在', csv_file)

    @staticmethod
    def backup_entries(data):
        '''Device.backup_entries(data)'''
        csv_file = os.path.join(current_app.config['DATA_DIR'], data, 'devices.csv')
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
                'mac_address',
                'category',
                'obsolete',
                'created_at',
                'modified_at',
                'modified_by_id',
            ])
            for entry in Device.query.all():
                writer.writerow(entry.to_csv())
            print('---> Write: {}'.format(csv_file))

    def __repr__(self):
        return '<Device {} {}>'.format(self.alias_serial, self.type.name)


class LessonType(db.Model):
    '''models.LessonType(db.Model)'''
    __tablename__ = 'lesson_types'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Unicode(64), unique=True, index=True)
    color = db.Column(db.Unicode(64))
    view_point = db.Column(db.Unicode(64))
    login_required = db.Column(db.Boolean, default=True)
    lessons = db.relationship('Lesson', backref='type', lazy='dynamic')
    device_authorizations = db.relationship(
        'DeviceLessonType',
        foreign_keys=[DeviceLessonType.lesson_type_id],
        backref=db.backref('lesson_type', lazy='joined'),
        lazy='dynamic',
        cascade='all, delete-orphan'
    )

    @staticmethod
    def insert_entries(data, verbose=False):
        '''LessonType.insert_entries(data, verbose=False)'''
        yaml_file = os.path.join(current_app.config['DATA_DIR'], data, 'lesson_types.yml')
        entries = load_yaml(yaml_file=yaml_file)
        if entries is not None:
            print('---> Read: {}'.format(yaml_file))
            for entry in entries:
                lesson_type = LessonType(
                    name=entry['name'],
                    color=entry['color'],
                    view_point=entry['view_point'],
                    login_required=entry['login_required']
                )
                db.session.add(lesson_type)
                if verbose:
                    print('导入课程类型信息', entry['name'], entry['color'], entry['view_point'])
            db.session.commit()
        else:
            print('文件不存在', yaml_file)

    def __repr__(self):
        return '<Lesson Type {}>'.format(self.name)


class Lesson(db.Model):
    '''models.Lesson(db.Model)'''
    __tablename__ = 'lessons'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Unicode(64), unique=True, index=True)
    abbr = db.Column(db.Unicode(64))
    type_id = db.Column(db.Integer, db.ForeignKey('lesson_types.id'))
    progress_threshold = db.Column(db.Float, default=0.0)
    videos = db.relationship('Video', backref='lesson', lazy='dynamic')

    @property
    def duration(self):
        '''Lesson.duration(self)'''
        return reduce(operator.add, [video.duration for video in self.videos], timedelta())

    @property
    def duration_format(self):
        '''Lesson.duration_format(self)'''
        return format_duration(duration=self.duration)

    @staticmethod
    def insert_entries(data, verbose=False):
        '''Lesson.insert_entries(data, verbose=False)'''
        yaml_file = os.path.join(current_app.config['DATA_DIR'], data, 'lessons.yml')
        entries = load_yaml(yaml_file=yaml_file)
        if entries is not None:
            print('---> Read: {}'.format(yaml_file))
            for entry in entries:
                lesson = Lesson(
                    name='{} {}'.format(entry['lesson_type_name'], entry['abbr']),
                    abbr=entry['abbr'],
                    type_id=LessonType.query.filter_by(name=entry['lesson_type_name']).first().id,
                    progress_threshold=entry['progress_threshold']
                )
                db.session.add(lesson)
                if verbose:
                    print('导入课程信息', entry['lesson_type_name'], entry['abbr'])
            db.session.commit()
        else:
            print('文件不存在', yaml_file)

    def __repr__(self):
        return '<Lesson {}>'.format(self.name)


class Video(db.Model):
    '''models.Video(db.Model)'''
    __tablename__ = 'videos'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Unicode(64), index=True)
    abbr = db.Column(db.Unicode(64))
    description = db.Column(db.Unicode(64))
    lesson_id = db.Column(db.Integer, db.ForeignKey('lessons.id'))
    duration = db.Column(db.Interval, default=timedelta())
    file_name = db.Column(db.Unicode(64))
    hls_cache_file_name = db.Column(db.Unicode(64))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    punches = db.relationship(
        'Punch',
        foreign_keys=[Punch.video_id],
        backref=db.backref('video', lazy='joined'),
        lazy='dynamic',
        cascade='all, delete-orphan'
    )

    @property
    def section(self):
        '''Video.section(self)'''
        if self.lesson.type.name == 'VB':
            return self.name
        if self.lesson.type.name in ['Y-GRE', 'Y-GRE AW']:
            return '{} 视频研修'.format(self.lesson.name)
        return None

    @property
    def duration_format(self):
        '''Video.duration_format(self)'''
        return format_duration(duration=self.duration)

    @property
    def hls_url(self):
        '''Video.hls_url(self)'''
        if self.hls_cache_invalid:
            self.refresh_hls_cache()
            db.session.commit()
        return '/hls/{}/index.m3u8'.format(self.hls_cache_file_name)

    @property
    def hls_cache_invalid(self):
        '''Video.hls_cache_invalid(self)'''
        return not os.path.exists(os.path.join(current_app.config['HLS_DIR'], self.hls_cache_file_name)) or \
            date_then(timestamp=self.timestamp, utc_offset=current_app.config['UTC_OFFSET']) != \
            date_now(utc_offset=current_app.config['UTC_OFFSET'])

    def refresh_hls_cache(self):
        '''Video.refresh_hls_cache(self)'''
        makedirs(path=current_app.config['HLS_DIR'])
        hls_cache_file = os.path.join(current_app.config['HLS_DIR'], self.hls_cache_file_name)
        new_hls_cache_file_name = '{}.mp4'.format(token_urlsafe(16))
        new_hls_cache_file = os.path.join(current_app.config['HLS_DIR'], new_hls_cache_file_name)
        if os.path.exists(hls_cache_file):
            os.rename(hls_cache_file, new_hls_cache_file)
        else:
            copyfile(os.path.join(current_app.config['VIDEO_DIR'], self.file_name), new_hls_cache_file)
        self.hls_cache_file_name = new_hls_cache_file_name
        self.timestamp = datetime.utcnow()
        db.session.add(self)

    @staticmethod
    def insert_entries(data, verbose=False):
        '''Video.insert_entries(data, verbose=False)'''
        yaml_file = os.path.join(current_app.config['DATA_DIR'], data, 'videos.yml')
        entries = load_yaml(yaml_file=yaml_file)
        if entries is not None:
            print('---> Read: {}'.format(yaml_file))
            makedirs(path=current_app.config['HLS_DIR'], overwrite=True)
            for entry in entries:
                video_file = os.path.join(current_app.config['VIDEO_DIR'], entry['file_name'])
                if os.path.exists(video_file):
                    hls_cache_file_name = '{}.mp4'.format(token_urlsafe(16))
                    copyfile(video_file, os.path.join(current_app.config['HLS_DIR'], hls_cache_file_name))
                    video = Video(
                        name='{} {}'.format(entry['lesson_name'], entry['abbr']),
                        abbr=entry['abbr'],
                        description=entry['description'],
                        lesson_id=Lesson.query.filter_by(name=entry['lesson_name']).first().id,
                        duration=get_video_duration(video_file),
                        file_name=entry['file_name'],
                        hls_cache_file_name=hls_cache_file_name
                    )
                    db.session.add(video)
                    if verbose:
                        print('导入视频信息', entry['lesson_name'], entry['abbr'], entry['file_name'])
                else:
                    print('视频文件不存在', entry['lesson_name'], entry['abbr'], entry['file_name'])
            db.session.commit()
        else:
            print('文件不存在', yaml_file)

    def __repr__(self):
        return '<Video {}>'.format(self.name)


class UserLog(db.Model):
    '''models.UserLog(db.Model)'''
    __tablename__ = 'user_logs'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    event = db.Column(db.UnicodeText)
    category = db.Column(db.Unicode(64), index=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def to_csv(self):
        '''UserLog.to_csv(self)'''
        csv_entry = [
            str(self.id),
            str(self.user_id),
            self.event,
            self.category,
            self.timestamp.strftime(current_app.config['DATETIME_FORMAT']),
        ]
        return csv_entry

    @staticmethod
    def insert_entries(data, verbose=False):
        '''UserLog.insert_entries(data, verbose=False)'''
        csv_file = os.path.join(current_app.config['DATA_DIR'], data, 'user_logs.csv')
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
                            timestamp=datetime.strptime(
                                entry[4],
                                current_app.config['DATETIME_FORMAT']
                            )
                        )
                        db.session.add(user_log)
                        if verbose:
                            print('导入用户日志信息', entry[1], entry[2], entry[3], entry[4])
                    line_num += 1
                db.session.commit()
        else:
            print('文件不存在', csv_file)

    @staticmethod
    def backup_entries(data):
        '''UserLog.backup_entries(data)'''
        csv_file = os.path.join(current_app.config['DATA_DIR'], data, 'user_logs.csv')
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
        return '<User Log {} {} {} {}>'.format(
            self.user.name_with_role,
            self.event,
            self.category,
            self.timestamp
        )
