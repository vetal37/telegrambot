from app import bot, db
from app.config import Config
import telebot
from telebot import types
from flask import request, current_app as app
import time
from app.models import Student, Teacher, Tables
from flask import request
import re


# import app.google_tables.tables


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
        time.sleep(0.4)
        bot.set_webhook(Config.URL + Config.secret)
        print("webhook set")
    except Exception as e:
        bot.send_message(message.chat.id, text="Ошибка " + str(e))
        return "Ошибка ", e
    return "!", 200


@app.route('/{}'.format(Config.secret), methods=["POST"])
def web_hook():
    if request.headers.get('content-type') == 'application/json':
        bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
        print("message received 200")
        return "!", 200
    else:
        print("flask abort 403")
        flask.abort(403)


@bot.message_handler(commands=['start'])
def start_command(message):
    keyboard = types.InlineKeyboardMarkup()
    callback_button_teacher = types.InlineKeyboardButton(text="Я преподаватель", callback_data="teacher")
    callback_button_student = types.InlineKeyboardButton(text="Я студент", callback_data="student")
    keyboard.add(callback_button_teacher)
    keyboard.add(callback_button_student)
    bot.send_message(message.chat.id, text='Выберите роль', reply_markup=keyboard)


@bot.message_handler(func=lambda message: message.text == "Нет, я не хочу передавать свой телефон"
                     and message.content_type == 'text')
def telephone(message):
    keyboard = types.ReplyKeyboardMarkup(one_time_keyboard=False)
    change_name = types.KeyboardButton(text='Поменять имя')
    phone = types.KeyboardButton(text='Передать номер телефона', request_contact=True)
    keyboard.add(change_name)
    keyboard.add(phone)
    bot.send_message(message.chat.id, text='Тогда всё готово! :)', reply_markup=keyboard)


@bot.message_handler(func=lambda message: message.text == "Поменять имя"
                     and message.content_type == 'text')
def new_name(message):
    msg1 = bot.send_message(message.chat.id, text='Ввведите новое имя')
    bot.register_next_step_handler(msg1, student_change_name_step)


@bot.message_handler(func=lambda message: message.text == "/test"
                     and message.content_type == 'text')
def test(message):
    try:
        try:
            msg = Student.query.filter(Student.id == str(message.chat.id)).first()
            bot.send_message(message.chat.id, text='Вот всё, что на вас есть:' + str(msg))
        except Exception:
            msg = Teacher.query.filter(Teacher.id == str(message.chat.id)).first()
            bot.send_message(message.chat.id, text='Вот всё, что на вас есть:' + str(msg))
    except Exception as e:
        bot.send_message(message.chat.id, text='Error ' + str(e))


@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    if call.message:
        if call.data == "teacher":
            msg = bot.send_message(chat_id=call.message.chat.id, text='Представьтесь, пожалуйста')
            bot.register_next_step_handler(msg, teacher_name_step)
        elif call.data == "student":
            msg = bot.send_message(chat_id=call.message.chat.id, text='Представьтесь, пожалуйста')
            bot.register_next_step_handler(msg, student_name_step)
        elif call.data == "link":
            bot.register_next_step_handler(call.message, teacher_table_link_step)
        elif call.data == "delete1":
            bot.register_next_step_handler(call.message, teacher_table_delete_step1)
        elif call.data == "delete2":
            bot.register_next_step_handler(call.message, teacher_table_delete_step2)
        elif call.data == "start test":
            bot.register_next_step_handler(call.message, teacher_start_test_step)
        elif call.data == "test table":
            bot.register_next_step_handler(call.message, teacher_test_step)


def teacher_name_step(message):
    try:
        chat_id = message.chat.id
        name = message.text

        try:
            check_name = Student.query.filter(Student.id == str(chat_id)).first().name
            bot.send_message(chat_id, text='Вы уже зарегистрировались как студент ' + str(check_name))
        except AttributeError:
            teacher = Teacher(id=chat_id, name=name)
            db.session.add(teacher)
            db.session.commit()
            msg = bot.send_message(chat_id, text='Введите ссылку на таблицу Google')
            bot.register_next_step_handler(msg, teacher_table_link_step)
    except Exception as e:
        bot.reply_to(message, "Произошла какая-то ошибка, я вас не понял" + str(e))


def find_url(string):
    url = re.findall("http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),#]|(?:%[0-9a-fA-F][0-9a-fA-F]))+", string)
    return url


def teacher_table_link_step(message):
    try:
        chat_id = message.chat.id
        link = message.text
        try:
            link = find_url(link)[0]
            msg = bot.send_message(chat_id, text='Введите, как таблица будет называться в боте')
            bot.register_next_step_handler(msg, teacher_table_name_step, link, False)
        except IndexError:
            bot.reply_to(message, 'Введите правильную ссылку на таблицу')
    except Exception as e:
        bot.reply_to(message, 'Произошла какая-то ошибка, я вас не понял' + str(e))


