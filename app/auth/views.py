# -*- coding: utf-8 -*-

from flask import abort, render_template, redirect, request, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from flask_babel import gettext

from werkzeug.urls import url_quote, url_unquote

from flask import session
#from passlib.hash import pbkdf2_sha256 as hasher

from config import (
     IsDebug, IsDeepDebug, IsTrace, IsPrintExceptions, IsNoEmail, IsPageClosed, page_redirect, errorlog, print_to, print_exception,
     default_unicode, default_encoding
     )

from . import auth
from ..import db, babel

from ..decorators import user_required
from ..utils import monthdelta, unquoted_url, decode_base64
from ..models import User, send_email, load_system_config
from ..database import get_locale as get_user_locale
from ..settings import *

from .forms import LoginForm, ChangePasswordForm, ResetPasswordRequestForm, PasswordResetForm

IsResponseNoCached = 0

_EMERGENCY_EMAILS = ('ichar.xx@gmail.com',)

##  ===========================
##  User Authentication Package
##  ===========================

@babel.localeselector
def get_locale():
    return get_request_item('locale') or get_user_locale()

def is_valid_pwd(x):
    v = len(x) > 9 or (len(x) > 7 and
        len(re.sub(r'[\D]+', '', x)) > 0 and
        len(re.sub(r'[\d]+', '', x)) > 0 and
        len(re.sub(r'[\w]+', '', x)) > 0) \
        and True or False
    return v

def is_pwd_changed(user):
    pass

def send_message(user, token, **kw):
    pass

def send_password_reset_email(user, **kw):
    pass

@auth.before_app_request
def before_request():
    g.current_user = current_user
    g.engine = None

    if IsDeepDebug:
        print('--> before_request:is_authenticated:%s is_active:%s' % (current_user.is_authenticated, current_user.is_active))

    if not request.endpoint:
        return

def get_default_url(user=None):
    pass

def menu(force=None):
    pass

@auth.route('/login', methods=['GET', 'POST'])
def login():
    pass

@auth.route('/default', methods=['GET', 'POST'])
def default():
    pass

@auth.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    pass

@auth.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    pass

@auth.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    pass

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('auth.login'))

@auth.route('/forbidden')
def forbidden():
    abort(403)

@auth.route('/onservice')
def onservice():
    if not IsPageClosed:
        next = request.args.get('next')
        return redirect(next or '/')
        
    kw = make_platform(mode='auth')

    kw.update({
        'title'        : gettext('Application Login'),
        'page_title'   : gettext('Application Auth'),
        'header_class' : 'middle-header',
        'show_flash'   : True,
        'semaphore'    : {'state' : ''},
        'sidebar'      : {'state' : 0, 'title' : ''},
        'module'       : 'auth',
        'message'      : page_redirect.get('message') or gettext('Software upgrade'),
    })

    kw['vsc'] = vsc()

    return render_template('auth/onservice.html', **kw)

@auth.route('/unconfirmed')
def unconfirmed():
    pass

@auth.route('/confirm/<token>')
@login_required
def confirm(token):
    pass
