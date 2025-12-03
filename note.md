## 新闻项目   

### 抽象   
> 设置一个基类，这样可以方便其它orm的模型继承    

```python
from exts.dbhelper import db
from datetime import datetime
class BaseModel(db.Model):
    __abstract__ = True #tips:这里设置的是作为一个抽象类，它就不会作为一个模型单独出现了
    id = db.Column(db.Integer, primary_key=True,autoincrement=True)
    date_time = db.Column(db.DateTime, default=datetime.now)

```  

注意要设置抽象,否则将会创建一个基类表
![img.png](img.png)  
这不是我们想要的，所以一定要加上__abstract__=True   

> 这样之后我们再进行migrate和upgrade，这样就正确了
> ![img_1.png](img_1.png)
> 
--- 
### 跨域操作   

- 引入CORS

```python
from flask_cors import CORS
cors = CORS()
```

- 调用并初始化
```python
def create_app():
    app = Flask(__name__)

    app.config.from_object(configdict['default'])
    db.init_app(app)

    #tips:注册蓝图
    app.register_blueprint(news_bp)
    print(app.url_map) #tips:打印一下路由
    cors.init_app(app)
    migrate.init_app(app, db)
    return app
```


