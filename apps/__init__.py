from apps.apis.newsapi import news_bp
from apps.apis.userapi import usr_bp
from settings import configdict
from flask import Flask
from .models.news import NewsType
from .models.user import User
from exts.dbhelper import db,migrate,cors
def create_app():
    app = Flask(__name__)

    app.config.from_object(configdict['default'])
    db.init_app(app) #tips:添加支持证书supports_credentials=True

    #tips:注册蓝图
    app.register_blueprint(news_bp)
    app.register_blueprint(usr_bp)
    print(app.url_map) #tips:打印一下路由
    cors.init_app(app)
    migrate.init_app(app, db)
    return app