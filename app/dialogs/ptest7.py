# -*- coding: utf-8 -*-

import re
import time
from copy import deepcopy

from config import (
     IsDebug, IsDeepDebug, IsTrace, IsPrintExceptions, IsWithPrintErrors, IsWithExtra, 
     errorlog, print_to, print_exception,
    )

from app.settings import DEFAULT_LANGUAGE, DEFAULT_PARSE_MODE, NO_RESULTS
from app.dialogs.start import help
from app.handlers import *

# Ответ "Не знаю"
_with_extra = IsWithExtra

# --------------------------------------
# Определение характеристик темперамента
# --------------------------------------

_TEST_NAME = 'T7'
_QCOUNT = 48

_QUESTIONS = {
    'ru': (
"""
1. Любите ли вы часто бывать в компании?
""",
"""
2. Вы избегаете иметь вещи, которые ненадёжны, непрочны, хотя и красивые?
""",
"""
3. Часто ли у вас бывают подъёмы и спады настроения?
""",
"""
4. Во время беседы вы очень быстро говорите?
""",
"""
5. Вам нравится работа, требующая полного напряжения сил и способностей?
""",
"""
6. Бывает ли, что вы передаёте слухи?
""",
"""
7. Считаете ли вы себя человеком очень весёлым и жизнерадостным?
""",
"""
8. Вы привыкаете к определённой одежде, её цвету и покрою, так что неохотно меняете её на что-нибудь другое?
""",
"""
9. Часто ли вы чувствуете, что нуждаетесь в людях, которые вас понимают, могут одобрить и утешить?
""",
"""
10. У вас очень быстрый почерк?
""",
"""
11. Ищете вы сами себе работу, занятие, хотя можно было бы и отдыхать?
""",
"""
12. Бывает ли так, что вы не выполняете своих обещаний?
""",
"""
13. У вас много очень хороших друзей?
""",
"""
14. Трудно ли вам оторваться от дела, которым поглощены, и переключиться на другой?
""",
"""
15. Часто вас мучает чувство вины?
""",
"""
16. Обычно вы ходите очень быстро, независимо от того, спешите или нет?
""",
"""
17. В школе вы бились над трудными задачами до тех пор, пока не решали их?
""",
"""
18. Бывает, что иногда вы рассуждаете хуже, чем обычно?
""",
"""
19. Вам легко найти общий язык с незнакомыми людьми?
""",
"""
20. Часто ли вы планируете, как будете себя вести при встрече, беседе?
""",
"""
21. Вы вспыльчивы и ранимы намёками и шутками над вами?
""",
"""
22. Во время беседы вы обычно жестикулируете?
""",
"""
23. Чаще всего вы просыпаетесь утром свежим и хорошо отдохнувшим?
""",
"""
24. Бывают ли у вас такие мысли, о которых вы не хотели, чтобы о них знали другие?
""",
"""
25. Вы любите подшучивать над другими?
""",
"""
26. Склонны ли вы к тому, чтобы основательно проверить свои мысли, прежде чем сообщать кому-либо?
""",
"""
27. Часто ли вам снятся кошмары?
""",
"""
28. Обычно вы легко запоминаете и усваиваете новый учебный материал?
""",
"""
29. Вы настолько активны, что вам трудно даже несколько часов быть без дела?
""",
"""
30. Бывало, что, разозлившись, вы выходили из себя?
""",
"""
31. Вам трудно внести оживление в довольно скучную компанию?
""",
"""
32. Вы обычно достаточно долго раздумываете, принимая какое-то, даже не очень важное, решение?
""",
"""
33. Вам говорили, что вы принимаете всё слишком близко к сердцу?
""",
"""
34. Вам нравится играть в игры, требующие быстроты и хорошей реакции?
""",
"""
35. Если у вас что-то долго не получается, то, конечно, вы всё же пытаетесь сделать это?
""",
"""
36. Возникало ли у вас, хоть и кратковременно, чувство раздражения к вашим родителям?
""",
"""
37. Считаете ли вы себя открытым и общительным человеком?
""",
"""
38. Обычно вам трудно взяться за новое дело?
""",
"""
39. Беспокоит ли вас чувство, что вы чем-то хуже других?
""",
"""
40. Обычно вам трудно что-то делать с медленными и неторопливыми людьми?
""",
"""
41. В течение дня вы можете долго и продуктивно заниматься чем-либо, не чувствуя усталости?
""",
"""
42. У вас есть привычки, от которых следовало бы избавиться?
""",
"""
43. Вас иногда принимают за человека беззаботного?
""",
"""
44. Считаете ли вы хорошим другом только того, чья симпатия к вам надёжна и проверена?
""",
"""
45. Вас можно рассердить?
""",
"""
46. Во время дискуссии обычно вы быстро находите подходящий ответ?
""",
"""
47. Вы можете заставить себя долго и продуктивно, не отвлекаясь, заниматься чем-нибудь?
""",
"""
48. Бывает ли, что вы говорите о вещах, в которых вовсе не разбираетесь?
""",
), 
    'uk': (
"""
1. Ви любите часто бувати у товаристві?
""",
"""
2. Ви уникаєте мати речі, які ненадійні, неміцні, хоча й красиві?
""",
"""
3. Чи часто у вас бувають підйоми і спади настрою?
""",
"""
4. Під час розмови ви дуже швидко говорите?
""",
"""
5. Вам подобається робота, яка вимагає повного напруження сил та здібностей?
""",
"""
6. Буває, що ви передаєте плітки?
""",
"""
7. Чи вважаєте ви себе людиною дуже веселою та життєрадісною?
""",
"""
8. Ви звикаєте до певного одягу, її кольору та покрою так, що неохоче змінюєте його на який-небудь інший?
""",
"""
9. Чи часто ви відчуваєте, що потребуєте людей, котрі вас розуміють, можуть схвалити й втішити?
""",
"""
10. У вас дуже швидкий почерк?
""",
"""
11. Ви шукаєте самому собі роботу, хоча можна було б і відпочивати?
""",
"""
12. Чи буває так, що ви не виконуєте своїх обіцянок?
""",
"""
13. У вас багато дуже близьких друзів?
""",
"""
14. Чи важко вам відірватися від справи, в яку заглиблені, й перемкнутися на іншу?
""",
"""
15. Чи часто вас турбує почуття провини?
""",
"""
16. Зазвичай ви ходите дуже швидко, незалежно від того, поспішаєте чи ні?
""",
"""
17. В школі ви сиділи над важкими задачами, допоки не розв’язували їх?
""",
"""
18. Чи буває, що іноді ви міркуєте гірше, ніж зазвичай?
""",
"""
19. Вам легко знайти спільну мову з незнайомими людьми?
""",
"""
20. Чи часто ви плануєте, як будете поводитися із незнайомими людьми?
""",
"""
21. Ви запальні й вразливі перед натяками і жартами над собою?
""",
"""
22. Ви зазвичай жестикулюєте під час розмови?
""",
"""
23. Частіше за все ви просинаєтеся вранці свіжим й добре відпочилим?
""",
"""
24. Чи бувають у вас такі думки, про які ви б не хотіли, щоб про них знали інші?
""",
"""
25. Ви любите жартувати над іншими?
""",
"""
26. Чи схильні ви до того, аби ґрунтовно перевірити свої думки, перед тим як повідомляти їх комусь?
""",
"""
27. Чи часто вам сняться нічні жахіття?
""",
"""
28. Зазвичай ви легко запам'ятовуєте і засвоюєте новий навчальний матеріал?
""",
"""
29. Ви настільки активні, що вам важко навіть кілька годин бути без діла?
""",
"""
30. Чи бувало, що, розлютившись, ви виходили з себе?
""",
"""
31. Вам важко пожвавити досить нудне товариство?
""",
"""
32. Ви зазвичай досить довго розмірковуєте, ухвалюючи якесь, навіть не дуже важливе, рішення?
""",
"""
33. Вам казали, що ви приймаєте все занадто близько до серця?
""",
"""
34. Вам подобається грати в ігри, які вимагають швидкості й гарної реакції?
""",
"""
35. Якщо у вас щось довго не виходить, то, звичайно, ви все ж таки спробуєте це зробити?
""",
"""
36. Чи виникало у вас, хоча б тимчасово, почуття роздратування на своїх батьків?
""",
"""
37. Чи вважаєте ви себе відкритою і товариською людиною?
""",
"""
38. Вам зазвичай важко взятися за нову справу?
""",
"""
39. Чи турбує вас відчуття, що ви чимось гірші за інших?
""",
"""
40. Вам зазвичай важко робити щось з повільними й неквапливими людьми?
""",
"""
41. Протягом дня ви можете довго й продуктивно займатися чим-небудь, не відчуваючи втоми?
""",
"""
42. У вас є звички, від яких треба було б відмовитися?
""",
"""
43. Вас іноді приймають за безтурботну людину?
""",
"""
44. Чи вважаєте ви добрим другом лише того, чия симпатія до вас надійна і перевірена?
""",
"""
45. Вас можна розсердити?
""",
"""
46. Під час дискусії ви зазвичай швидко знаходите слушну відповідь?
""",
"""
47. Ви можете змусити себе довго й продуктивно, не відволікаючись, займатися чим-небудь?
""",
"""
48. Чи буває, що ви говорите про речі, в яких не розбираєтеся?
""",
),
}

