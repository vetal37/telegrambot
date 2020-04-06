from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from app.config import Config
import telebot
import time

db = SQLAlchemy()
bot = telebot.TeleBot(Config.secret, threaded=True)


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    db.init_app(app)

    with app.app_context():
        from app import routes
        db.create_all()
        bot.remove_webhook()
        time.sleep(0.4)
        bot.set_webhook(config_class.URL + config_class.secret)

    migrate = Migrate(app, db)

    return app
