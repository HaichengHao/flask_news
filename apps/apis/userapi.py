from flask_restful import Resource, Api, fields, reqparse
from flask import Blueprint
from werkzeug.datastructures.file_storage import FileStorage
from flask_restful.inputs import regex
import re

# tips 创建蓝图和api

usr_bp = Blueprint('usr', __name__)
usrApi = Api(usr_bp)

# 创建输出的fields模板
resp_fields = {
    'id': fields.Integer,
    'username': fields.String,
    # 'password': fields.String,
}

# 创建parser，定义输入的内容
parser = reqparse.RequestParser()
parser.add_argument('username', type=str, help='输入有问题', location=['form'])
parser.add_argument('password', type=str, location=['form'])
parser.add_argument('icon',type=FileStorage,location=['file'])


def phone_validator(phone):
    if re.match(r'^1[3-9]\d{9}$', phone):
        return phone
    else:
        raise ValueError('手机号格式有问题')


parser.add_argument('phone', type=phone_validator, location='form')
#tips:定义发送验证码的部分
class SendMessageCBV(Resource):
    def post(self):
        sms_parser = parser.parse_args()
        username = sms_parser.get('username')
        password = sms_parser.get('password')
        phone = sms_parser.get('phone')



class Usr_CBV(Resource):
    def get(self):
        pass

    def post(self):
        pass



usrApi.add_resource(Usr_CBV, '/users', endpoint='users')
