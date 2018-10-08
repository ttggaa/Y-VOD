# -*- coding: utf-8 -*-

'''manage.py'''

import os
from flask_script import Manager, Shell
from flask_migrate import Migrate, MigrateCommand
from app import create_app, db


if os.path.exists('.env'):
    print('Importing environment from .env...')
    from dotenv import load_dotenv
    load_dotenv()


app = create_app(os.getenv('YVOD_CONFIG') or 'default')
manager = Manager(app)
migrate = Migrate(app, db)


def make_shell_context():
    '''Make shell context'''
    return dict(app=app, db=db)


manager.add_command('shell', Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)


@manager.command
def create():
    '''Run create tasks'''

    db.create_all()
    print('---> All tables are created.')


@manager.command
def cleanup():
    '''Run cleanup tasks'''

    if app.debug:
        remove_database_confirm = input('Would you like to remove all database files? [yes/No]: ')
        if remove_database_confirm.lower() in ['y', 'yes']:
            from config import basedir
            from shutil import rmtree
            db_files = [
                'ysys-dev.sqlite',
                'migrations',
            ]
            for db_file in db_files:
                full_db_file = os.path.join(basedir, db_file)
                if os.path.exists(full_db_file):
                    if os.path.isfile(full_db_file):
                        os.remove(full_db_file)
                    elif os.path.isdir(full_db_file):
                        rmtree(full_db_file)
                    print('---> Remove {}'.format(full_db_file))
    drop_table_confirm = input('Are you sure to drop all the tables? [yes/No]: ')
    if drop_table_confirm.lower() in ['y', 'yes']:
        db.drop_all()
        print('---> All tables are dropped.')


@manager.command
def deploy():
    '''Run deployment tasks'''

    # migrate database to latest revision
    from flask_migrate import upgrade
    upgrade()

    verbose = False
    if app.debug:
        verbose_mode = input('Run in verbose mode? [yes/No]: ')
        if verbose_mode.lower() in ['y', 'yes']:
            verbose = True

    # insert data
    from config import basedir
    data = 'common'

    from app.models import Permission
    Permission.insert_entries(data=data, basedir=basedir, verbose=verbose)

    from app.models import Role
    Role.insert_entries(data=data, basedir=basedir, verbose=verbose)

    from app.models import IDType
    IDType.insert_entries(data=data, basedir=basedir, verbose=verbose)

    from app.models import Gender
    Gender.insert_entries(data=data, basedir=basedir, verbose=verbose)

    from app.models import Room
    Room.insert_entries(data=data, basedir=basedir, verbose=verbose)

    from app.models import DeviceType
    DeviceType.insert_entries(data=data, basedir=basedir, verbose=verbose)

    from app.models import LessonType
    LessonType.insert_entries(data=data, basedir=basedir, verbose=verbose)

    from app.models import Lesson
    Lesson.insert_entries(data=data, basedir=basedir, verbose=verbose)

    from app.models import Video
    Video.insert_entries(data=data, basedir=basedir, verbose=verbose)

    data = input('Enter data identifier (e.g.: initial or 20180805): ')
    datadir = os.path.join(basedir, 'data', data)
    if os.path.exists(datadir):
        from app.models import User
        User.insert_entries(data=data, basedir=basedir, verbose=verbose)

        from app.models import Device
        Device.insert_entries(data=data, basedir=basedir, verbose=verbose)

        from app.models import UserLog
        UserLog.insert_entries(data=data, basedir=basedir, verbose=verbose)


@manager.command
def backup():
    '''Run backup tasks'''

    from config import basedir
    data = input('Enter data identifier (e.g.: backup or 20180805 or press the enter/return key): ')
    if data == '':
        from datetime import datetime
        data = datetime.now().strftime('%Y%m%d%H%M%S')
    datadir = os.path.join(basedir, 'data', data)
    if not os.path.exists(datadir):
        os.makedirs(datadir)

    from app.models import User
    User.backup_entries(data=data, basedir=basedir)

    from app.models import Device
    Device.backup_entries(data=data, basedir=basedir)

    from app.models import UserLog
    UserLog.backup_entries(data=data, basedir=basedir)


if __name__ == '__main__':
    manager.run()
