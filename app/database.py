# -*- coding: utf-8 -*-

import os
import re
from urllib.parse import urlparse

import redis

from config import (
     IsDebug, IsDeepDebug, IsTrace, IsPrintExceptions, 
     errorlog, print_to, print_exception,
     is_webhook,
    )

from app import db, babel
from app.settings import DEFAULT_LANGUAGE, g, current_app, product_version, tests_count
from app.utils import getToday, getDate, isIterable

#from flask_babel import gettext

_DEBUG_HTML = '''
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <meta http-equiv="Cache-Control" content="must-revalidate">
  <meta http-equiv="Pragma" content="no-cache">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta name="apple-mobile-web-app-capable" content="yes">
  <meta name="mobile-web-app-capable" content="yes">
  <title>debug</title>
  <style type="text/css">
    body { padding:10px; font-family:Arial,Tahoma; background-color:#ffffff; }
    h1 { font-size:14px; padding:0; margin:0 0 10px 0; }
    h1.caption { font-weight:bold; color:chocolate; font-size:24px; }
    h2 { font-size:12px; color:#9c5478; font-weight:normal; }
    .bg1 { background-color:#eee; }
    .bg2 { background-color:#fed; }
    .bg3 { background-color:#cdc; }
    .negative .value { background-color:#46a !important; color:#fff; }
    .zero .value { background-color:#d24 !important; color:#fff; }
    .possitive .value {}
    .value { width:fit-content; padding:0 2px 0 2px; }
    .result { background-color:#333; color:#fff; }
    .result .value { color:#333; }
    .text { background-color:#884; color:#fff; }
    .text .value { color:#333; }
    div.server { font-size:12px; }
    div.person { border:1px solid #ccc; padding:5px; margin-bottom:5px; width:fit-content; }
    div.chat { font-weight:bold; margin-top:10px; color:#6880de; }
    div.box { padding-left:20px; }
    table.person { font-size:14px; margin-left:20px; }
    table.person .data { display:flex; }
    table.line { font-size:12px; margin-top:10px; }
    table.line td { white-space:nowrap; border:1px solid #ccc; padding:3px; }
    table.line td.data .value { background-color:#eee; }
    table.dialog { font-size:12px; }
  </style>
</head>
<body>
  <div>
    <h1 class="caption">Психолог ПТСР [TVMLiveHealthBot Telegram Bot]</h1>
    <div>%(server)s</div>
    <div>%(header)s</div>
    <hr>
    <div class="box">%(content)s</div>
  </div>
</body>
</html>
'''

_RES_PREFIX = '.R'
_TEXT_PREFIX = '.T'


@babel.localeselector
def get_locale(lang=None):
    try:
        print(current_app.config['BABEL_TRANSLATION_DIRECTORIES'])
    except:
        print('Babel Error!')
    return lang or DEFAULT_LANGUAGE


