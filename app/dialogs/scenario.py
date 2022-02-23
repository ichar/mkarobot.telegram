# -*- coding: utf-8 -*-

__all__ = [
    'make_start', 'make_description', 'make_help', 'make_commands', 'make_tests', 
    'make_begin', 'make_answer', 'make_stop', 'make_langs', 'make_version', 
    'make_debug', 'make_message',
    ]

import os
import sys
import re
import time
"""
from config import (
     IsDebug, IsDeepDebug, IsTrace, IsPrintExceptions, 
     errorlog, print_to, print_exception,
     is_webhook,
    )
"""
from app.settings import *
from app.dialogs.start import *

from app.utils import getToday, getDate, isIterable

from ..database import activate_storage, deactivate_storage

basedir = os.path.split(os.path.abspath(os.path.dirname(__file__)))[0]

def setup():
    if basedir not in sys.path:
        sys.path.append(basedir)

        if IsDeepDebug:
            print('... basedir: %s' % basedir)

##  =====================
##  Bot Scenario Handlers
##  =====================

class Chat:
    
    def __init__(self, message):
        self._id = message and message.chat.id or 0
        self._name = 'chat:%s' % self._id
        self._person = message and message.chat.first_name or '...'

        self.message = message

    @property
    def id(self):
        return self._id
    @property
    def name(self):
        return self._name
    @property
    def person(self):
        return self._person


def activate(command, query_id, message):
    chat = Chat(message)

    storage = activate_storage(command=command, query_id=query_id, person=chat.person)

    if IsDebug:
        storage.dump(chat.name)

    return chat, storage

def deactivate(chat, storage):
    deactivate_storage(storage)
    del chat

def get_lang(message):
    chat, storage = activate('lang', 0, message)
    try:
        return storage.get_lang(chat.name)
    finally:
        deactivate(chat, storage)

## ========================================== ##

def make_start(bot, message, logger=None, **kw):
    start(bot, message, logger=logger, lang=get_lang(message), **kw)

def make_description(bot, message, logger=None, **kw):
    description(bot, message, logger=logger, lang=get_lang(message), **kw)

def make_help(bot, message, logger=None, **kw):
    help(bot, message, logger=logger, lang=get_lang(message), **kw)

def make_commands(bot, message, logger=None, **kw):
    commands(bot, message, logger=logger, lang=get_lang(message), **kw)

def make_tests(bot, message, logger=None, **kw):
    tests(bot, message, logger=logger, lang=get_lang(message), **kw)

def make_langs(bot, message, logger=None, **kw):
    langs(bot, message, logger=logger, lang=get_lang(message), **kw)

def make_version(bot, message, logger=None, **kw):
    bot.send_message(message.chat.id, product_version)

def make_debug():
    chat, storage = activate('', 0, '')
    try:
        return storage.debug()
    finally:
        deactivate(chat, storage)

def make_message(bot, info, logger=None, **kw):
    chat, storage = activate('message', 0, '')
    try:
        x = info[1:].split(':')
        person = x[1]
        text = x[2]
        chat_id = storage.get_person_chat_id(person)
        if chat_id:
            bot.send_message(chat_id, text)
    except:
        pass
    deactivate(chat, storage)

## -------------------------- ##

