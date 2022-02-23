#!venv/bin/python

import os
import datetime
import time
import pytz
import json
import traceback
import logging
import threading

import telebot
from telebot import types

from flask import Flask, request

from config import *
from app.utils import normpath, getToday, getTime, getDate, getDateOnly, checkDate, spent_time
from app.dialogs.scenario import make_answer

P_TIMEZONE = pytz.timezone(TIMEZONE)
TIMEZONE_COMMON_NAME = TIMEZONE_COMMON_NAME

basedir = ''

def setup():
    print(basedir)
    sys.path.append(basedir)

# --------------
# Enable logging
# --------------

today = getDate(getToday())

log = normpath(os.path.join(LOG_PATH, '%s_%s.log' % (today, LOG_NAME)))

logging.basicConfig(
    filename=log,
    format='%(asctime)s: %(name)s-%(levelname)s\t%(message)s', 
    level=logging.DEBUG, 
    datefmt=UTC_FULL_TIMESTAMP,
)

logger = logging.getLogger(__name__)

# ------------
# Create a bot
# ------------

bot = telebot.TeleBot(TOKEN)

app = Flask(__name__)

# ======== #
# HANDLERS #
# ======== #

def info(command, force=None, is_error=False, is_warning=False, is_ok=False, data=None):
    line = '>>> %s%s' % (command, data and '\n%s' % data or '')
    if IsDisableOutput:
        return
    if is_error:
        logging.error(line)
    elif is_warning:
        logging.warning(line)
    elif IsTrace or force:
        logging.info(line)

## ------ ##

@bot.message_handler(commands=['start'])
def start(message):
    command = message.text[1:]
    info(command, data=message.json)
    bot.reply_to(message, """
Здравствуйте!
Вы работаете с Telegram-Ботом: AdvanceMentalHealthBot.
Спасибо, что обратились к нам! 
Для начала нашей беседы, пожалуйста, нажмите кнопку /begin.
Помощь /help.
    """.strip())

@bot.message_handler(commands=['description'])
def description(message):
    command = message.text[1:]
    info(command, data=message.json)
    bot.reply_to(message, """
А) объяснение возможностей этого самого нашего чудо-бота;
Б) сообщение, что он, бот, понимает обратившегося и может ему помочь;
В) что у него, бота, есть свой метод.
    """.strip())

@bot.message_handler(commands=['help'])
def help(message):
    command = message.text[1:]
    info(command, data=message.json)
    bot.reply_to(message, """
/description: Краткое описание и наши возможности;
/commands: Список команд;
    """.strip())

@bot.message_handler(commands=['commands'])
def commands(message):
    command = message.text[1:]
    info(command, data=message.json)
    bot.reply_to(message, """
/begin: Начать диалог (доверительную беседу);
/end: Завершить диалог.
    """.strip())

@bot.message_handler(commands=['begin'])
def begin(message):
    command = message.text[1:]
    info(command, data=message.json)
    bot.reply_to(message, """
Хорошо. Давайте, продолжим...
    """.strip())
    time.sleep(1)
    make_answer(bot, message, command, logger=info)

@bot.message_handler(commands=['end'])
def end(message):
    command = message.text[1:]
    make_answer(bot, message, command, logger=info, no_advice=True)
    
@bot.callback_query_handler(func=lambda call: True) 
def button(query):
    command = 'button'
    bot.send_message(query.message.chat.id, query.data)
    """
    bot.answer_callback_query(
            query.id,
            text='Hello! This callback.',
            show_alert=True
            )
    """
    if query.data == 'accept:0':
        make_answer(bot, query.message, 'end', logger=info, query_id=query.id)
    else:
        make_answer(bot, query.message, command, data=query.data, logger=info, query_id=query.id)

@bot.message_handler(func=lambda message: True)
def text(message):
    command = 'text'
    make_answer(bot, message, command, logger=info)
    time.sleep(3)
    make_answer(bot, message, '...', logger=info, index=1)

@bot.message_handler(commands=['stop'])
def stop(message):
    #threading.Thread(target=shutdown).start()
    #shutdown()
    bot.reply_to(message, """
Для начала диалога нажмите /begin.
    """.strip())

def shutdown():
    #updater.stop()
    #updater.is_idle = False
    pass

@app.route('/{}'.format(TOKEN), methods=['POST'])
def getMessage():
    bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
    return "!", 200

def main():
    """
        Start the bot
    """
    while True:
        try:
            bot.polling(none_stop=True) #, interval=0, timeout=0
        except KeyboardInterrupt:
            break
        except:
            logger.error('Impossible to start...')
            print_exception()

        time.sleep(10)


if __name__ == '__main__':
    if app_mode == 'webhook':
        app.run(threaded=True)
    else:
        main()