def teacher_table_name_step(message, link, reg):
    try:
        chat_id = message.chat.id
        name = message.text

        if not reg:
            table = Tables(url=link, user_id=chat_id, list_name=name)
            db.session.add(table)
            db.session.commit()

        keyboard = types.InlineKeyboardMarkup()
        add_table = types.InlineKeyboardButton(text="Добавить таблицу", callback_data="link")
        delete_table = types.InlineKeyboardButton(text="Удалить таблицу", callback_data="delete1")
        start_test = types.InlineKeyboardButton(text="Начать тест", callback_data="start test")
        keyboard.add(add_table)
        keyboard.add(delete_table)
        keyboard.add(start_test)
        bot.send_message(chat_id, text='Принято, вот доступные действия:', reply_markup=keyboard)
    except Exception as e:
        bot.reply_to(message, 'Произошла какая-то ошибка, я вас не понял' + str(e))


def teacher_table_delete_step1(message):
    try:
        chat_id = message.chat.id
        keyboard = types.InlineKeyboardMarkup()
        for i in Tables.query.filter_by(
                Tables.user_id == str(chat_id)).all().list_name:
            keyboard.add(types.InlineKeyboardButton(text=i, callback_data="delete2"))
        bot.send_message(chat_id, text='Выберите таблицу для удаления', reply_markup=keyboard)
    except Exception as e:
        bot.reply_to(message, 'Произошла какая-то ошибка, я вас не понял' + str(e))


def teacher_table_delete_step2(message):
    try:
        chat_id = message.chat.id
        text = message.text
        Tables.query.get({'list_name': text}).query.delete()
        msg = bot.send_message(chat_id, text='Таблица ' + text + ' удалена')
        bot.register_next_step_handler(msg, teacher_table_name_step, None, True)
    except Exception as e:
        bot.reply_to(message, 'Произошла какая-то ошибка, я вас не понял' + str(e))


def teacher_start_test_step(message):
    try:
        chat_id = message.chat.id
        name = message.text
        table = Tables(url=link, user_id=chat_id, list_name=name)
        db.session.add(table)
        db.session.commit()
        keyboard = types.InlineKeyboardMarkup()
        query = Tables.query.filter_by(Tables.user_id == str(chat_id)).all()
        #  log:
        print(query)
        for i in query:
            keyboard.add(types.InlineKeyboardButton(text=i, callback_data="test table"))
        msg = bot.send_message(chat_id, text='Выберите таблицу', reply_markup=keyboard)
    except Exception as e:
        bot.reply_to(message, 'Произошла какая-то ошибка, я вас не понял')


def teacher_test_step(message):
    try:
        chat_id = message.chat.id
        name = message.text

    except Exception as e:
        bot.reply_to(message, "Произошла какая-то ошибка, я вас не понял")


def student_name_step(message):
    try:
        chat_id = message.chat.id
        name = message.text
        try:
            check_name = Student.query.filter(Student.id == str(chat_id)).first().name
            bot.send_message(chat_id, text='Вы уже зарегистрировались как студент ' + str(check_name))
        except AttributeError:
            student = Student(id=chat_id, name=name)
            db.session.add(student)
            db.session.commit()
            keyboard = types.ReplyKeyboardMarkup(one_time_keyboard=False)
            agree = types.KeyboardButton(text='Да, я хочу передать свой телефон', request_contact=True)
            decline = types.KeyboardButton(text='Нет, я не хочу передавать свой телефон')
            keyboard.add(agree)
            keyboard.add(decline)
            bot.send_message(chat_id, text='Хотите передать свой номер телефона?', reply_markup=keyboard)
    except Exception as e:
        bot.reply_to(message, 'Произошла какая-то ошибка, я вас не понял' + str(e))


def student_change_name_step(message):
    try:
        chat_id = message.chat.id
        new_name = message.text
        Student.query.filter(Student.id == str(chat_id)).first().name = new_name
        db.session.commit()
        keyboard = types.ReplyKeyboardMarkup(one_time_keyboard=False)
        change_name = types.KeyboardButton(text='Поменять имя')
        if not Student.query.filter(Student.id == str(chat_id)).first().phone:
            phone = types.KeyboardButton(text='Передать номер телефона', request_contact=True)
            keyboard.add(phone)
        keyboard.add(change_name)
        bot.send_message(chat_id, text='Завершено успешно', reply_markup=keyboard)
    except Exception as e:
        bot.reply_to(message, 'Произошла какая-то ошибка, я вас не понял' + str(e))


def vote_for_best_student(message): #TODO голосовалка
    try:
        chat_id = message.chat.id
        poll = types.Poll(question="Кто является самым активным студентом?")
        for i in Student.query.filter(Student.id == str(chat_id)).all():
            poll.add(Student.query.filter(Student.id == str(chat_id)).first().name)
        bot.send_poll(chat_id=chat_id, poll = poll)
    except Exception as e:
        bot.reply_to(message, 'Произошла какая-то ошибка, я вас не понял')

@bot.message_handler(content_types=['contact'])
def student_phone_step(message):
    try:
        chat_id = message.chat.id
        student_phone = message.contact.phone_number
        Student.query.filter(Student.id == str(chat_id)).first().phone = student_phone
        db.session.commit()
        keyboard = types.ReplyKeyboardMarkup(one_time_keyboard=False)
        change_name = types.KeyboardButton(text='Поменять имя')
        keyboard.add(change_name)
        bot.send_message(chat_id, text='Завершено успешно', reply_markup=keyboard)
    except Exception as e:
        bot.reply_to(message, 'Произошла какая-то ошибка, я вас не понял' + str(e))


bot.enable_save_next_step_handlers(delay=0.5)

bot.load_next_step_handlers()