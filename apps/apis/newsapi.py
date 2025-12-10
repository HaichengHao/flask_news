from flask_restful import Resource, fields, marshal_with, reqparse, Api, marshal
from flask import Blueprint
from exts.dbhelper import db
from ..models.news import NewsType, News
from sqlalchemy.orm import joinedload #预加载关联数据

news_bp = Blueprint('news', __name__)
news_api = Api(news_bp)

# tips:定义输出
resp_field = {
    'id': fields.Integer,
    'tpname': fields.String(attribute='type_name'),
    'date_time': fields.DateTime
}

# tips:定义输入req,并添加参数
parser = reqparse.RequestParser()
parser.add_argument('type_name', type=str, location=['form'])


# step 1:定义新闻类型api

class NewstypeCBV(Resource):
    @marshal_with(resp_field)
    def get(self):
        all_news = NewsType.query.all()
        return all_news

    @marshal_with(resp_field)
    def post(self):
        pargs = parser.parse_args()

        typename = pargs.get('type_name')
        ndbobj = NewsType()  # tips:创建一个新的数据库对象
        ndbobj.type_name = typename
        db.session.add(ndbobj)
        db.session.commit()  # 提交

        return ndbobj


# step 2: 定义新闻api

# tips:自定义一个fields,来实现relationship的返回
class id2name(fields.Raw):
    def format(self, value):
        return value.username


nl_fields = {
    'id': fields.Integer,
    'title': fields.String,
    'desc': fields.String,
    'date_time': fields.DateTime,
    'author': id2name(attribute='author'),  # 直接对接字段User表中的author
    'url': fields.Url('news.news_detail', absolute=True)  # 这里是新闻详情页的链接
}
nl_parser = reqparse.RequestParser()
nl_parser.add_argument('typeid', type=int, location=['form', 'args'], help='需要选择新闻类型id', required=True)
nl_parser.add_argument('page', type=int, location=['args'])


class NewsListCBV(Resource):
    def get(self):
        nl_args = nl_parser.parse_args()
        page = nl_args.get('page', 1)  # 没传入就默认为1
        typeid = nl_args.get('typeid')

        pagination = News.query.filter(News.news_type_id == typeid).paginate(page=page, per_page=8)
        # tips:
        # 回顾一下,pagination有几个常用方法
        # .page 获取当前页数
        # .items 拿到所有元素
        # .has_prev,.has_next 判断有没有上下页
        # .total
        data = {
            'has_more': pagination.has_next,  # tips:利用pagination对象的内置has_next,has_prev来进行分页判断
            'data': marshal(pagination.items, nl_fields),
            'page': pagination.page,
            'html': 'null'
        }

        return data


# 定义评论的回复fields
reply_fields = {
    'user': id2name(attribute='replyuser'),
    'love_num': fields.Integer,
    'content': fields.String,
    'date_time': fields.DateTime,

}

# 定义评论的fiedls
comments_fields = {
    'user': id2name('user'),
    'love_num': fields.Integer,
    'content': fields.String,
    'date_time': fields.DateTime,
    'reply': fields.List(fields.Nested(reply_fields)),
}

# 定义新闻详情页面
news_detail_fields = {
    'id': fields.Integer,
    'title': fields.String,
    'date_time': fields.DateTime,
    'author': id2name(attribute='author'),
    'content': fields.String,
    'comments': fields.List(fields.Nested(comments_fields)),
}

# tips:创建新增新闻的parser
news_parser = reqparse.RequestParser()
news_parser.add_argument('title', type=str, location=['form'])  # 标题
news_parser.add_argument('content', type=str, location=['form'])  # 内容
news_parser.add_argument('user_id', type=str, location=['form'])  # 作者
news_parser.add_argument('desc', type=str, location=['form'])  # 简介
news_parser.add_argument('news_type_id', type=int, location=['form'])  # 分类


class NewsDetailCBV(Resource):
    def get(self, id):
        news = News.query(joinedload(News.author)).get_or_404(id)
        return marshal(news, news_detail_fields)

    def post(self, uid):
        news_parser_args = news_parser.parse_args()
        title = news_parser_args.get('title')
        desc = news_parser_args.get('desc')
        author = news_parser_args.get('user_id')
        content = news_parser_args.get('content')
        news_type_id = news_parser_args.get('news_type_id')
        news = News(title=title, content=content, desc=desc, news_type_id=news_type_id, user_id=author)
        db.session.add(news)
        db.session.commit()
        return {
            'msg': '添加成功'
        }, 200


news_api.add_resource(NewstypeCBV, '/types', endpoint='types')
news_api.add_resource(NewsListCBV, '/newslst', endpoint='newslst')
news_api.add_resource(NewsDetailCBV, '/newsdetail/<id>', endpoint='news_detail')
