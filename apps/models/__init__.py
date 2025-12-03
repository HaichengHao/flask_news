#tips:定义一个基类,让models继承这个基类

from exts.dbhelper import db
from datetime import datetime
class BaseModel(db.Model):
    __abstract__ = True #tips:这里设置的是作为一个抽象类，它就不会作为一个模型单独出现了
    id = db.Column(db.Integer, primary_key=True,autoincrement=True)
    date_time = db.Column(db.DateTime, default=datetime.now)



