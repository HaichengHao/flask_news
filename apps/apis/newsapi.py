from flask_restful import Resource, fields, marshal_with, reqparse, Api
from flask import Blueprint
from exts.dbhelper import db
from ..models.news import NewsType, News

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
parser.add_argument('type_name', type=str,location=['form'])


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


news_api.add_resource(NewstypeCBV, '/types', endpoint='types')
