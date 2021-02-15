import os
import sys

import flask
import telebot
from dao import DBdao as db
from models import Person, Queue
import config
from flask import Flask, request

# globals
bot = telebot.TeleBot(config.token)
queue_id = None

app = Flask(__name__)


@bot.message_handler(commands=["roll"])
def new_queue(message):
    try:
        ranging = int(message.text.split()[1])
        name = " ".join(message.text.split()[2:])
    except Exception as e:
        print(e)
        name = ""
        ranging = 0
    queue = Queue(name, ranging=ranging)
    added = db._add_queue(queue)
    qid = queue.id
    keyboard = telebot.types.InlineKeyboardMarkup()
    btn2 = telebot.types.InlineKeyboardButton(text="Додати фото", callback_data="img "+str(qid))
    keyboard.add(btn2)
    if not added:
        bot.send_message(message.chat.id, "Такий ролл уже існує\n")
    else:
        bot.send_message(message.chat.id, "Ролл «" + queue.name + "»", reply_markup=keyboard)


@bot.message_handler(commands=["hello"])
def hello(message):
    bot.send_message(message.chat.id, "Привіт")


@bot.message_handler(commands=["list"])
def list_rolls(message):
    queues = db.get_queues()
    list_items = []
    for item in queues:
        list_items.append("!" + str(item[0]))
    markup = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    for item in list_items:
        markup.add(item)
    bot.send_message(message.chat.id, "Вибирай", reply_markup=markup)



@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    if call.message:
        if call.data.split()[0] != 'img':
            qid = int(call.data)
            queue = db.get_queue(qid)
            user = call.from_user
            first_name = user.first_name or "Anonymous"
            last_name = user.last_name or ""
            new_user = Person(user.id, first_name, last_name)
            order = db.get_order(queue)
            for person in order:
                if person[1] == new_user.id:
                    bot.answer_callback_query(call.id)
                    return
            else:
                db.add_order(new_user, queue)
            text = "Ролл «" + queue.name + "»\n"
            order = db.get_order(queue)
            for i in range(len(order)):
                item = order[i]
                text += "(" + str(item[0]) + ") " + item[2] + " " + item[3] + "\n"
            keyboard = telebot.types.InlineKeyboardMarkup()
            btn1 = telebot.types.InlineKeyboardButton(text="Ролл", callback_data=str(qid))
            keyboard.add(btn1)
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=text, reply_markup=keyboard)
        else:
            global queue_id
            queue_id = int(call.data.split()[1])
            bot.send_message(call.message.chat.id, "Тепер надсилай мені фото")



@bot.message_handler(content_types=["photo"])
def add_photo(message):
    global queue_id
    if queue_id is None:
        print("Queue id is None")
    else:
        file_id = message.photo[-1].file_id
        queue = Queue(id=queue_id, img=str(file_id))
        db.update_queue(queue)
        bot.send_photo(message.chat.id, file_id)
        keyboard = telebot.types.InlineKeyboardMarkup()
        btn1 = telebot.types.InlineKeyboardButton(text="Ролл", callback_data=str(queue_id))
        keyboard.add(btn1)
        bot.send_message(message.chat.id, "Готово", reply_markup=keyboard)
        queue_id = None


@bot.message_handler(func=lambda message: True)
def choose(message):
    if message.text[0] == "!":
        try:
            name = message.text[1:]
        except Exception as e:
            print(e)
            name = ""
        queue = db.get_queue(name, name=True)
        added = db._add_queue(queue)
        qid = queue.qid
        bot.send_photo(message.chat.id, queue.img)
        keyboard = telebot.types.InlineKeyboardMarkup()
        btn1 = telebot.types.InlineKeyboardButton(text="Ролл", callback_data=str(qid))
        keyboard.add(btn1)
        bot.send_message(message.chat.id, "Готово", reply_markup=keyboard)


@app.route("/bot", methods=['POST'])
def read_webhook():
    if flask.request.headers.get('content-type') == 'application/json':
        json_string = flask.request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return ''
    else:
        flask.abort(403)


@app.route("/")
def webhook():
    bot.remove_webhook()
    bot.set_webhook(url=config.WEBHOOK_URL_PATH + "bot")
    return "?", 200


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=os.environ.get('PORT', 80))