_ANSWERS = {
    'ru': [['Да', '%s.%s:1'], ['Нет', '%s.%s:-1']],
    'uk': [['Так', '%s.%s:1'], ['Ні', '%s.%s:-1']],
}

_no_ext_questions = (0, 90,)

_EXT_ANSWERS = {
    'ru': [['Не знаю', '%s.%s:0']],
    'uk': [['Не знаю', '%s.%s:0']],
}

_RESULTS = {
    'ru': {
        '0' : (([6, 12, 18, 30, 36, 42, 48], [24, 25], []), ([], [], [23])),
        '1' : (([1, 7, 19, 23, 25, 31, 37], [4, 43], []), ([], [], [2])),
        '2' : (([2, 8, 14, 20, 26, 32, 38, 44], [], []), ([], [37], [19, 46])),
        '3' : (([3, 9, 15, 21, 27, 33, 39, 45], [], []), ([], [], [])),
        '4' : (([4, 10, 16, 22, 28, 34, 40], [17, 29, 37, 46], []), ([], [], [])),
        '5' : (([5, 11, 13, 23, 29, 35, 41], [], [10, 47]), ([], [], [38])),
    },
    'uk': {
        '0' : (([6, 12, 18, 30, 36, 42, 48], [24, 25], []), ([], [], [23])),
        '1' : (([1, 7, 19, 23, 25, 31, 37], [4, 43], []), ([], [], [2])),
        '2' : (([2, 8, 14, 20, 26, 32, 38, 44], [], []), ([], [37], [19, 46])),
        '3' : (([3, 9, 15, 21, 27, 33, 39, 45], [], []), ([], [], [])),
        '4' : (([4, 10, 16, 22, 28, 34, 40], [17, 29, 37, 46], []), ([], [], [])),
        '5' : (([5, 11, 13, 23, 29, 35, 41], [], [10, 47]), ([], [], [38])),
    },
}

