import random

from flask_restful import Resource, Api, fields, reqparse,inputs,marshal
from flask import Blueprint,request,abort,g,session


from apps.models.user import User
from exts.dbhelper import db
from apps.utils.auth import login_required
from apps.utils.jwt_helper import generate_token
from apps.utils.captchagen import generate_captcha
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

#tips:用户登陆和注册
l_and_rParser=parser.copy() #tips:直接用之前定义的parser的copy
l_and_rParser.add_argument('vcode',type=inputs.regex(r'^\d{4}$'),help='必须输入验证码',required=True,location=['form']) #tips:添加一个验证码参数解析

#tips:定制输出
lar_fields={
    'id':fields.Integer,
    'username':fields.String,
    'phone':fields.String
}
class LoginAndRegisterCBV(Resource):
    def post(self):
        args = l_and_rParser.parse_args()
        phone = args.get('phone') #输入手机号
        vcode = args.get('vcode')
        #因为还是没有申请到个人短信api所以只能先用假的了
        if vcode == '1234':
            #tips:验证码通过之后查找数据库中有没有该电话号码，如果有就作登陆处理，否则作注册处理
            user = User.query.filter(User.phone==phone).first()
            if user: #tips:如果有就直接是登陆操作
                #tips:记录登陆状态
                token=generate_token(user_id=user.id)#根据用户id来生成token
                return {
                    'msg':'登陆成功',
                    'token':token,
                    'user':marshal(user,lar_fields) #tips:这里用我们自己设置的输出
                },200
            else:
                #tips:先随机生成一个用户名
                s=''

                new_user=User(phone=phone,username=s)
                db.session.add(new_user)
                db.session.commit()
                return {'msg':'注册成功'}


        else:
            return {'error':'验证码错误'},400

#tips:定义重置密码的路由   ,这次我们也要给前端传入图形验证码，但在前后端分离当中，我们只需要传入验证码，图片的绘制交给前端来操作
class MofyPwdCBV(Resource):
    def get(self):
        captcha,_=generate_captcha(6)#因为我们只需要返回验证码而不再需要图片，所以只需要取出第一个返回值即可
        session['captcha'] = captcha
        return {
            'captcha':captcha,
        }


#tips:定义用户信息页面
class UserProfileCBV(Resource):
    @login_required
    def get(self):
        user_id = request.current_user_id
        # user_id=g.current_user_id tips:或者使用g
        user = User.query.get(user_id)
        if not user:
            abort(404, message='用户不存在')
        return marshal(user, resp_fields)



usrApi.add_resource(UserProfileCBV, '/profile', endpoint='profile')
usrApi.add_resource(LoginAndRegisterCBV, '/login_vc', endpoint='loginvc')  #tips:设置的这个是通过验证码登陆的
usrApi.add_resource(MofyPwdCBV,'/mofycode',endpoint='mofycode')