def make_answer(bot, message, command, data=None, logger=None, **kw):
    """
        Reply an answer for the dialog's question
    """
    setup()

    query_id = kw.get('query_id') or -1

    if logger is not None:
        logger('%s:%s%s' % (command, query_id, data and '[%s]' % data or ''), data=message.json)

    chat, storage = activate(command, query_id, message)

    module, keyboard, index, question, with_usage, code = '', '', -1, 0, False, 1

    commands = ['T%s' % str(n) for n in range(1, tests_count())]

    lang = storage.get_lang(chat.name)

    is_test = False

    # -------------------------------
    # Схема интерпретации команд бота
    # -------------------------------

    if command == 'button' and data == 'begin:0':
        module = BEGIN[0]
    elif command == 'button' and data == 'tests:0':
        make_tests(bot, message, logger=logger, **kw)
        return 1
    elif command == 'begin-dialog':
        module = BEGIN[0]
    elif command == 'end':
        module = END[0]
    elif command == 'clear':
        storage.delete(chat.name)
    elif command in STARTMENU[lang][1].values():
        keyboard = command
    elif command in ('ru', 'uk'):
        storage.set_lang(chat.name, command)
    elif command in ('button', 'q', '...') or command in commands:
        if kw.get('index'):
            index = kw['index']
        else:
            words = message.text.split('.')
            index = len(words) > 1 and words[0].isdigit() and int(words[0]) or 0

            if command.startswith('T') or words[0].startswith('T'):
                is_test = True

            spec = SCENARIO[index][1]
            if spec is not None and len(words) > 2:
                question = words[1].isdigit() and int(words[1]) or 0
                if question >= spec:
                    question = -1
                    index += 1
            elif index == 0:
                if not is_test:
                    nic = storage.get(chat.name, 'nic')
                    if nic:
                        index = 1
            else:
                index += 1

        if index == 0 and is_test:
            question = len(words) > 1 and words[1].isdigit() and int(words[1]) or 0
            if words[0].startswith('T'):
                x = re.sub(r'[/Tt]', '', words[0])
            else:
                x = re.sub(r'[/Tt\D ]', '', command)
            index = x and int(x) or 0
            module = TESTS[index][0]

            if question == 0:
                storage.delete(chat.name, command='%s.' % command)
                storage.delete(chat.name, command='warning')

        elif index > len(SCENARIO)-1:
            module = END[0]
        else:
            module = SCENARIO[index][0]
    else:
        info = message.text

        if IsDeepDebug:
            print('... user info message:', info)

        if info in STARTMENU[lang][1].keys():
            keyboard = STARTMENU[lang][1][info]
        else:
            module = THANKS[0]

    if IsTrace:
        print('... action(module, keyboard):[%s|%s]' % (module, keyboard))

    if not (module or keyboard):
        return 0

    if keyboard:
        with_usage = True

        if IsTrace:
            print('... make_answer:%s keyboard:%s' % (chat.person, keyboard))

        module = KEYBOARD[0]

    elif index == 0 and question == 0 or question == 1:
        with_usage = True

    if is_test:
        if IsTrace:
            print('... make_answer:%s module:%s, index:%s, question:%s, answer:%s' % (
                chat.person, module, index, question, storage.answer))

    storage.register(chat.name, data, with_usage=with_usage)

    # ----------------------
    # Старт модуля обработки
    # ----------------------

    try:
        _module = __import__(module, fromlist=['answer'])

        if not (_module is not None and hasattr(_module, 'answer')):
            return True

        if is_test and question == 0:
            text = '<b>%s %s%s. %s (%s %s)\n* * *</b>' % (gettrans('Test', lang), gettrans('#', lang), 
                index, 
                TESTNAMES[lang]['T%s' % index], 
                gettrans('total questions', lang), _module.total_questions())
            bot.send_message(message.chat.id, text, parse_mode=DEFAULT_PARSE_MODE)

        code = _module.answer(bot, message, command, data=data, logger=logger, question=question, keyboard=keyboard,
            chat=chat, storage=storage, name=chat.name, lang=lang, 
            **kw)

    except ModuleNotFoundError:
        code = 0

    except:
        if IsPrintExceptions:
            print_exception()

    if command == 'end':
        if kw.get('with_clear'):
            storage.clear(chat.name)

    deactivate(chat, storage)

    return code is None and 1 or code

def make_begin(bot, message, logger=None, **kw):
    begin(bot, message, logger=logger, lang=get_lang(message), **kw)
    time.sleep(1)
    make_answer(bot, message, 'begin-dialog', logger=logger)

def make_stop(bot, message, logger=None, **kw):
    stop(bot, message, logger=logger, lang=get_lang(message), **kw)

## -------------------------- ##

def selftest(chat_name, lang=None, with_print=None):
    """
        Self Test of Storage Results
    """
    setup()

    tests = {}

    storage = activate_storage()

    for module, key in TESTS:
        if not key:
            continue

        tests[key] = '...'

        try:
            _module = __import__(module, fromlist=['selftest'])
    
            if not (_module is not None and hasattr(_module, 'selftest')):
                continue

            data = storage.get_data(chat_name, '%s.*' % key, with_decode=True)

            if IsDeepDebug:
                print(chat_name, data, key)

            if not data:
                tests[key] = NO_DATA
                continue
            
            tests[key] = _module.selftest(data, lang=lang or DEFAULT_LANGUAGE, with_print=with_print)
        except:
            tests[key] = 'Exception in %s' % module

            if IsPrintExceptions:
                print_exception()

    deactivate_storage(storage)

    return tests
