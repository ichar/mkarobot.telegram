# -*- coding: utf-8 -*-

import os
import sys
import re
from math import ceil
from datetime import datetime
from time import time
from collections import namedtuple
from operator import itemgetter
from copy import deepcopy

from flask import current_app, request, url_for
from flask_login import UserMixin, AnonymousUserMixin, current_user
from flask_babel import lazy_gettext
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer

from . import app_release, db, login_manager

from sqlalchemy import create_engine, MetaData
from sqlalchemy import func, asc, desc, and_, or_

from config import (
     IsDebug, IsDeepDebug, IsTrace, IsPrintExceptions, IsNoEmail, errorlog, 
     default_unicode, default_encoding, default_print_encoding, 
     print_to, print_exception, isIterable, 
     UTC_FULL_TIMESTAMP, LOCAL_EASY_DATESTAMP
     )

from .settings import DEFAULT_PER_PAGE, DEFAULT_HTML_SPLITTER, gettext, g
#from .mails import send_simple_mail
from .utils import getDate, getDateOnly, getToday, out, cid, cdate, clean, image_base64, make_config

roles_ids = ['USER', 'ADMIN', 'EDITOR', 'OPERATOR', 'VISITOR', 'X1', 'X2', 'X3', 'SERVICE', 'ROOT']
roles_names = tuple([lazy_gettext(x) for x in roles_ids])
ROLES = namedtuple('ROLES', ' '.join(roles_ids))
valid_user_roles = [n for n, x in enumerate(roles_ids)]
roles = ROLES._make(zip(valid_user_roles, roles_names))

answers_ids = ['TEXT', 'INLINE', 'INLINE_ROWS', 'MULTILINE', 'X1', 'X2', 'X3']
answers_names = tuple([lazy_gettext(x) for x in answers_ids])
ANSWERS = namedtuple('ANSWERS', ' '.join(answers_ids))
valid_question_answers = [n for n, x in enumerate(answers_ids)]
answers = ANSWERS._make(zip(valid_question_answers, answers_names))


def _commit(check_session=True):
    if check_session:
        if not (db.session.new or db.session.dirty or db.session.deleted):
            if IsDebug:
                print('>>> No data to commit: new[%s], dirty[%s], deleted[%s]' % ( \
                    len(db.session.new),
                    len(db.session.dirty),
                    len(db.session.deleted))
                )
            return
    try:
        db.session.commit()
        if IsDebug:
            print('>>> OK')
    except Exception as error:
        db.session.rollback()
        if IsDebug:
            print('>>> Commit Error: %s' % error)
        print_to(errorlog, '!!! System Commit Error: %s' % str(error))
        if IsPrintExceptions:
            print_exception()

##  ------------
##  Help Classes
##  ------------

class Pagination(object):
    #
    # Simple Pagination
    #
    def __init__(self, page, per_page, total, value, sql):
        self.page = page
        self.per_page = per_page
        self.total = total
        self.value = value
        self.sql = sql

    @property
    def query(self):
        return self.sql

    @property
    def items(self):
        return self.value

    @property
    def current_page(self):
        return self.page

    @property
    def pages(self):
        return int(ceil(self.total / float(self.per_page)))

    @property
    def has_prev(self):
        return self.page > 1

    @property
    def has_next(self):
        return self.page < self.pages

    def get_page_params(self):
        return (self.current_page, self.pages, self.per_page, self.has_prev, self.has_next, self.total,)

    def iter_pages(self, left_edge=1, left_current=0, right_current=3, right_edge=1):
        last = 0
        out = []
        for num in range(1, self.pages + 1):
            if num <= left_edge or (
                num > self.page - left_current - 1 and num < self.page + right_current) or \
                num > self.pages - right_edge:
                if last + 1 != num:
                    out.append(-1)
                out.append(num)
                last = num
        return out

##  ==========================
##  Objects Class Construction
##  ==========================

class ExtClassMethods(object):
    """
        Abstract class methods
    """
    @classmethod
    def all(cls):
        return cls.query.all()

    @classmethod
    def count(cls):
        return cls.query.count()

    @classmethod
    def get_by_id(cls, id):
        return cls.query.filter_by(id=id).first()

    @classmethod
    def print_all(cls):
        for x in cls.all():
            print(x)


