# -*- coding: utf-8 -*-

import re
import time
from copy import deepcopy
import random

from config import (
     IsDebug, IsDeepDebug, IsTrace, IsPrintExceptions, IsWithPrintErrors, IsRandomScores,
     errorlog, print_to, print_exception,
    )

from app.settings import DEFAULT_LANGUAGE, DEFAULT_PARSE_MODE, NO_RESULTS
from app.dialogs.start import help
from app.handlers import *

_is_random_scores = IsRandomScores

# --------------------------------
# Измерение уровня депрессии (BDI)
# --------------------------------

_TEST_NAME = 'T3'
_QCOUNT = 21

_QUESTIONS = {
    'ru': (
"""
1. Вопрос 1
""",
"""
2. Вопрос 2
""",
"""
3. Вопрос 3
""",
"""
4. Вопрос 4
""",
"""
5. Вопрос 5
""",
"""
6. Вопрос 6
""",
"""
7. Вопрос 7
""",
"""
8. Вопрос 8
""",
"""
9. Вопрос 9
""",
"""
10. Вопрос 10
""",
"""
11. Вопрос 11
""",
"""
12. Вопрос 12
""",
"""
13. Вопрос 13
""",
"""
14. Вопрос 14
""",
"""
15. Вопрос 15
""",
"""
16. Вопрос 16
""",
"""
17. Вопрос 17
""",
"""
18. Вопрос 18
""",
"""
19. Вопрос 19
""",
"""
20. Вопрос 20
""",
"""
21. Вопрос 21
""",
), 
    'uk': (
"""
1. Запитання 1
""",
"""
2. Запитання 2
""",
"""
3. Запитання 3
""",
"""
4. Запитання 4
""",
"""
5. Запитання 5
""",
"""
6. Запитання 6
""",
"""
7. Запитання 7
""",
"""
8. Запитання 8
""",
"""
9. Запитання 9
""",
"""
10. Запитання 10
""",
"""
11. Запитання 11
""",
"""
12. Запитання 12
""",
"""
13. Запитання 13
""",
"""
14. Запитання 14
""",
"""
15. Запитання 15
""",
"""
16. Запитання 16
""",
"""
17. Запитання 17
""",
"""
18. Запитання 18
""",
"""
19. Запитання 19
""",
"""
20. Запитання 20
""",
"""
21. Запитання 21.
""",
),
}

_scores_numbers = 'ABCD'

