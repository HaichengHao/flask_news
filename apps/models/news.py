from exts.dbhelper import db
from . import BaseModel


class NewsType(BaseModel):
    __tablename__ = 'news_type'
    type_name = db.Column(db.String(50), nullable=False)
    # newslst = db.relationship('News', backref='news_type', lazy=True)


#tips:设置news表
class News(BaseModel):
    __tablename__ = 'news'
    title = db.Column(db.String(128), nullable=False) #标题
    content = db.Column(db.Text, nullable=False)  #内容
    desc = db.Column(db.String(255), nullable=False)  #概述
    news_type_id = db.Column(db.Integer,db.ForeignKey('news_type.id'), nullable=False) #添加外键,新闻类型id
    user_id = db.Column(db.Integer,db.ForeignKey('user.id'), nullable=False)
    def __str__(self):
        return self.title
class Comments(BaseModel):
    __tablename__ = 'comments'
    content=db.Column(db.Text,nullable=False)
    love_num = db.Column(db.Integer,default=0)
    user_id = db.Column(db.Integer,db.ForeignKey('user.id'))
    news_id=db.Column(db.Integer,db.ForeignKey('news.id'))
    def __str__(self):
        return self.content



