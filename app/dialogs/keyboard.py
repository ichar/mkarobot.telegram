# -*- coding: utf-8 -*-

import re
import time
from copy import deepcopy
import random

from config import (
     IsDebug, IsDeepDebug, IsTrace, IsPrintExceptions, IsWithPrintErrors, IsWithGroup, IsWithExtra,
     errorlog, print_to, print_exception,
     URL,
    )

from app.settings import DEFAULT_LANGUAGE, DEFAULT_PARSE_MODE, TESTNAMES, NO_RESULTS, gettrans
from app.dialogs.start import help, mainmenu
from app.handlers import *


_INFO = {
    'ru': (
"""
<b>Экстренная помощь</b>

Связь с дежурным психологом: +7 999 111-22-33
Переход на сайт компании: 
%(landing)s
%(application)s
%(debug)s
""",
"""
<b>Информация о пройденных тестах</b>
""",
"""
<b>Личный кабинет</b>
""",
"""
<b>Главное меню</b>
""",
"""
Вами пройдено всего тестов <b>%s</b> со следующими результатами.
""",
"""
Вами еще не пройдено ни одного теста.
""",
), 
    'uk': (
"""
<b>Екстрена допомога</b>

Зв'язок із черговим психологом: +7 999 111-22-33
Перехід до сайту компанії:  
%(landing)s
%(application)s
%(debug)s
""",
"""
<b>Інформація про пройдені тести</b>
""",
"""
<b>Особистий кабінет</b>
""",
"""
<b>Головне меню</b>
""",
"""
Пройдено всього тестів %s з наступними результатами.
""",
"""
Вами ще не пройдено жодного тесту.
""",
),
}

_KEYS = {
    'ru' : {
        'query_id'    : 'ID', 
        'chat_person' : 'Телеграм-чат', 
        'nic'         : 'Имя пользователя', 
        'date'        : 'Дата последнего посещения', 
        'lang'        : 'Язык', 
        'usage'       : 'Активность', 
        'age'         : 'Возраст', 
        'gender'      : 'Пол', 
        'accept'      : 'Акцепт',
    },
    'uk' : {
        'query_id'    : 'ID', 
        'chat_person' : 'Телеграм-чат', 
        'nic'         : "Ім'я користувача", 
        'date'        : 'Дата останнього відвідування', 
        'lang'        : 'Мова', 
        'usage'       : 'Активність', 
        'age'         : 'Вік', 
        'gender'      : 'Пол', 
        'accept'      : 'Акцепт',
    },
}


def get_info(i, lang, no_eof=None):
    s = _INFO[lang][i].strip()
    return no_eof and re.sub(r'\n', ' ', s) or s

def get_link(href, title, text):
    return '<a href="%s" title="%s">%s</a>' % (href, title, text)

def answer(bot, message, command, data=None, logger=None, keyboard=None, **kw):
    """
        Make the step's answer
    """
    lang = kw.get('lang') or DEFAULT_LANGUAGE
    storage = kw.get('storage')
    name = kw.get('name')

    is_run, is_help = True, False

    params = {
        'url' : URL,
    }

    info = ''

    if not keyboard:
        return
    elif keyboard == 'emergency':
        params['landing'] = get_link('http://mentalne.pro/landing/#', keyboard, gettrans('Landing', lang))
        params['application'] = get_link('%s%s' % (URL, 'welcome'), keyboard, gettrans('Application site', lang))
        params['debug'] = get_link('%s%s' % (URL, 'debug'), keyboard, gettrans('Debug', lang))
        info = get_info(0, lang) % params
        bot.send_message(message.chat.id, info, parse_mode=DEFAULT_PARSE_MODE)
        is_help = True

    elif keyboard == 'diagnosis':
        info = get_info(1, lang)
        bot.send_message(message.chat.id, info, parse_mode=DEFAULT_PARSE_MODE)
        tests = TESTNAMES[lang].keys()
        items = storage.get_test_results(name, lang, tests=tests, with_decode=True)
        count = len(items.keys())
        rows = []
        if count > 0:
            info = get_info(4, lang) % count
            for test in tests:
                if test in items:
                    info += '\n%s<b>%s %s:</b>' % ('', gettrans('Test', lang), test)
                    for i, item in enumerate(items[test]):
                        x = items[test][i].split(':')
                        s1 = '. '.join(x[0:-1])
                        s2 = len(x) > 1 and ' [%s]' % x[-1] or ''
                        s = '%s%s' % (s1, s2)
                        if s not in rows:
                            info += '\n%s%s' % (' '*4, s)
                            rows.append(s)
        else:
            info = get_info(5, lang)
        bot.send_message(message.chat.id, info.strip(), parse_mode=DEFAULT_PARSE_MODE)

    elif keyboard == 'profile':
        info = get_info(2, lang)
        bot.send_message(message.chat.id, info, parse_mode=DEFAULT_PARSE_MODE)
        keys = _KEYS[lang].keys()
        items = storage.get_items(name, keys, with_decode=True)
        info = ''
        for key in keys:
            info += '<b>%s</b>: %s\n' % (_KEYS[lang][key], items[key])
        bot.send_message(message.chat.id, info.strip(), parse_mode=DEFAULT_PARSE_MODE)

    elif keyboard == 'menu':
        info = get_info(3, lang)
        bot.send_message(message.chat.id, info, parse_mode=DEFAULT_PARSE_MODE)
        mainmenu(bot, message, logger=logger, lang=lang)

    else:
        is_run = False

    if not is_run or is_help:
        time.sleep(3)

        help(bot, message, logger=logger, mode=1, **kw)

    return 0