_SCORES = {
    'ru': [
        (
            ('я не грустный', '%s.1:0',),
            ('я грустный', '%s.1:1',),
            ('я постоянно грустный и не могу выйти из этого состояния', '%s.1:2',),
            ('я настолько печален, что не могу выдержать это состояние', '%s.1:3',),
        ),
        (
            ('я не доведен до отчаяния, особенно когда думаю о будущем', '%s.2:0',),
            ('я чувствую отчаяние, когда думаю о будущем', '%s.2:1',),
            ('я чувствую, что в будущем меня не ждет ничего хорошего', '%s.2:2',),
            ('я чувствую, что будущее безнадежно и ничего уже не может измениться к лучшему', '%s.2:3',),
        ),
        (
            ('я не чувствую себя неудачником', '%s.3:0',),
            ('я чувствую, что потерплю неудачу чаще, чем среднестатистический человек', '%s.3:1',),
            ('когда я оглядываюсь на свою жизнь, я вижу только множество неудач', '%s.3:2',),
            ('неудачник', '%s.3:3',),
        ),
        (
            ('я получаю удовольствие от тех же вещей, что и в прошлом', '%s.4:0',),
            ('я не получаю удовольствие от тех вещей, от которых получал удовольствие в прошлом', '%s.4:1',),
            ('я уже реально ничем не доволен', '%s.4:2',),
            ('я совершенно не доволен, и меня ничто уже не интересует', '%s.4:3',),
        ),
        (
            ('я не чувствую себя особенно виноватым', '%s.5:0',),
            ('некоторое время я чувствую себя виновным', '%s.5:1',),
            ('я чувствую себя виновным большую часть времени', '%s.5:2',),
            ('я все время чувствую себя виновным', '%s.5:3',),
        ),
        (
            ('я не чувствую, что меня наказали', '%s.6:0',),
            ('я чувствую, что могу быть наказанным', '%s.6:1',),
            ('я жду, что буду наказан', '%s.6:2',),
            ('я чувствую, что наказан', '%s.6:3',),
        ),
        (
            ('я не чувствую разочарование в себе', '%s.7:0',),
            ('я разочарован в себе', '%s.7:1',),
            ('я себе противен', '%s.7:2',),
            ('я ненавижу себя', '%s.7:3',),
        ),
        (
            ('я не чувствую себя хуже любого', '%s.8:0',),
            ('я критичен по отношению к себе за ошибки и слабость', '%s.8:1',),
            ('я все время виню себя в своих недостатках', '%s.8:2',),
            ('я виню себя за все плохое, что происходит', '%s.8:3',),
        ),
        (
            ('у меня нет мыслей о самоубийстве', '%s.9:0',),
            ('у меня есть мысли о самоубийстве, но я этого никогда не сделаю', '%s.9:1',),
            ('я хотел бы покончить с собой', '%s.9:2',),
            ('я бы покончил с собой, если бы появилась такая возможность', '%s.9:3',)
        ),
        (
            ('я не плачу больше, чем обычно', '%s.10:0',),
            ('я плачу сейчас больше, чем в прошлом', '%s.10:1',),
            ('сейчас я плачу все время', '%s.10:2',),
            ('в прошлом я мог плакать, но сейчас не могу, хотя очень хочу', '%s.10:3',),
        ),
        (
            ('я не нервничаю больше, чем обычно', '%s.11:0',),
            ('я раздражаюсь легче, чем когда-либо', '%s.11:1',),
            ('я нервничаю все время', '%s.11:2',),
            ('я даже не раздражаюсь теперь от тех вещей, которые когда-то меня раздражали', '%s.11:3',),
        ),
        (
            ('я не потерял интерес к другим людям', '%s.12:0',),
            ('теперь я меньше интересуюсь другими людьми', '%s.12:1',),
            ('я в значительной степени потерял интерес к другим людям', '%s.12:2',),
            ('я потерял всякий интерес к другим людям', '%s.12:3',),
        ),
        (
            ('я принимаю решение с той же легкостью, как всегда', '%s.13:0',),
            ('я откладываю принятие решений чаще, чем обычно', '%s.13:1',),
            ('мне труднее принимать решения, чем обычно', '%s.13:2',),
            ('я совершенно не могу принимать решения', '%s.13:3',),
        ),
        (
            ('я не чувствую, что выгляжу хуже, чем обычно', '%s.14:0',),
            ('я чувствую, что выгляжу старше своих лет и неприглядный', '%s.14:1',),
            ('я чувствую, что в моей внешности постоянно происходят изменения, которые делают меня непривлекательным', '%s.14:2',),
            ('я считаю, что выгляжу безобразным', '%s.14:3',),
        ),
        (
            ('я могу сейчас работать так же, как и раньше', '%s.15:0',),
            ('мне приходится специально напрягаться, чтобы начать что-то делать', '%s.15:1',),
            ('мне приходится себя заставлять, чтобы что-то сделать', '%s.15:2',),
            ('я не могу теперь делать вообще никакой работы', '%s.15:3',),
        ),
        (
            ('я могу сейчас спать, как всегда', '%s.16:0',),
            ('я сплю сейчас хуже, чем всегда', '%s.16:1',),
            ('я просыпаюсь на час-два раньше обычного, и мне трудно заснуть снова', '%s.16:2',),
            ('я просыпаюсь на несколько часов раньше обычного, и не могу заснуть снова', '%s.16:3',),
        ),
        (
            ('я не устаю сейчас больше, чем обычно', '%s.17:0',),
            ('я устаю быстрее, чем обычно', '%s.17:1',),
            ('я устаю теперь от всего, что бы я не делал', '%s.17:2',),
            ('я слишком устал, чтобы выполнять любую работу', '%s.17:3',),
        ),
        (
            ('меня аппетит как обычно', '%s.18:0',),
            ('мой аппетит хуже, чем был раньше', '%s.18:1',),
            ('мой аппетит гораздо хуже, чем был раньше', '%s.18:2',),
            ('у меня совершенно нет аппетита', '%s.18:3',),
        ),
        (
            ('я не потерял вес тела, разве что совсем немного', '%s.19:0',),
            ('я потерял вес тела более 2-2,5 кг', '%s.19:1',),
            ('я потерял вес тела более 4-4,5 кг', '%s.19:2',),
            ('я потерял вес тела более 6,5-7 кг', '%s.19:3',),
        ),
        (
            ('я не обеспокоен своим здоровьем больше, чем обычно', '%s.20:0',),
            ('я обеспокоен физическими проблемами, такими как боль, расстройство желудка, запоры', '%s.20:1',),
            ('я настолько обеспокоен проблемами своего физического здоровья, не могу думать о какой-либо другие вещи', '%s.20:2',),
            ('я настолько обеспокоен проблемами своего физического здоровья, не могу думать вообще ни о чем', '%s.20:3',),
        ),
        (
            ('я не заметил никаких изменений в своем отношении к сексу', '%s.21:0',),
            ('я меньше заинтересован в сексе, чем обычно', '%s.21:1',),
            ('я гораздо меньше заинтересован в сексе сейчас', '%s.21:2',),
            ('я полностью потерял интерес к сексу', '%s.21:3',),
        ),
    ],
    'uk': [
        (
            ('я не сумний', '%s.1:0',),
            ('я сумний', '%s.1:1',),
            ('я постійно сумний і не можу вийти з цього стану', '%s.1:2',),
            ('я настільки сумний, що не можу витримати цей стан', '%s.1:3',),
        ),
        (
            ('я не доведений до відчаю, особливо коли думаю про майбутнє', '%s.2:0',),
            ('я відчуваю розпач, коли думаю про майбутнє', '%s.2:1',),
            ('я відчуваю, що в майбутньому на мене не чекає нічого доброго', '%s.2:2',),
            ('я відчуваю, що майбутнє безнадійне і що нічого вже не може змінитися на краще', '%s.2:3',),
        ),
        (
            ('я не відчуваю себе невдахою', '%s.3:0',),
            ('я відчуваю, що зазнаю невдачі частіше, ніж середньостатистична людина', '%s.3:1',),
            ('коли я оглядаюся на своє життя, я бачу лише безліч невдач', '%s.3:2',),
            ('я відчуваю, що я – невдаха', '%s.3:3',),
        ),
        (
            ('я отримую задоволення від тих же речей, що і в минулому', '%s.4:0',),
            ('я не отримую задоволення від тих речей, від яких отримував задоволення в минулому', '%s.4:1',),
            ('я вже реально нічим не задоволений', '%s.4:2',),
            ('я абсолютно не задоволений, і мене ніщо вже не цікавить', '%s.4:3',),
        ),
        (
            ('я не відчуваю себе особливо винним', '%s.5:0',),
            ('якийсь час я відчуваю себе винним', '%s.5:1',),
            ('я відчуваю себе винним переважну частину часу', '%s.5:2',),
            ('я весь час відчуваю себе винним', '%s.5:3',),
        ),
        (
            ('я не відчуваю, що мене покарано', '%s.6:0',),
            ('я відчуваю, що можу бути покараним', '%s.6:1',),
            ('я чекаю, що буду покараним', '%s.6:2',),
            ('я відчуваю, що покараний', '%s.6:3',),
        ),
        (
            ('я не відчуваю розчарування у собі', '%s.7:0',),
            ('я розчарований у собі', '%s.7:1',),
            ('я собі огидний', '%s.7:2',),
            ('я ненавиджу себе', '%s.7:3',),
        ),
        (
            ('я не відчуваю себе гіршим за будь-кого', '%s.8:0',),
            ('я критичний стосовно себе за свої помилки і слабкість', '%s.8:1',),
            ('я весь час звинувачую себе у своїх недоліках', '%s.8:2',),
            ('я звинувачую себе за все погане, що відбувається', '%s.8:3',),
        ),
        (
            ('у мене немає думок про самогубство', '%s.9:0',),
            ('у мене є думки про самогубство, але я цього ніколи не зроблю', '%s.9:1',),
            ('я хотів би накласти на себе руки', '%s.9:2',),
            ('я би наклав на себе руки, якби з’явилася така можливість', '%s.9:3',)
        ),
        (
            ('я не плачу більше, ніж зазвичай', '%s.10:0',),
            ('я плачу зараз більше, ніж у минулому', '%s.10:1',),
            ('зараз я плачу увесь час', '%s.10:2',),
            ('у минулому я міг плакати, але зараз не можу, хоча дуже хочу', '%s.10:3',),
        ),
        (
            ('я не нервую більше, ніж зазвичай', '%s.11:0',),
            ('я дратуюся легше, ніж будь-коли', '%s.11:1',),
            ('я нервую увесь час', '%s.11:2',),
            ('я навіть не дратуюся тепер від тих речей, які колись мене дратували', '%s.11:3',),
        ),
        (
            ('я не втратив цікавість до інших людей', '%s.12:0',),
            ('тепер я менше цікавлюся іншими людьми', '%s.12:1',),
            ('я значною мірою втратив цікавість до інших людей', '%s.12:2',),
            ('я втратив будь-яку цікавість до інших людей', '%s.12:3',),
        ),
        (
            ('я приймаю рішення  з тією ж легкістю, як завжди', '%s.13:0',),
            ('я відкладаю прийняття рішень частіше, ніж зазвичай', '%s.13:1',),
            ('мені важче приймати рішення, ніж зазвичай', '%s.13:2',),
            ('я абсолютно не можу приймати рішення', '%s.13:3',),
        ),
        (
            ('я не відчуваю, що виглядаю гірше, ніж зазвичай', '%s.14:0',),
            ('я відчуваю, що виглядаю доросліше за свої роки і непривабливий', '%s.14:1',),
            ('я відчуваю, що в моїй зовнішності постійно відбуваються зміни, які роблять мене непривабливим', '%s.14:2',),
            ('я вважаю, що виглядаю потворним', '%s.14:3',),
        ),
        (
            ('я можу зараз працювати так само, як і раніше', '%s.15:0',),
            ('мені доводиться спеціально напружуватися, щоб почати щось робити', '%s.15:1',),
            ('мені доводиться себе змушувати, щоб щось зробити', '%s.15:2',),
            ('я не можу тепер виконувати взагалі ніякої роботи', '%s.15:3',),
        ),
        (
            ('я можу зараз спати, як завжди', '%s.16:0',),
            ('я сплю зараз гірше, ніж завжди', '%s.16:1',),
            ('я прокидаюся на годину-дві раніше звичайного, і мені важко заснути знову', '%s.16:2',),
            ('я прокидаюся на декілька годин раніше звичайного, і не можу заснути знову', '%s.16:3',),
        ),
        (
            ('я не втомлююся зараз більше, ніж зазвичай', '%s.17:0',),
            ('я втомлююся швидше, ніж завжди', '%s.17:1',),
            ('я втомлююся тепер від всього, що б я не робив', '%s.17:2',),
            ('я дуже втомився, щоб виконувати будь-яку роботу', '%s.17:3',),
        ),
        (
            ('мене апетит як зазвичай', '%s.18:0',),
            ('мій апетит гірше, ніж був раніше', '%s.18:1',),
            ('мій апетит набагато гірше, ніж був раніше', '%s.18:2',),
            ('у мене абсолютно немає апетиту', '%s.18:3',),
        ),
        (
            ('я не втратив вагу тіла, хіба що зовсім небагато', '%s.19:0',),
            ('я втратив вагу тіла понад 2-2,5 кг', '%s.19:1',),
            ('я втратив вагу тіла понад 4-4,5 кг', '%s.19:2',),
            ('я втратив вагу тіла понад 6,5-7 кг', '%s.19:3',),
        ),
        (
            ('я не стурбований своїм здоров’ям більше, ніж зазвичай', '%s.20:0',),
            ('я стурбований фізичними проблемами, такими як біль, розлад шлунку, запори', '%s.20:1',),
            ('я настільки стурбований проблемами свого фізичного здоров’я, що не можу думати про будь-які інші речі', '%s.20:2',),
            ('я настільки стурбований проблемами свого фізичного здоров’я, що не можу думати взагалі ні про що', '%s.20:3',),
        ),
        (
            ('я не помітив ніяких змін у своєму ставленні до сексу', '%s.21:0',),
            ('я менше зацікавлений в сексі, ніж зазвичай', '%s.21:1',),
            ('я набагато менше зацікавлений в сексі зараз', '%s.21:2',),
            ('я повністю втратив цікавість до сексу', '%s.21:3',),
        ),
    ],
}

