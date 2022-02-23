import random
import re
from flask import Flask, request
import telegram
from bot.credentials import bot_token, bot_user_name, URL

DESCRIPTION = """
Welcome to MKaroPrivateBot.
This is a Telegram Chatbots example.

Prequisites:
    Python
    Flask
    Telegram Bot API
    Heroku
    Git
"""

global bot
global TOKEN

TOKEN = bot_token
bot = telegram.Bot(token=TOKEN)

app = Flask(__name__)

def Capitalize(s, as_is=None):
    return (s and len(s) > 1 and s[0].upper() + (as_is and s[1:] or s[1:].lower())) or (len(s) == 1 and s.upper()) or ''

def unCapitalize(s, as_is=None):
    return (s and len(s) > 1 and s[0].lower() + s[1:]) or (len(s) == 1 and s.lower()) or ''

def _get_message(text):
    return re.sub(r'\s{2,}', ' ', re.sub(r'[\.!,<>]', '', text.encode('utf-8').decode())).strip().lower()

def _get_answer(choices):
    return Capitalize(random.choice(choices.split(':')), as_is=1)

@app.route('/{}'.format(TOKEN), methods=['POST'])
def respond():
    # retrieve the message in JSON and then transform it to Telegram object
    update = telegram.Update.de_json(request.get_json(force=True), bot)

    if not (update and update.message):
        return repr(request)

    chat_id = update.message.chat.id
    msg_id = update.message.message_id

    # Telegram understands UTF-8, so encode text for unicode compatibility
    text = _get_message(update.message.text)

    answer = None

    # the first time you chat with the bot AKA the welcoming message
    if text == "/start":
        # print the welcoming message
        answer = DESCRIPTION

    elif text.endswith('?'):
        answer = '%s, %s' % (
            _get_answer('ой:ай:ах:ох'),
            _get_answer('да не знаю я, что пристал:лучше нажми 1:подумаю на досуге:это когда туалетная бумага заканчивается?...')
        )

    elif text in 'приветик:здорово:hi:hello:здравствуйте':
        answer = '%s!' % _get_answer('привет:здравствуйте:hi:hello:ну здорово:приветик')

    elif text in 'как дела:как обстановка:как жизнь:how are you:як у тебе':
        answer = '%s' % _get_answer('нормально:so-so:ничего:очень хорошо, спасибо!:здоровеньки були:fine really:отлично')

    elif text in 'что нового:какие новости:новини є':
        answer = '%s' % _get_answer('все добре! новини будуть наступного разу:новин чекаємо від Янінкі')

    elif text in 'пока:до свидания:bye:счастливо:удачи:до встречи':
        answer = '%s!' % _get_answer('пока:до свидания:bye:счастливо:удачи:до встречи:goodbye:допобачення:хай щастить: see you dear')

    elif text and len(re.sub(r'[\D]', '', text)) == 0:
        answer = 'Я пока до конца Вас не понимаю.\nСильно не старайтесь мне объяснять. Подучусь немножко.'

    elif text.isdigit() and (int(text) > 8 or int(text) <= 0):
        answer = 'Можете посмотреть веселые картинки: 1,2,3 ... 8'

    if answer:
        bot.sendMessage(chat_id=chat_id, text=answer, reply_to_message_id=msg_id)

    else:
        try:
            # clear the message we got from any non alphabets
            text = re.sub(r"\W", "_", text)

            # create the api link for the avatar based on http://avatars.adorable.io/
            url = "https://api.adorable.io/avatars/285/{}.png".format(text.strip())

            # reply with a photo to the name the user sent,
            # note that you can send photos by url and telegram will fetch it for you
            bot.sendPhoto(chat_id=chat_id, photo=url, reply_to_message_id=msg_id)

        except Exception:
            # if things went wrong
            bot.sendMessage(chat_id=chat_id, text="У меня плохое настроение. Давай завтра.", reply_to_message_id=msg_id)

    return 'ok'

@app.route('/getwebhook', methods=['GET', 'POST'])
@app.route('/getwebhookinfo', methods=['GET', 'POST'])
def get_webhook_info():
    return str(bot.getWebhookInfo().to_json())

@app.route('/setwebhook', methods=['GET', 'POST'])
def set_webhook():
    s = bot.setWebhook('{URL}{HOOK}'.format(URL=URL, HOOK=TOKEN), max_connections=20)
    if s:
        return "webhook setup ok: [%s]" % str(s)
    else:
        return "webhook setup failed"

@app.route('/disablewebhook', methods=['GET', 'POST'])
def disable_webhook():
    s = bot.setWebhook('')
    if s:
        return "webhook disable ok: [%s]" % str(s)
    else:
        return "webhook disable failed"

@app.route('/')
def index():
    return 'started'


if __name__ == '__main__':
    app.run(threaded=True)