class RedisStorage:
    """
        Redis Storage Class
    """
    def __init__(self):
        self.redis_url = os.environ.get("REDIS_URL", "http://localhost:6379")
        self.is_local = True if 'localhost' in self.redis_url else False

        self.rserver = None

    def _init_state(self, command, query_id, chat_person):
        self._command = command
        self._query_id = query_id
        self._chat_person = chat_person

        if self.is_local:
            url = urlparse(self.redis_url)
            self.rserver = redis.Redis(host=url.hostname, port=url.port, username=url.username, password=url.password, 
                ssl=False, ssl_cert_reqs=None)
        else:
            self.rserver = redis.from_url(self.redis_url)

        self._question = None
        self._answer = None

        self._tests_count = tests_count()

        #if is_webhook:
        #    g.rserver = self.rserver

        if IsDeepDebug:
            print('>>> RedisStorage:%s' % self.rserver.client())

    @property
    def command(self):
        return self._command
    @property
    def query_id(self):
        return self._query_id
    @property
    def chat_person(self):
        return self._chat_person
    @property
    def question(self):
        return self._question
    @property
    def answer(self):
        return self._answer

    def is_exists(self, name):
        return self.rserver and self.rserver.exists(name) and True or False

    def getall(self, name):
        return self.rserver.hgetall(name)

    def get(self, name, key, with_decode=None):
        x = self.rserver.hget(name, key)
        if with_decode:
            return x.decode()
        return x

    def get_items(self, name, keys, with_decode=None):
        items = {}
        for key in keys:
            items[key] = self.get(name, key, with_decode=with_decode)
            if IsDeepDebug:
                print(key, items[key])
        return items

    def get_test_results(self, name, lang, tests=None, **kw):
        data = self.getall(name)
        keys = [x for x in data.keys()]

        if not tests:
            tests = TESTNAMES[lang].keys()

        items = {}

        for test in tests:
            for key in keys:
                k = key.decode()
                if k.startswith(test):
                    x = k.split('.')
                    if len(x) > 1 and x[0] == test and x[1].startswith('T'):
                        value = data[key].decode()
                        if not value:
                            continue
                        if test not in items:
                            items[test] = []
                        items[test].append(value)

        return items

    def get_chat_names(self):
        return self.rserver.client() and [x.decode() for x in self.rserver.keys('*')] or []

    def get_data(self, name, key, with_decode=None):
        data = self.getall(name)

        res = {}

        is_parse = '.' not in key
        is_all = '*' in key

        k0 = None
        k1 = re.sub(r'\*', '', key)
        k2 = re.sub(r'\.', '', k1)

        for k in [x.decode() for x in data.keys()]:
            k0, p = k2, '.' in k and '.' or ''
            if is_parse:
                x = k.split('.')[0]
                if x.startswith(k1):
                    k0, p = x, '.'
                else:
                    continue
            if k.startswith(k1) and k0 not in res:
                r = [(x.decode(), with_decode and data[x].decode() or data[x]) 
                        for x in data.keys() if is_all and (k0+p) in x.decode() or k0 == x.decode()]
                if len(r) > 1:
                    res[k0] = dict(r)
                else:
                    res[k0] = r and r[0][1] or ''

        return res

    def set(self, name, key, value, mapping=None, with_encode=None):
        self.rserver.hset(name, key, with_encode and value.encode() or value, mapping=mapping)

    def delete(self, name, command=None, clear=None):
        try:
            if self.is_exists(name):
                if clear:
                    self.rserver.delete(name)
                    return
                data = self.getall(name)
                keys = sorted([x.decode() for x in data.keys()])
                if command:
                    for key in keys:
                        if key.startswith(command):
                            self.rserver.hdel(name, key)
                else:
                    for key in keys:
                        if key not in ('query_id', 'chat_person', 'date', 'nic', 'lang', 'usage'):
                            self.rserver.hdel(name, key)
        except:
            pass

    def clear(self, name):
        self.delete(name, clear=True)

    def dump(self, name):
        if IsDeepDebug:
            print('dump redis:%s' % self.getall(name))

    def register(self, name, data, with_usage=None):
        if not data:
            return
    
        mapping = { 'command' : self.command, 'query_id' : self.query_id, 'chat_person' : self.chat_person, 'date' : getDate(getToday()) }

        is_error = False

        try:
            question, answer = data.split(':')
        except:
            question, answer = 0, -1
            is_error = True

        if with_usage:
            usage = self.get(name, 'usage')
            mapping['usage'] = usage and int(usage)+1 or 1

        if not is_error:
            self.set(name, question, answer, mapping=mapping)

        self._question = question
        self._answer = answer

    def get_person_chat_id(self, chat_person):
        if not self.rserver.client():
            return None

        for name in [x.decode() for x in self.rserver.keys('*')]:
            x = name.split(':')
            chat_id = x[1] and x[1].isdigit() and int(x[1])
            if chat_id:
                if self.get(name, 'chat_person').decode() == chat_person:
                    return chat_id

        return None

    def debug(self):
        groups = (
            ['person', '', ('query_id', 'chat_person', 'nic', 'date', 'command', 'lang', 'usage', 'warning')], 
            ['line', 'Тесты:', [(int(n), 'T%s.' % str(n)) for n in range(1, self._tests_count+1)]], 
            ('dialog', 'Клиническая беседа:', None)
            )

        html = {}

        backgrounds, bid = ('bg1', 'bg2', 'bg3'), 0

        html['server'] = '<div class="server">%s</div>' % '&nbsp;'.join([
            repr(self.rserver.client()), '<strong>%s</strong>' % self.redis_url,
            repr(urlparse(self.redis_url)), 'is_webhook:%s' % is_webhook,
        ])

        def _get_value(name, key):
            return self.get(name, key).decode()

        def _get_value_cls(key, value):
            if _RES_PREFIX in key:
                return ' result'
            if _TEXT_PREFIX in key:
                return ' text'
            if value.isdigit() or value.startswith('-'):
                x = int(value)
                return x < 0 and ' negative' or x == 0 and ' zero' or ' positive'
            return ''

        def _add_output(output, cls, keys, cols=None):
            values = dict([(key, _get_value(name, key)) for key in keys])

            def _add(i, key, mode=0):
                if mode == 0:
                    if cols and i > 0 and i%cols == 0:
                        output.append('</tr><tr>')
                    output.append('<td class="data%s">%s: <div class="value">%s</div></td>' % (
                        _get_value_cls(key, values[key]), 
                        key, 
                        values[key]
                        ))
                else:
                    output.append('<tr><td class="data%s">%s: <div class="value">%s</div></td></tr>' % (
                        _get_value_cls(key, values[key]), 
                        key, 
                        values[key]
                        ))
                    

            if not keys:
                return

            res, text = [], []
            output.append('<table class="%s">' % cls)
            output.append('<tr>')
            for i, key in enumerate(keys):
                if _RES_PREFIX in key:
                    res.append(key)
                    continue
                if _TEXT_PREFIX in key:
                    text.append(key)
                    continue
                _add(i, key)
            output.append('</tr>')
            output.append('</table>')

            if not res:
                return

            output.append('<table class="%s">' % cls)
            output.append('<tr>')
            for i, key in enumerate(res):
                _add(i, key)
            output.append('</tr>')
            output.append('</table>')

            if not text:
                return

            output.append('<table class="%s">' % cls)
            output.append('<tr>')
            for i, key in enumerate(text):
                _add(i, key, mode=1)
            output.append('</tr>')
            output.append('</table>')

        def _sorted_keys(keys, key):
            def _skey(x):
                return ('00'+str(x))[-2:]
            def _question(x):
                k = x.split('.')[1]
                return '.R' in x and '99%s' % k or ('00'+k)[-2:]
            subkeys = [x[1] for x in sorted([('%s.%s' % (key[0], _question(x)), x)
                for x in keys if x.startswith(key[1])])]
            return subkeys

        if self.rserver.client():
            names = [x.decode() for x in self.rserver.keys('*')]
            html['header'] = '<div class="server">names:[%s]</div>' % ', '.join(['<span>%s</span>' % x for x in names])

            outputs = []

            for name in names:
                output = []
                output.append('<div class="chat">%s:</div>' % name)

                try:
                    data = self.getall(name)
                    keys = [x.decode() for x in data.keys()]
                except:
                    output.append('error:%s' % name)
                    continue

                for cls, caption, group in groups:
                    if caption:
                        output.append('<h2>%s</h2>' % caption)
                    if not group:
                        _add_output(output, cls, sorted(keys), cols=15)
                    elif isIterable(group):
                        for key in group:
                            if isIterable(key):
                                subkeys = _sorted_keys(keys, key)
                            else:
                                subkeys = [x[1] for x in sorted([(x, x) for x in keys if x.startswith(key)])]
                            _add_output(output, cls, subkeys, cols=25)
                            for x in subkeys:
                                keys.remove(x)

                outputs.append('<div class="person %s">%s</div>' % (backgrounds[bid], ''.join(output)))

                bid = bid < len(backgrounds)-1 and bid+1 or 0

            html['content'] = ''.join(outputs)

        return _DEBUG_HTML % html

    def set_lang(self, name, value):
        self.set(name, 'lang', value)

    def get_lang(self, name):
        x = self.get(name, 'lang')
        lang = x and x.decode() or DEFAULT_LANGUAGE
        return lang #get_locale(lang)


def activate_storage(**kw):
    command = kw.get('command', '')
    query_id = kw.get('query_id', None)
    person = kw.get('person', None)

    storage = RedisStorage()
    storage._init_state(command, query_id, person)

    return storage

def deactivate_storage(storage):
    del storage
