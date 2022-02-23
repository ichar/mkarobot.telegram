# -*- coding: utf-8 -*-

import re
import random
import json
from datetime import datetime

#https://pypi.org/project/user-agents/
from user_agents import parse as user_agent_parse

from flask import (
    Response, render_template, url_for, redirect, request, make_response, 
    jsonify, flash, stream_with_context, g, current_app
)
from flask_login import login_required, current_user
from flask_babel import gettext, lazy_gettext

from config import (
    CONNECTION,
    IsDebug, IsDeepDebug, IsTrace, IsShowLoader, IsForceRefresh, IsPrintExceptions, IsNoEmail, 
    basedir, errorlog, print_to, print_exception,
    default_unicode, default_encoding,
    LOCAL_EASY_DATESTAMP, getCurrentDate,
    is_webhook,
)

product_version = '1.02, 2021-10-30 (Python3, Redis)'

#########################################################################################

#   -------------
#   Default types
#   -------------

DEFAULT_LANGUAGE = 'uk'
DEFAULT_PARSE_MODE = 'HTML'
DEFAULT_PER_PAGE = 10
DEFAULT_PAGE = 1
DEFAULT_UNDEFINED = '---'
DEFAULT_DATE_FORMAT = ('%d/%m/%Y', '%Y-%m-%d',)
DEFAULT_DATETIME_FORMAT = '%Y-%m-%d< %H:%M:%S'
DEFAULT_DATETIME_INLINE_FORMAT = '<nobr>%Y-%m-%d</nobr> <nobr>%H:%M:%S</nobr>'
DEFAULT_DATETIME_INLINE_SHORT_FORMAT = '<nobr>%Y-%m-%d</nobr><br><nobr>%H:%M</nobr>'
DEFAULT_DATETIME_TODAY_FORMAT = '%d.%m.%Y'
DEFAULT_HTML_SPLITTER = ':'

BEGIN = (
    'dialogs.begin',
)

SCENARIO = (
    ('dialogs.person', None),
    ('dialogs.gender', None),
    ('dialogs.age', None),
    ('dialogs.occupation', None),
    ('dialogs.education', None),
    ('dialogs.marital_status', None),
    ('dialogs.children', None),
    ('dialogs.upbringing', None),
    ('dialogs.childhood', None),
    ('dialogs.family', None),
    ('dialogs.relationships', None),
    ('dialogs.discomfort', None),
    ('dialogs.stress', None),
    ('dialogs.grievance', 23),
)

TESTS = (
    ('', None),
    ('dialogs.ptest1', 'T1',),
    ('dialogs.ptest2', 'T2',),
    ('dialogs.ptest3', 'T3',),
    ('dialogs.ptest4', 'T4',),
    ('dialogs.ptest5', 'T5',),
    ('dialogs.ptest6', 'T6',),
    ('dialogs.ptest7', 'T7',),
    ('dialogs.ptest8', 'T8',),
    ('dialogs.ptest9', 'T9',),
    ('dialogs.ptest10', 'T10',),
    ('dialogs.ptest11', 'T11',),
    ('dialogs.ptest12', 'T12',),
    ('dialogs.ptest13', 'T13',),
    ('dialogs.ptest14', 'T14',),
    ('dialogs.ptest15', 'T15',),
    ('dialogs.ptest16', 'T16',),
    ('dialogs.ptest17', 'T17',),
)

