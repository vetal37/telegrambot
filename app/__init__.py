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

    from app.views.users.routes import users
    from app.views.main.routes import main
    from app.views.posts.routes import posts
    from app.views.errors.handlers import errors

    app.register_blueprint(users)
    app.register_blueprint(main)
    app.register_blueprint(posts)
    app.register_blueprint(errors)

    return app
