from exts.dbhelper import db
from . import BaseModel


class NewsType(BaseModel):
    __tablename__ = 'news_type'
    type_name = db.Column(db.String(50), nullable=False)
    # newsinfo = db.relationship('News', backref='news_type', lazy=True)


#tips:设置news表
class News(BaseModel):
    __tablename__ = 'news'
    title = db.Column(db.String(128), nullable=False) #标题
    content = db.Column(db.Text, nullable=False)  #内容
    news_type_id = db.Column(db.Integer,db.ForeignKey('news_type.id'), nullable=False) #添加外键,新闻类型id