TESTNAMES = {
    'ru': {
        'T1'  : 'Госпитальная шкала тревоги и депрессии (HADS)',
        'T2'  : 'Индивидуально-типологический опросник Собчик (ИТО)',
        'T3'  : 'Измерение уровня депрессии (BDI)',
        'T4'  : 'Уровень тревожности Бека',
        'T5'  : 'Острая реакция на стресс',
        'T6'  : 'Шкала депрессии Цунга',
        'T7'  : 'Определение характеристик темперамента',
        'T8'  : 'Тревожность Тейлора',
        'T9'  : 'Уровень социальной фрустрированности Вассермана',
        'T10' : 'Шкала реактивной и личностной тревожности Спилбергера-Ханина',
        'T11' : 'Эмоциональное выгорание Бойко',
        'T12' : 'Мотивация к успеху Реана',
        'T13' : 'Эмоциональное выгорание Маслач',
        'T14' : 'Диагностика враждебности Кука-Медлея',
        'T15' : 'Акцентуация характера Шмишека',
        'T16' : 'Исследование самоотношения Пантелеева',
        'T17' : 'Агрессивность Почебут',
    },
    'uk': {
        'T1'  : 'Госпітальна шкала тривоги та депресії (HADS)',
        'T2'  : 'Індивідуально-типологічний опитувальник Собчик (ІТО)',
        'T3'  : 'Вимірювання рівня депресіїТест (BDI)',
        'T4'  : 'Рівень тривожності Бека',
        'T5'  : 'Гостра реакція на стрес',
        'T6'  : 'Шкала депресії Цунга',
        'T7'  : 'Визначення характеристик темпераменту',
        'T8'  : 'Тривожність Тейлора',
        'T9'  : 'Рівень соціальної фрустрованність Васермана',
        'T10' : 'Шкала реактивної і особистісної тривожності Спілбергера-Ханіна',
        'T11' : 'Емоційне вигорання Бойко',
        'T12' : 'Мотивацію до успіху Реана',
        'T13' : 'Психологічне вигорання Маслач',
        'T14' : 'Діагностика ворожості Кука-Медлея',
        'T15' : 'Акцентуація характеру Шмішека',
        'T16' : 'Дослідження самоставлення Пантєєлєва',
        'T17' : 'Агресивність Почебут',
    },
}

STARTMENU = {
    'ru': [
        (('Доверительная беседа', 'begin:0'), ('Психологические тесты', 'tests:0')), 
        { 
            'Экстренная помощь'              : 'emergency', 
            'Информация о пройденных тестах' : 'diagnosis', 
            'Личный кабинет'                 : 'profile',
            'Главное меню'                   : 'menu',
        }, 
        (('', '')),
    ],
    'uk': [
        (('Довірлива бесіда', 'begin:0'), ('Психологічні тести', 'tests:0')), 
        { 
            'Екстрена допомога'              : 'emergency', 
            'Інформація про пройдені тести'  : 'diagnosis', 
            'Особистий кабінет'              : 'profile',
            'Головне меню'                   : 'menu',
        }, 
        (('', '')),
    ],
}

_TRANS = {
    'ru': {
        "#"                : "№",
        "Landing"          : "Портал психологического здоровья",
        "Application site" : "Сайт приложения",
        "Debug"            : "Журнал бота",
        "Test"             : "Тест",
        "total questions"  : "всего вопросов",
    },
    'uk': {
        "#"                : "№",
        "Landing"          : "Портал психологічного здоров'я",
        "Application site" : "Сайт програми",
        "Debug"            : "Журнал бота",
        "Test"             : "Тест",
        "total questions"  : "всього питань",
    },
}

KEYBOARD = (
    'dialogs.keyboard',
)

THANKS = (
    'dialogs.thanks',
)

END = (
    'dialogs.end',
)

NO_RESULTS = 'not enough results'
NO_DATA = 'no data'

default_locale = 'rus'


def tests_count():
    return len(TESTS)

def gettrans(key, lang):
    return _TRANS[lang or DEFAULT_LANGUAGE].get(key) or key

## ================================================== ##

_agent = None
_user_agent = None

def IsAndroid():
    return _agent.platform == 'android'
def IsiOS():
    return _agent.platform == 'ios' or 'iOS' in _user_agent.os.family
def IsiPad():
    return _agent.platform == 'ipad' or 'iPad' in _user_agent.os.family
def IsLinux():
    return _agent.platform == 'linux'

def IsChrome():
    return _agent.browser == 'chrome'
def IsFirefox():
    return _agent.browser == 'firefox'
def IsSafari():
    return _agent.browser == 'safari' or 'Safari' in _user_agent.browser.family
def IsOpera():
    return _agent.browser == 'opera' or 'Opera' in _user_agent.browser.family

