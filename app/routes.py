from app import bot, db
from app.config import Config
import telebot
from telebot import types
from flask import request, current_app as app
import time
from app.models import Student, Teacher, Tables
from flask import request
# import httplib2
# import googleapiclient.discovery
# from oauth2client.service_account import ServiceAccountCredentials

# CREDENTIALS_FILE = 'woven-environs-272314-a2f4d17f757a.json'
# credentials = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE,
# ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive'])

# httpAuth = credentials.authorize(httplib2.Http()) # Авторизуемся в системе
# service = googleapiclient.discovery.build('sheets', 'v4', http=httpAuth) # Выбираем работу с таблицами и 4 версию API


@app.route('/')
def webhook():
    try:
        bot.remove_webhook()
        time.sleep(1)
        bot.set_webhook(Config.URL + Config.secret)
    except Exception as e:
        return "Ошибка ", e
    return "!", 200


@app.route('/{}'.format(Config.secret), methods=["POST"])
def web_hook():
    if request.headers.get('content-type') == 'application/json':
        bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
        return "!", 200
    else:
        flask.abort(403)


@bot.message_handler(content_types=['text'])
def start_command(message):
    if message.text == "/start":
        keyboard = types.InlineKeyboardMarkup()
        callback_button_teacher = types.InlineKeyboardButton(text="Я преподаватель", callback_data="teacher")
        callback_button_student = types.InlineKeyboardButton(text="Я студент", callback_data="student")
        keyboard.add(callback_button_teacher)
        keyboard.add(callback_button_student)
        bot.send_message(message.chat.id, text='Выберите роль', reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    if call.message:
        if call.data == "teacher":
            # keyboard = types.InlineKeyboardMarkup()
            bot.send_message(chat_id=call.message.chat.id, text='Представьтесь, пожалуйста')
            bot.register_next_step_handler(call.message, teacher_name_step)
        elif call.data == "student":
            bot.send_message(chat_id=call.message.chat.id, text='Представьтесь, пожалуйста')
            bot.register_next_step_handler(call.message, student_name_step)


def teacher_name_step(message):
    try:
        chat_id = message.chat.id
        name = message.text
        teacher = Teacher(id=chat_id, name=name)
        db.session.add(teacher)
        db.session.commit()
        msg = bot.send_message(chat_id, text='Введите ссылку на таблицу Google')
        bot.register_next_step_handler(msg, teacher_table_link_step)
    except Exception as e:
        bot.reply_to(message, "Произошла какая-то ошибка, я вас не понял")


def teacher_table_link_step(message):
    try:
        chat_id = message.chat.id
        link = message.text
        msg = bot.send_message(chat_id, text='Введите, как таблица будет называться в боте')
        bot.register_next_step_handler(msg, teacher_table_name_step, link)
    except Exception as e:
        bot.reply_to(message, 'Произошла какая-то ошибка, я вас не понял')


def teacher_table_name_step(message, link):
    try:
        chat_id = message.chat.id
        name = message.text
        table = Tables(url=link, user_id=chat_id, list_name=name)
        db.session.add(table)
        db.session.commit()
        msg = bot.send_message(chat_id, text='Принято')
    except Exception as e:
        bot.reply_to(message, 'Произошла какая-то ошибка, я вас не понял')


def student_name_step(message):
    try:
        chat_id = message.chat.id
        name = message.text
        student = Student(id=chat_id, name=name)
        db.session.add(student)
        db.session.commit()
        keyboard = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        agree = types.KeyboardButton(text='Да, я хочу передать свой телефон', request_contact=True)
        decline = types.KeyboardButton(text='Нет, я не хочу передавать свой телефон')
        keyboard.add(agree)
        keyboard.add(decline)
        bot.send_message(chat_id, text='Хотите передать свой номер телефона?', reply_markup=keyboard)
    except Exception as e:
        bot.reply_to(message, 'Произошла какая-то ошибка, я вас не понял')


@bot.message_handler(content_types=['contact'])
def student_phone_step(message):
    chat_id = message.chat.id
    student_phone = message.contact.phone_number
    Student.query.filter_by(id=chat_id).first().update({'phone': student_phone})
    db.session.commit()
    bot.send_message(chat_id, text='Завершено успешно')
    
    
bot.enable_save_next_step_handlers(delay=2)

bot.load_next_step_handlers()
