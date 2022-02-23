#!venv/bin/python

import os
import datetime
import pytz
import json
import traceback
import logging
import telebot

from config import *
from app.utils import normpath, getToday, getTime, getDate, getDateOnly, checkDate, spent_time

P_TIMEZONE = pytz.timezone(TIMEZONE)
TIMEZONE_COMMON_NAME = TIMEZONE_COMMON_NAME

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

# ======== #
# HANDLERS #
# ======== #

def _info(command, line=None):
    logging.info('>>> %s%s' % (command, line and '\n%s' % line or ''))

@bot.message_handler(commands=['start'])
def send_welcome(message):
    command = message.text[1:]
    _info(command, message.json)
    bot.reply_to(message, """
Здравствуйте!
Вы работаете с Telegram-Ботом: AdvanceMentalHealthBot.
Спасибо, что обратились к нам! 
Для начала нашей беседы, пожалуйста, нажмите кнопку /begin.
Помощь /help.
    """.strip())

@bot.message_handler(commands=['description'])
def send_welcome(message):
    bot.reply_to(message, """
А) объяснение возможностей этого самого нашего чудо-бота;
Б) сообщение, что он, бот, понимает обратившегося и может ему помочь;
В) что у него, бота, есть свой метод.
    """.strip())

@bot.message_handler(commands=['help'])
def send_welcome(message):
    bot.reply_to(message, """
/description: Краткое описание и наши возможности;
/commands: Список команд;
    """.strip())

@bot.message_handler(commands=['commands'])
def send_welcome(message):
    bot.reply_to(message, """
/begin: Начать диалог (доверительную беседу);
/end: Завершить диалог.
    """.strip())

@bot.message_handler(commands=['begin', 'end'])
def begin_end(message):
    command = message.text[1:]
    _info(command, message.json)
    bot.reply_to(message, """
Продолжим...
    """.strip())

def run():
    try:
        bot.polling(none_stop=True)
    except:
        logger.error('Impossible to start...')


if __name__ == '__main__':
    run()