_RESULTS = {
    'ru' : (
        ( 9, 'Симптомы депрессии отсутствуют'), 
        (18, 'Обнаружено низкий уровень депрессии'), 
        (29, 'Выявлен средний уровень депрессии'), 
        (63, 'Выявлено высокий уровень депрессии, клиническое проявление. Настоятельно рекомендуется обратиться к специалисту'), 
    ),
    'uk' : (
        ( 9, 'Симптоми депресії відсутні'), 
        (18, 'Виявлено низький рівень депресії'), 
        (29, 'Виявлено середній рівень депресії'), 
        (63, 'Виявлено високий рівень депресії, клінічне проявлення. Наполегливо рекомендується звернутися до фахівця'), 
    ),
}

_WARNINGS = {
    'ru': (
"""
Внимание, предоставленные данные выглядят недостоверными, рекомендуется быть более искренним в ответах или обратиться к специалисту!
""",
), 
    'uk': (
"""
Увага, надані відповіді видаються не надто достовірними; рекомендується бути більш щирим у відповідях або звернутися до фахівця!
""",
),
}

_FINISH = {
    'ru': (
"""
Завершение диалога.
""",
"""
Мы благодарим Вас за Ваши ответы.
Желаем Вам крепкого здоровья, и всего Вам доброго!
""",
), 
    'uk': (
"""
Завершення діалогу.
""",
"""
Ми дякуємо Вам за Ваші відповіді.
Бажаємо Вам міцного здоров'я, і всього Вам доброго!
""",
),
}

