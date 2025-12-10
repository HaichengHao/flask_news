# from exts.dbhelper import db,migrate
from . import BaseModel
from exts.dbhelper import db


class User(BaseModel):
    __tablename__ = 'user'
    username = db.Column(db.String(64), unique=True, nullable=False)  # 用户名不可重复
    password = db.Column(db.String(256), nullable=False)
    phone = db.Column(db.String(64), unique=True, nullable=False)
    icon = db.Column(db.String(64), nullable=True)
    newslst = db.relationship('News', backref='author')
    comments = db.relationship('Comments', backref='user')  # tips:和评论建立关系，方便标记评论用户
    reply = db.relationship('Reply', backref='replyuser')

    def __str__(self):
        return self.username
