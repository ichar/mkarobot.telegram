# -*- coding: utf-8 -*-

import os
import sys
import datetime
import traceback
import re

from collections import Iterable

basedir = os.path.abspath(os.path.dirname(__file__))
errorlog = os.path.join(basedir, 'traceback.log')

app_release = 1
is_webhook = False

# ----------------------------
# Global application constants
# ----------------------------

IsDebug                = 1  # Debug[errorlog]: prints general info
IsDeepDebug            = 0  # Debug[errorlog]: prints detailed info, replicate to console
IsTrace                = 1  # Trace[stdout]: output trace
IsPrintExceptions      = 1  # Flag: sets printing of exceptions
IsWithPrintErrors      = 1  # Flag: print selftest errors
IsRandomScores         = 1  # Flag: random score results letters
IsWithGroup            = 1  # Flag: output results with groups
IsWithExtra            = 1  # Flag: with extra answers
IsWithErrorlog         = 1  # Flag: use errorlog to print exceptions
IsTmpClean             = 1  # Flag: clean temp-folder
IsForceRefresh         = 1  # Flag: sets http forced refresh for static files (css/js)
IsDisableOutput        = 0  # Flag: disabled stdout
IsShowLoader           = 0  # Flag: sets page loader show enabled
IsNoEmail              = 1  # Flag: don't send email
IsFlushOutput          = 0  # Flag: flush stdout
IsPageClosed           = 0  # Flag: page is closed or moved to another address (page_redirect)

PUBLIC_URL = 'http://172.19.7.136:5000/'

page_redirect = {
    'items'    : ('*',),
    'base_url' : '/auth/onservice',
    'logins'   : ('admin',),
    'message'  : 'Waiting 30 sec',
}

LocalDebug = {
    'scenario'    : 0,
}

LOCAL_FULL_TIMESTAMP   = '%d-%m-%Y %H:%M:%S'
LOCAL_EXCEL_TIMESTAMP  = '%d.%m.%Y %H:%M:%S'
LOCAL_EASY_TIMESTAMP   = '%d-%m-%Y %H:%M'
LOCAL_EASY_DATESTAMP   = '%Y-%m-%d'
LOCAL_EXPORT_TIMESTAMP = '%Y%m%d%H%M%S'
UTC_FULL_TIMESTAMP     = '%Y-%m-%d %H:%M:%S'
UTC_EASY_TIMESTAMP     = '%Y-%m-%d %H:%M'
DATE_TIMESTAMP         = '%d/%m'
DATE_STAMP             = '%Y%m%d'

default_print_encoding = 'utf-8'
default_unicode        = 'utf-8'
default_encoding       = 'utf-8'
default_iso            = 'ISO-8859-1'

# ---------------------------------------
# AdvanceMentalHealthBot (mkarodebug_bot)
# ---------------------------------------

URL = "https://tvmlivehealth.herokuapp.com/"

BOT_NAME = 'MKaroDebugBot'
BOT_USERNAME = 'mkarodebug_bot'
TOKEN = '1887190810:AAEf_ZjWfWPsOIOlIFo8F4njT6yNhaPwFiM'
TELEGRAM_URL = 'https://api.telegram.org/bot1887190810:AAEf_ZjWfWPsOIOlIFo8F4njT6yNhaPwFiM' #/getwebhookinfo
TIMEZONE = 'Europe/Kiev'
TIMEZONE_COMMON_NAME = 'Kiev'

LOG_PATH = './logs'
LOG_NAME = 'bot'

# ----------------------------

CONNECTION = {}

# ----------------------------

path_splitter = '/'
n_a = 'n/a'
cr = '\n'

_config = None

def isIterable(v):
    return not isinstance(v, str) and isinstance(v, Iterable)

########################################################################

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard to guess string'
    SSL_DISABLE = False

    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_RECORD_QUERIES = True
    SQLALCHEMY_TRACK_MODIFICATIONS = True

    WTF_CSRF_ENABLED = False

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'storage', 'app.db.debug')

    @classmethod
    def init_app(cls, app):
        Config.init_app(app)


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'storage', 'app.db')

    @classmethod
    def init_app(cls, app):
        Config.init_app(app)


config = { \
    'production' : ProductionConfig,
    'default'    : DevelopmentConfig,
}

##  --------------------------------------- ##

def setup_console(sys_enc=default_unicode):
    pass

def print_to(f, v, mode='ab', request=None, encoding=default_encoding):
    if IsDisableOutput:
        return
    items = not isIterable(v) and [v] or v
    if not f:
        f = getErrorlog()
    fo = open(f, mode=mode)
    def _out(s):
        if not isinstance(s, bytes):
            fo.write(s.encode(encoding, 'ignore'))
        else:
            fo.write(s)
        fo.write(cr.encode())
    for text in items:
        try:
            if IsDeepDebug:
                print(text)
            if request is not None:
                _out('%s>>> %s [%s]' % (cr, datetime.datetime.now().strftime(UTC_FULL_TIMESTAMP), request.url))
            _out(text)
        except Exception as e:
            pass
    fo.close()

def print_exception(stack=None):
    if IsWithErrorlog:
        print_to(errorlog, '%s>>> %s:%s' % (cr, datetime.datetime.now().strftime(LOCAL_FULL_TIMESTAMP), cr))
        traceback.print_exc(file=open(errorlog, 'a'))
        if stack is not None:
            print_to(errorlog, '%s>>> Traceback stack:%s' % (cr, cr))
            traceback.print_stack(file=open(errorlog, 'a'))
    else:
        print('%s>>> %s:%s' % (cr, datetime.datetime.now().strftime(LOCAL_FULL_TIMESTAMP), cr))
        traceback.print_exc()
        if stack is not None:
            print('%s>>> Traceback stack:%s' % (cr, cr))
            traceback.print_stack()
    
def getErrorlog():
    return errorlog

def getCurrentDate():
    return datetime.datetime.now().strftime(LOCAL_EASY_DATESTAMP)