def IsIE(version=None):
    ie = _agent.browser.lower() in ('explorer', 'msie',)
    if not ie:
        return False
    elif version:
        return float(_agent.version) == version
    return float(_agent.version) < 10
def IsSeaMonkey():
    return _agent.browser.lower() == 'seamonkey'
def IsEdge():
    return 'Edge' in _agent.string
def IsMSIE():
    return _agent.browser.lower() in ('explorer', 'ie', 'msie', 'seamonkey',) or IsEdge()

def IsMobile():
    return IsAndroid() or IsiOS() or IsiPad() or _user_agent.is_mobile or _user_agent.is_tablet
def IsNotBootStrap():
    return IsIE(10) or IsAndroid()
def IsWebKit():
    return IsChrome() or IsFirefox() or IsOpera() or IsSafari()

def BrowserVersion():
    return _agent.version

def BrowserInfo(force=None):
    mobile = 'IsMobile:[%s]' % (IsMobile() and '1' or '0')
    info = 'Browser:[%s] %s Agent:[%s]' % (_agent.browser, mobile, _agent.string)
    browser = IsMSIE() and 'IE' or IsOpera() and 'Opera' or IsChrome() and 'Chrome' or IsFirefox() and 'FireFox' or IsSafari() and 'Safari' or None
    if force:
        return info
    return browser and '%s:%s' % (browser, mobile) or info

## -------------------------------------------------- ##

def get_request_item(name, check_int=None, args=None, is_iterable=None):
    if args:
        x = args.get(name)
    elif request.method.upper() == 'POST':
        if is_iterable:
            return request.form.getlist(name)
        else:
            x = request.form.get(name)
    else:
        x = None
    if not x and (not check_int or (check_int and x in (None, ''))):
        x = request.args.get(name)
    if check_int:
        if x in (None, ''):
            return None
        elif x.isdigit():
            return int(x)
        elif x in 'yY':
            return 1
        elif x in 'nN':
            return 0
        else:
            return None
    if x:
        if x == DEFAULT_UNDEFINED or x.upper() == 'NONE':
            x = None
        elif x.startswith('{') and x.endswith('}'):
            return eval(re.sub('null', '""', x))
    return x or ''

def get_request_items():
    return request.method.upper() == 'POST' and request.form or request.args

def has_request_item(name):
    return name in request.form or name in request.args

def get_request_search():
    return get_request_item('reset_search') != '1' and get_request_item('search') or ''

def get_page_params(view=None):
    pass

def default_user_avatar(user=None):
    pass

def make_platform(mode=None, debug=None):
    global _agent, _user_agent

    agent = request.user_agent
    browser = agent.browser

    if browser is None:
        return { 'error' : 'Access is not allowed!' }

    os = agent.platform
    root = '%s/' % request.script_root

    _agent = agent
    _user_agent = user_agent_parse(agent.string)

    if IsTrace:
        print_to(errorlog, '\n==> agent:%s[%s], browser:%s' % (repr(agent), _user_agent, browser), request=request)

    is_owner = False
    is_admin = False
    is_manager = True
    is_operator = False

    avatar = None

    referer = ''
    links = {}

    is_mobile = IsMobile()
    is_default = 1 or os in ('ipad', 'android',) and browser in ('safari', 'chrome',) and 1 or 0 
    is_frame = not is_mobile and 1 or 0

    version = agent.version
    css = IsMSIE() and 'ie' or is_mobile and 'mobile' or 'web'

    platform = '[os:%s, browser:%s (%s), css:%s, %s %s%s%s]' % (
        os, 
        browser, 
        version, 
        css, 
        default_locale, 
        is_default and ' default' or ' flex',
        is_frame and ' frame' or '', 
        debug and ' debug' or '',
    )

    kw = {
        'os'             : os, 
        'platform'       : platform,
        'root'           : root, 
        'back'           : '',
        'agent'          : agent.string,
        'version'        : version, 
        'browser'        : browser, 
        'browser_info'   : BrowserInfo(0),
        'is_linux'       : IsLinux() and 1 or 0,
        'is_demo'        : 0, 
        'is_frame'       : 0, 
        'is_mobile'      : is_mobile and 1 or 0,
    }

    if mode:
        kw[mode] = True

    if mode in ('auth',):
        kw['bootstrap'] = '-new'

    kw.update({
        'links'          : links, 
        'with_avatar'    : 1,
        'with_post'      : 1,
        'logo'           : '', 
    })

    kw['is_active_scroller'] = 0 if IsMSIE() or IsFirefox() or is_mobile else 1

    if IsTrace and IsDeepDebug:
        print_to(errorlog, '--> make_platform:%s' % mode)

    return kw

