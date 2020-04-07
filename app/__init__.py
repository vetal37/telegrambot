from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from app.config import Config
import telebot
import time

bot = telebot.TeleBot(Config.secret, threaded=True)


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    db = SQLAlchemy()
    db.app = app
    db.init_app(app)

    app.app_context().push()
    with app.app_context():
        from app import routes
        db.create_all()

    migrate = Migrate(app, db)

    return app