_CONCLUSIONS = {
    'ru' : {
        '0' : ('Искренность', [(7, 'Низкая искренность (ответы ненадёжные)'), (12, 'Средняя искренность'), (26, 'Высокая искренность')]),
        '1' : ('Экстраверсия', [(6, 'Очень высокая интроверсия'), (11, 'Высокая интроверсия'), (13, 'Средняя интроверсия'), (16, 'Средняя экстраверсия'), (21, 'Высокая экстраверсия'), (26, 'Очень высокая экстраверсия')]),
        '2' : ('Ригидность', [(2, 'Очень высокая пластичность'), (6, 'Высокая пластичность'), (8, 'Средняя пластичность'), (11, 'Средняя ригидность'), (15, 'Высокая ригидность'), (28, 'Очень высокая ригидность')]),
        '3' : ('Эмоциональная возбудимость', [(3, 'Очень высокая эмоциональная уравновешенность'), (7, 'Высокая эмоциональная уравновешенность'), (12, 'Средняя эмоциональная уравновешенность'), (13, 'Средняя эмоциональная возбудимость'), (17, 'Высокая эмоциональная возбудимость'), (24, 'Очень высокая эмоциональная возбудимость')]),
        '4' : ('Темп реакции', [(4, 'Очень медленный темп реакции'), (8, 'Медленный темп реакции'), (13, 'Средний темп реакции'), (19, 'Высокий темп реакции'), (29, 'Очень высокий темп реакции')]),
        '5' : ('Активность', [(8, 'Очень низкая активность'), (13, 'Низкая активность'), (20, 'Средняя активность'), (23, 'Высокая активность'), (24, 'Очень высокая активность')]),
    },
    'uk' : {
        '0' : ('Щирість', [(7, 'Низька щирість (відповіді ненадійні)'), (12, 'Середня щирість'), (26, 'Висока щирість')]),
        '1' : ('Екстраверсія', [(6, 'Дуже висока інтроверсія'), (11, 'Висока інтроверсія'), (13, 'Середня інтроверсія'), (16, 'Середня екстраверсія'), (21, 'Висока екстраверсія'), (26, 'Дуже висока екстраверсія')]),
        '2' : ('Ригідність', [(2, 'Дуже висока пластичність'), (6, 'Висока пластичність'), (8, 'Середня пластичність'), (11, 'Середня ригідність'), (15, 'Висока ригідність'), (28, 'Дуже висока ригідність')]),
        '3' : ('Емоційна збуджуваність', [(3, 'Дуже висока емоційна врівноваженість'), (7, 'Висока емоційна врівноваженість'), (12, 'Середня емоційна врівноваженість'), (13, 'Середня емоційна збуджуваність'), (17, 'Висока емоційна збуджуваність'), (24, 'Дуже висока емоційна збуджуваність')]),
        '4' : ('Темп реакції', [(4, 'Дуже повільний темп реакції'), (8, 'Повільний темп реакції'), (13, 'Середній темп реакції'), (19, 'Високий темп реакції'), (29, 'Дуже високий темп реакції')]),
        '5' : ('Активність', [(8, 'Дуже низька активність'), (13, 'Низька активність'), (20, 'Середня активність'), (23, 'Висока активність'), (24, 'Дуже висока активність')]),
    },
}