_results = {}


def total_questions():
    return _QCOUNT

def get_question(i, lang, no_eof=None):
    x = _QUESTIONS[lang][i].strip()
    s = '%s.%s:' % (_TEST_NAME, x[-1] == '.' and x[:-1] or x)
    return no_eof and re.sub(r'\n', ' ', s) or s

def get_finish(storage, name, i, lang, no_eof=None):
    nic = storage.get(name, 'nic', with_decode=True)
    s = '%s%s' % (nic and '%s!\n\n' % nic or _FINISH[lang][0], _FINISH[lang][i].strip())
    return no_eof and re.sub(r'\n', ' ', s) or s

def get_answers(question, lang, no_eof=None):
    scores = list(_SCORES[lang][question])

    if _is_random_scores:
        random.shuffle(scores)

    answers = []
    buttons = []
    for i, x in enumerate(scores):
        s, b = x[0], x[1].split(':')[1]
        n = _scores_numbers[i]
        q = '%s.%s:%s' % (_TEST_NAME, question+1, b)
        answers.append('%s) %s' % (n, s))
        buttons.append((n, q))

    if _is_random_scores:
        buttons = sorted(buttons)

    return '\n'.join(answers), buttons

def get_result(storage, name, lang, mode=None):
    global _results

    res = ''
    data = storage.getall(name)
    results = _RESULTS[lang]

    x = 0

    for n in range(0, 21):
        key = ('%s.%s' % (_TEST_NAME, n+1)).encode()
        x += int(data.get(key, 0))
    c = ''
    for i, item in enumerate(results):
        if x <= item[0]:
            c = results[i][1]
            res = (x, '<b>%s</b>' % c)
            break

    _results['value'] = (x, c)

    return res