def make_keywords():
    return (
        # --------------
        # Error Messages
        # --------------
        "'Execution error':'%s'" % gettext('Execution error'),
        # -------
        # Buttons
        # -------
        "'Add':'%s'" % gettext('Add'),
        "'Back':'%s'" % gettext('Back'),
        "'Calculate':'%s'" % gettext('Calculate'),
        "'Cancel':'%s'" % gettext('Cancel'),
        "'Confirm':'%s'" % gettext('Confirm'),
        "'Close':'%s'" % gettext('Close'),
        "'Execute':'%s'" % gettext('Execute'),
        "'Finished':'%s'" % gettext('Done'),
        "'Frozen link':'%s'" % gettext('Frozen link'),
        "'Link':'%s'" % gettext('Link'),
        "'OK':'%s'" % gettext('OK'),
        "'Open':'%s'" % gettext('Open'),
        "'Reject':'%s'" % gettext('Decline'),
        "'Rejected':'%s'" % gettext('Rejected'),
        "'Remove':'%s'" % gettext('Remove'),
        "'Run':'%s'" % gettext('Run'),
        "'Save':'%s'" % gettext('Save'),
        "'Search':'%s'" % gettext('Search'),
        "'Select':'%s'" % gettext('Select'),
        "'Update':'%s'" % gettext('Update'),
        # ----
        # Help
        # ----
        "'Attention':'%s'" % gettext('Attention'),
        "'All':'%s'" % gettext('All'),
        "'Commands':'%s'" % gettext('Commands'),
        "'Help':'%s'" % gettext('Help'),
        "'Help information':'%s'" % gettext('Help information'),
        "'Helper keypress guide':'%s'" % gettext('Helper keypress guide'),
        "'System information':'%s'" % gettext('System information'),
        "'Total':'%s'" % gettext('Total'),
        # --------------------
        # Flags & Simple Items
        # --------------------
        "'error':'%s'" % gettext('error'),
        "'yes':'%s'" % gettext('Yes'),
        "'no':'%s'" % gettext('No'),
        "'none':'%s'" % gettext('None'),
        "'true':'%s'" % 'true',
        "'false':'%s'" % 'false',
        # ------------------------
        # Miscellaneous Dictionary
        # ------------------------
        "'batch':'%s'" % gettext('batch'),
        # -------------
        # Notifications
        # -------------
        "'Admin Find':'%s'" % gettext('Find (name, login, email)'),
    )

def init_response(title):
    host = request.form.get('host') or request.host_url

    if 'debug' in request.args:
        debug = request.args['debug'] == '1' and True or False
    else:
        debug = None

    kw = make_platform(debug=debug)
    keywords = make_keywords()
    forms = ('index', 'admin',)

    now = datetime.today().strftime(DEFAULT_DATE_FORMAT[1])

    kw.update({
        'title'        : '%s. %s' % (gettext('ADVANCEMENTALHEALTHGROUP'), gettext(title)),
        'host'         : host,
        'locale'       : default_locale, 
        'language'     : DEFAULT_LANGUAGE == 'uk' and 'uk' or 'ru',
        'keywords'     : keywords, 
        'forms'        : forms,
        'now'          : now,
    })

    kw['selected_data_menu_id'] = get_request_item('selected_data_menu_id')
    kw['window_scroll'] = get_request_item('window_scroll')
    kw['avatar_width'] = '80'

    return debug, kw

def vsc(force=False):
    return (IsIE() or IsForceRefresh or force) and ('?%s' % str(int(random.random()*10**12))) or ''

def is_app_public():
    return IsPublic and request.host_url == PUBLIC_URL

def get_navigation():
    return None
