from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from app.config import Config
import telebot
import time

db = SQLAlchemy()
bot = telebot.TeleBot(Config.secret, threaded=False)
bot.remove_webhook()


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)

    with app.app_context():
        from app import routes
        db.create_all()

    time.sleep(1)

    bot.set_webhook(Config.URL + Config.secret)
    migrate = Migrate(app, db)

    return app