class Dialog(db.Model, ExtClassMethods):
    """
        Bot Dialog instances
    """
    __tablename__ = 'dialogs'

    id = db.Column(db.Integer, primary_key=True)

    code = db.Column(db.String(20), index=True)
    name = db.Column(db.Unicode(250), default='')

    def __init__(self, code, name):
        self.code = code
        self.name = name

    def __repr__(self):
        return '<Dialog %s:[%s-%s]>' % (cid(self), str(self.code), self.name)

    @classmethod
    def get_by_code(cls, code):
        return cls.query.filter_by(code=code).first()


class Question(db.Model, ExtClassMethods):
    """
        Bot Dialog Question instances
    """
    __tablename__ = 'questions'

    id = db.Column(db.Integer, primary_key=True)
    dialog_id = db.Column(db.Integer, db.ForeignKey('dialogs.id'))

    number = db.Column(db.Integer, nullable=True)
    code = db.Column(db.String(20), index=True)
    answer_type = db.Column(db.SmallInteger, default=answers.INLINE[0])

    text_ru = db.Column(db.Unicode(250), default='')
    text_ua = db.Column(db.Unicode(250), default='')
    text_en = db.Column(db.Unicode(250), default='')

    dialog = db.relationship('Dialog', backref=db.backref('questions', lazy='joined'), uselist=True)

    def __init__(self, dialog):
        self.dialog_id = dialog.id

    def __repr__(self):
        return '<Questions %s: %s # %s answer_type:%s code:%s>' % (
            cid(self), 
            str(self.dialog_id), 
            str(self.number), 
            str(self.answer_type), 
            str(self.code), 
            )


class Answer(db.Model, ExtClassMethods):
    """
        Bot Dialog Answer instances
    """
    __tablename__ = 'answers'

    id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id'))

    number = db.Column(db.Integer, nullable=True)
    code = db.Column(db.String(20), index=True)

    text_ru = db.Column(db.Unicode(50), default='')
    text_ua = db.Column(db.Unicode(50), default='')
    text_en = db.Column(db.Unicode(50), default='')

    question = db.relationship('Question', backref=db.backref('answers', lazy='joined'), uselist=True)

    def __init__(self, dialog):
        self.dialog_id = dialog.id

    def __repr__(self):
        return '<Answers %s: %s # %s code:%s>' % (
            cid(self), 
            str(self.question_id), 
            str(self.number), 
            str(self.code), 
            )


class User(UserMixin, db.Model, ExtClassMethods):
    """
        Пользователи
    """
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    reg_date = db.Column(db.DateTime, index=True)

    login = db.Column(db.Unicode(20), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    nick = db.Column(db.Unicode(40), default='')
    first_name = db.Column(db.Unicode(50), default='')
    family_name = db.Column(db.Unicode(50), default='')
    last_name = db.Column(db.Unicode(50), default='')
    role = db.Column(db.SmallInteger, default=roles.USER[0])
    email = db.Column(db.String(120), index=True)

    last_seen = db.Column(db.DateTime(), default=datetime.utcnow)
    last_visit = db.Column(db.DateTime)
    last_pwd_changed = db.Column(db.DateTime)

    confirmed = db.Column(db.Boolean, default=False)
    enabled = db.Column(db.Boolean(), default=True)

    post = db.Column(db.String(100), default='')

    def __init__(self, login, name=None, role=None, email=None, **kw):
        super(User, self).__init__(**kw)
        self.login = login
        self.set_name(name, **kw)
        self.role = role in valid_user_roles and role or roles.USER[0]
        self.post = kw.get('post') or ''
        self.email = not email and '' or email
        self.reg_date = datetime.now()

    def __repr__(self):
        return '<User %s:%s %s>' % (cid(self), str(self.login), self.full_name())


class AnonymousUser(AnonymousUserMixin):
    def can(self, permissions):
        return False

    def is_administrator(self, private=False):
        return False

    @property
    def is_emailed(self):
        return False

login_manager.anonymous_user = AnonymousUser


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

## ============================================================ ##

def drop_table(cls):
    cls.__table__.drop(db.engine)

def show_tables():
    return local_reflect_meta().tables.keys()

def print_tables():
    for x in db.get_tables_for_bind():
        print(x)

def show_all():
    return local_reflect_meta().sorted_tables

def get_answers():
    return [x for x in list(answers) if not x[1].startswith('X')]

## ==================================================== ##

def load_system_config(user=None):
    g.system_config = make_config('system_config.attrs')

    if not user:
        user = current_user

    login = not user.is_anonymous and user.is_authenticated and user.login or ''

def send_email(subject, html, user, addr_to, addr_cc=None, addr_from=None):
    pass