_HEADERS = {
    'ru': 
"""
Ответьте на каждый вопрос «да» или «нет». Не следует тратить много времени на обдумывание вопросов. Дайте ответ, который первым приходит в голову. Отвечайте на все вопросы подряд, ничего не пропуская. Чем искреннее вы это сделаете, тем точнее и правильнее сможете изучить свой темперамент.
""",
    'uk': 
"""
На кожне запитання дайте відповідь "так" чи "ні". Не варто витрачати багато часу на обмірковування запитань. Дайте відповідь, яка першою спаде на думку. Відповідайте на всі запитання по черзі, нічого не пропускаючи. Що більш відверто ви це зробите, то точніше і вірніше ви зможете вивчити свій темперамент.
""",
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
    s = '%s.%s' % (_TEST_NAME, x[-1] == '.' and x[:-1] or x)
    return no_eof and re.sub(r'\n', ' ', s) or s

def get_header(lang, no_eof=None):
    s = '<b>%s</b>' % _HEADERS[lang].strip()
    return no_eof and re.sub(r'\n', ' ', s) or s

def get_finish(storage, name, i, lang, no_eof=None):
    nic = storage.get(name, 'nic', with_decode=True)
    s = '%s%s' % (nic and '%s!\n\n' % nic or _FINISH[lang][0], _FINISH[lang][i].strip())
    return no_eof and re.sub(r'\n', ' ', s) or s

def get_result(storage, name, lang, mode=None):
    global _results

    res = ''
    data = storage.getall(name)
    results = _RESULTS[lang]
    conclusions = _CONCLUSIONS[lang]

    if mode == 1:
        keys = sorted([x for x in results.keys() if x[0].isdigit()])
    else:
        keys = sorted([x for x in results.keys() if x[0] in 'T'])

    cs, px = {}, {}

    for p in keys:
        # p: ключ параметра: LF или 0,1...
        x = 0
        for i in range(0, 2):
            # i=0: группа "Да"
            # i=1: группа "Нет"
            for k, sc in enumerate(results[p][i]):
                # k: номер группы 0,1,2
                # sc: номера вопросов (3 группы)
                # score: баллы за ответ на вопрос
                score = k == 2 and 1 or k == 1 and 2 or 3
                for n in sc:
                    # n: номер вопроса
                    key = ('%s.%s' % (_TEST_NAME, n)).encode()
                    v = int(data.get(key, 0))
                    x += i == 0 and v > 0 and score or i == 1 and v < 0 and score or 0

        _results[p] = [x, '...']

        if mode == 1:
            px[p] = x
            c = ''
            # name: наименование параметра
            # conclusion: характеристика (группа ответов)
            name, conclusion = conclusions[p]
            for i, item in enumerate(conclusion):
                # item: граничное значение параметра
                if x <= item[0]:
                    # c: итоговая оценка по параметру
                    c = item[1]
                    _results[p][1] = c
                    break
            # res: текст результата
            res += '%s. %s: [%s] <b>%s</b>\n' % (p, name, x, c)
        else:
            if x < 8:
                return True

    if mode == 1:
        return res.strip()

def answer(bot, message, command, data=None, logger=None, question=None, **kw):
    """
        Make the step's answer
    """
    lang = kw.get('lang') or DEFAULT_LANGUAGE
    storage = kw.get('storage')
    name = kw.get('name')

    is_run = True

    if question == 0:
        text = get_header(lang)
        bot.send_message(message.chat.id, text, parse_mode=DEFAULT_PARSE_MODE)

    if question == 48 or (IsDebug and question > 0 and question%10 == 0):
        result = get_result(storage, name, lang, mode=1)
        bot.send_message(message.chat.id, result, parse_mode=DEFAULT_PARSE_MODE)
        is_run = question < 48

        if is_run:
            time.sleep(3)

    if question > 21 and 'query_id' in kw:
        if get_result(storage, name, lang, mode=2) and not storage.get(name, 'warning'):
            text = _WARNINGS[lang][0]

            bot.answer_callback_query(
                kw['query_id'],
                text=text,
                show_alert=True
                )

            storage.set(name, 'warning', 1)
            time.sleep(3)

    if is_run:
        answers = deepcopy(_ANSWERS[lang])
        if _with_extra:
            if question not in _no_ext_questions:
                answers += deepcopy(_EXT_ANSWERS[lang])
        for i, a in enumerate(answers):
            answers[i][1] = answers[i][1] % (_TEST_NAME, question+1)
        send_inline_keyboard(bot, message, answers, get_question(question, lang))

    elif 'query_id' in kw:
        bot.answer_callback_query(
            kw['query_id'],
            text=get_finish(storage, name, 1, lang),
            show_alert=True
            )

        for p in sorted([x for x in _RESULTS[lang].keys()]):
            if p in _results:
                value, param = _results[p]
                storage.set(name, '%s.R%s' % (_TEST_NAME, p), value)
                storage.set(name, '%s.T%s' % (_TEST_NAME, p), '%s:%s' % (param, value), with_encode=True)

        time.sleep(3)

        help(bot, message, logger=logger, mode=1, **kw)

## -------------------------- ##

def lines(text):
    for line in text.split('\n'):
        if not line:
            continue
        x = line.split('.')
        n, s = int(x[0].strip()), x[1].strip()
        print('"""\n%s. %s\n""",' % (n, s))

def check(data, key, res):
    s = 0
    for k in data[key].keys():
        #print(k)
        q = k.split('.')[1]
        if not q.isdigit():
            continue
        #print(q)
        v = int(data[key][k])
        for i in range(0, 2):
            for r, sc in enumerate(res[i]):
                score = r == 2 and 1 or r == 1 and 2 or 3
                if int(q) in sc:
                    s += i == 0 and v > 0 and score or i == 1 and v < 0 and score or 0
                    break
    return s

def selftest(data, lang, with_print=None):
    key = _TEST_NAME
    results = _RESULTS[lang]

    out = []
    r = {}
    for k in sorted(results.keys()):
        if not k in r:
            r[k] = 0
        x = check(data, key, results[k])
        if with_print:
            print(x)
        r[k] += x

        rp = '%s.R%s' % (key, k)
        if rp in data[key]:
            x = int(data[key].get(rp, '0'))
            if r[k] == x:
                out.append('OK')
            else:
                out.append('Error %s [%s:%s]' % (rp, r[k], x))
        else:
            out.append(NO_RESULTS)

    is_ok, is_error = 1, 0
    for s in out:
        if s.startswith('OK'):
            pass
        elif s.startswith('Error'):
            is_ok = 0
            is_error = 1
            if with_print or IsWithPrintErrors:
                print(key, s)
            break
        else:
            is_ok = 0
            break

    return is_ok and 'OK' or is_error and 'Error' or NO_RESULTS
