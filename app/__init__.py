from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from app.config import Config
import telebot
import time

db = SQLAlchemy()
bot = telebot.AsyncTeleBot(Config.secret, threaded=True)
bot.remove_webhook()
time.sleep(0.4)
bot.set_webhook(Config.URL + Config.secret)


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    db.init_app(app)

    with app.app_context():
        from app import routes
        db.create_all()

    migrate = Migrate(app, db)

    return app
