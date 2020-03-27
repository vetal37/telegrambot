from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from app.config import Config
import telebot

db = SQLAlchemy()
bot = telebot.TeleBot(Config.secret, threaded=False)
bot.remove_webhook()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(Config)
    ctx = app.app_context()
    ctx.push()

    db.init_app(app)
    # bot.set_webhook(Config.URL.format(Config.secret))

    migrate = Migrate(app, db)

    from app import routes, models

    return app