def answer(bot, message, command, data=None, logger=None, question=None, **kw):
    """
        Make the step's answer
    """
    lang = kw.get('lang') or DEFAULT_LANGUAGE
    storage = kw.get('storage')
    name = kw.get('name')

    is_run = True

    if question == 21 or (IsDebug and question > 0 and question%10 == 0):
        text = '[%s] %s.' % get_result(storage, name, lang,)
        bot.send_message(message.chat.id, text, parse_mode=DEFAULT_PARSE_MODE)
        is_run = question < 21

        if is_run:
            time.sleep(3)

    if is_run:
        answers, buttons = get_answers(question, lang)
        text = '%s\n\n%s' % (get_question(question, lang), answers)
        send_inline_keyboard(bot, message, buttons, text)

    elif 'query_id' in kw:
        bot.answer_callback_query(
            kw['query_id'],
            text=get_finish(storage, name, 1, lang),
            show_alert=True
            )

        if 'value' in _results:
            value, param = _results['value']
            storage.set(name, '%s.R' % _TEST_NAME, value)
            storage.set(name, '%s.T' % _TEST_NAME, '%s:%s' % (param, value), with_encode=True)

        time.sleep(3)

        help(bot, message, logger=logger, mode=1, **kw)

## -------------------------- ##

def lines(text):
    is_print_questions = False
    questions = []
    n = 0
    for line in text.split('\n'):
        if not line:
            continue
        if line.startswith('T3'):
            questions.append(line)
            print('%s),\n%s(' % (' '*8, ' '*8,))
            n += 1
            continue
        m = re.match(r'(- )(.*)(\(\d+\))', line)
        if not m:
            continue
        b = int(re.sub(r'[\(\)]', r'', m.group(3)))
        s = m.group(2).strip()
        print("%s('%s', '%s.%s:%s')," % (' '*12, s, _TEST_NAME, n, b))
    if is_print_questions:
        for q in questions:
            print('"""\n%s\n""",' % q)

def check(data, key, res):
    s = 0
    for k in data[key].keys():
        #print(k)
        q = k.split('.')[1]
        if not q.isdigit():
            continue
        #print(q)
        if not res or int(q) in res:
            s += int(data[key][k])
    return s

def selftest(data, lang, with_print=None):
    key = _TEST_NAME
    params = ('1',)

    out = ''
    r = 0
    for k in sorted(params):
        x = check(data, key, None)
        if with_print:
            print(x)
        r += x

    rp = '%s.R' % key
    if rp in data[key]:
        x = int(data[key].get(rp, '0'))
        if r == x:
            out = 'OK'
        else:
            out = 'Error %s [%s:%s]' % (rp, r, x)
            if with_print or IsWithPrintErrors:
                print(key, out)

    return out or NO_RESULTS