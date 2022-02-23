# -*- coding: utf-8 -*-

import re
from copy import deepcopy

from app.settings import DEFAULT_LANGUAGE
from app.handlers import *

_QUESTIONS = {
    'ru': (
"""
Полагаю, все клинические симптомы обусловлены стрессом
""",
"""
Жалобы на физическое здоровье на данный момент отсутствуют
""",
"""
Жалобы есть, но связаны с основным медицинским диагнозом
""",
"""
Раздражительность
""",
"""
Растерянность
""",
"""
Психомоторное возбуждение
""",
"""
Снижение концентрации внимания
""",
"""
Ухудшение памяти
""",
"""
Наличие негативных мыслей
""",
"""
Слабость
""",
"""
Заторможенность реакции
""",
"""
Нарушения сна
""",
"""
Агрессивность, которую я могу контролировать
""",
"""
Агрессивность, которую мне трудно контролировать
""",
"""
Наличие голосов в голове
""",
"""
Суицидальные мысли
""",
"""
Аутоагрессия (желание наказать себя)
""",
"""
Плаксивость
""",
"""
Фантомные боли
""",
"""
Ощущение постоянно нарастающей эмоциональной усталости
""",
"""
Болевые симптомы
""",
"""
Преимущественно пониженное настроение, угнетённость
""",
"""
Чрезмерная реакция на внешние стимулы
""",
), 
    'uk': (
"""
Вважаю, всі клінічні симптоми обумовлені стресом
""",
"""
Скарги на фізичне здоров'я на даний момент відсутні
""",
"""
Скарги є, але пов'язані з основним медичним діагнозом
""",
"""
Дратівливість
""",
"""
Розгубленість
""",
"""
Психомоторне збудження
""",
"""
Зниження концентрації уваги
""",
"""
Погіршення пам'яті
""",
"""
Наявність негативних думок
""",
"""
Слабкість
""",
"""
Загальмованість реакції
""",
"""
Порушення сну
""",
"""
Агресивність, яку я можу контролювати
""",
"""
Агресивність, яку мені важко контролювати
""",
"""
Наявність голосів в голові
""",
"""
Суїцидальні думки
""",
"""
Аутоагресія (бажання покарати себе)
""",
"""
Плаксивість
""",
"""
Фантомні болі
""",
"""
Відчуття постійно наростаючим емоційним втоми
""",
"""
Больові симптоми
""",
"""
Переважно погіршення настрою, пригніченість
""",
"""
Надмірна реакція на зовнішні стимули
""",
),
}

_HEADERS = {
    'ru': 
"""
13.%s. Какие жалобы у Вас есть на собственное физическое здоровье?
""",
    'uk': 
"""
13.%s. Які скарги у Вас є на власне фізичне здоров'я? 
""",
}

_GRIEVANCE = {
    'ru': [['Да', 'grievance.%s:yes'], ['Нет', 'grievance.%s:no']],
    'uk': [['Так', 'grievance.%s:yes'], ['Ні', 'grievance.%s:no']], 
}

def get_question(i, lang, no_eof=None):
    q = i+1
    s = _QUESTIONS[lang][i].strip()
    text = '%s\n%s.' % (_HEADERS[lang] % q, s)
    answers = deepcopy(_GRIEVANCE[lang])
    for i, x in enumerate(answers):
        answers[i][1] = answers[i][1] % q
    return answers, no_eof and re.sub(r'\n', ' ', text) or text

def answer(bot, message, command, data=None, logger=None, question=None, **kw):
    """
        Make the step's answer
    """
    lang = kw.get('lang') or DEFAULT_LANGUAGE
    answers, text = get_question(question, lang)
    send_inline_keyboard(bot, message, answers, text)