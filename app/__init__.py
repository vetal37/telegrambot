from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from app.config import Config

db = SQLAlchemy()


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(Config)
    ctx = app.app_context()
    ctx.push()

    db.init_app(app)
    bcrypt.init_app(app)
    csrf.init_app(app)
    login_manager.init_app(app)

    bot = telebot.TeleBot(config.secret, threaded=False)
    bot.remove_webhook()
    time.sleep(1)
    bot.set_webhook(url="https://vetal37.pythonanywhere.com/{}".format(Config.secret))

    migrate = Migrate(app, db)

    return app
