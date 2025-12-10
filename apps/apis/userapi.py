import random

from flask_restful import Resource, Api, fields, reqparse, inputs, marshal
from flask import Blueprint, request, abort, g, session
from sqlalchemy.orm.sync import update
from werkzeug.security import generate_password_hash, check_password_hash

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
parser.add_argument('icon', type=FileStorage, location=['file'])


def phone_validator(phone):
    if re.match(r'^1[3-9]\d{9}$', phone):
        return phone
    else:
        raise ValueError('手机号格式有问题')


parser.add_argument('phone', type=phone_validator, location='form')


# tips:定义发送验证码的部分
class SendMessageCBV(Resource):
    def post(self):
        sms_parser = parser.parse_args()
        username = sms_parser.get('username')
        password = sms_parser.get('password')
        phone = sms_parser.get('phone')


# tips:用户登陆和注册
l_and_rParser = parser.copy()  # tips:直接用之前定义的parser的copy
l_and_rParser.add_argument('vcode', type=inputs.regex(r'^\d{4}$'), help='必须输入验证码', required=True,
                           location=['form'])  # tips:添加一个验证码参数解析

# tips:定制输出
lar_fields = {
    'id': fields.Integer,
    'username': fields.String,
    'phone': fields.String
}


class LoginAndRegisterCBV(Resource):
    def post(self):
        args = l_and_rParser.parse_args()
        phone = args.get('phone')  # 输入手机号
        vcode = args.get('vcode')
        password = args.get('password') #也要输入密码，这是更好的写法，不然无法处置用户
        # 因为还是没有申请到个人短信api所以只能先用假的了
        if vcode == '1234':
            # tips:验证码通过之后查找数据库中有没有该电话号码，如果有就作登陆处理，否则作注册处理
            user = User.query.filter(User.phone == phone).first()
            if user:  # tips:如果有就直接是登陆操作
                # tips:记录登陆状态
                token = generate_token(user_id=user.id)  # 根据用户id来生成token
                return {
                    'msg': '登陆成功',
                    'token': token,
                    'user': marshal(user, lar_fields)  # tips:这里用我们自己设置的输出
                }, 200
            else:
                # tips:先随机生成一个用户名
                s = f'用户{phone[4:9]}'

                new_user = User(phone=phone, username=s,password=generate_password_hash(password,salt_length=8))
                db.session.add(new_user)
                db.session.commit()
                return {'msg': '注册成功'}


        else:
            return {'error': '验证码错误'}, 400


# tips:定义申请重置密码的路由   ,这次我们也要给前端传入图形验证码，但在前后端分离当中，我们只需要传入验证码，图片的绘制交给前端来操作
mfvcode_parser = parser.copy()  # 由于会用到手机号，所以我们还是先要copy
mfvcode_parser.add_argument('imgcode', type=inputs.regex(r'^[a-zA-Z0-9]{6}$'), required=True, location=['form'],
                            help='请输入正确格式的验证码')  # 然后添加一个图形验证码的输入位置


class MofyPwdCBV(Resource):
    def get(self):
        captcha, _ = generate_captcha(6)  # 因为我们只需要返回验证码而不再需要图片，所以只需要取出第一个返回值即可
        session['captcha'] = captcha
        return {
            'captcha': captcha,
        }
        # tips:上面测试返回验证码成功，下面就涉及到输入，一个输入的是手机号，一个输入的是图形验证码的code

    # def post(self):
    #     captcha = session['captcha']
    #     return {
    #         'captcha': captcha,
    #     }
    # 测试成功

    def post(self):
        mfvcode_args = mfvcode_parser.parse_args()
        phonenum = mfvcode_args.get('phone')
        imgcode = mfvcode_args.get('imgcode')
        res = User.query.filter(User.phone == phonenum).first()
        if not res:  # 如果没有查询到手机号就返回有误让重新输入
            return {
                'msg': '用户不存在，请检查手机号后重新输入'
            }
        else:  # 如果手机号查询到就进行密码验证
            if imgcode.lower() != session.get('captcha').lower():
                return {
                    'msg': 'error,验证码输入有误'
                }, 400
            # 如果检测成功就跳到输入手机验证码的界面并进行密码的修改操作
            # tips:由于短信服务还是没有申请成功，所以还是得用假的短信验证码操作接下来的代码
            else:  # 如果成功了应该转到更新密码的接口
                pass


# tips:更新密码
# update_parser=reqparse.RequestParser()
# update_parser.add_argument('phonevcode', type=inputs.regex(r'^\d{4}$'), help='必须输入手机验证码',
#                            location=['form'])  # tips:定义接收手机验证码
# update_parser.add_argument('newpwd', type=inputs.regex(r'^(?=.*\d)(?=.*[a-z])(?=.*[A-Z])[a-zA-Z0-9]{8,10}$'),
#                            required=True, location=['form'],
#                            help='8-10位，含大小写字母和数字,无特殊符号')  # 强密码，8-10位含大小写和数字
# update_parser.add_argument('renewpwd', type=inputs.regex(r'^(?=.*\d)(?=.*[a-z])(?=.*[A-Z])[a-zA-Z0-9]{8,10}$'),
#                            required=True, location=['form']) #和之前学的wtform不同的是这里没有可以方便检验二者是否相同的工具


# 或者不用定义直接拿之前的那个
update_parser = l_and_rParser.copy()
update_parser.add_argument('newpwd', type=inputs.regex(r'^(?=.*\d)(?=.*[a-z])(?=.*[A-Z])[a-zA-Z0-9]{8,10}$'),
                           required=True, location=['form'],
                           help='8-10位，含大小写字母和数字,无特殊符号')  # 强密码，8-10位含大小写和数字
update_parser.add_argument('renewpwd', type=inputs.regex(r'^(?=.*\d)(?=.*[a-z])(?=.*[A-Z])[a-zA-Z0-9]{8,10}$'),
                           required=True, location=['form'])  # 和之前学的wtform不同的是这里没有可以方便检验二者是否相同的工具

# class UpdatePwdCBV(Resource):
#
#     def post(self):
#         up_args = update_parser.parse_args()
#         pwd = up_args.get('newpwd')
#         rpwd = up_args.get('renewpwd')
#         phone_num = up_args.get('phone')
#         phonevcode = up_args.get('vcode')  # 因为这里copy的parser里头写的就是vcode,所以直接这样写就行,还有就是因为没有真正的短信验证所以这里用假的。。。
#         if pwd != rpwd:
#             return {
#                 'msg': '两次输入密码不一致'
#             }, 400
#         if phonevcode != '1234':
#             return {
#                 'msg': '请输入正确的短信验证码'
#             }, 400
#
#         # 如果成功后要对密码进行数据库级别的更新
#         # 因为我们做了.copy(),所以不用验证有没有存在用户了，接下来直接查询就行
#         user = User.query.filter(User.phone == phone_num).first()
#         user.password = generate_password_hash(pwd,salt_length=8)  # 将密码加密
#         db.session.commit()
#         return {
#             'msg': '密码更新成功!'
#         }, 200
#

# 密码更新成功之后就会到登陆界面了

login_parser = l_and_rParser.copy().remove_argument('vcode')
login_parser.add_argument('pwd', required=True, location=['form'])


# class LoginCBV(Resource):
class USRCBV(Resource):

    def post(self):
        lg_args = login_parser.parse_args()
        phone = lg_args.get('phone')
        pwd = lg_args.get('pwd')
        user = User.query.filter(User.phone == phone).first()
        if not user:
            return {'msg': '用户不存在请重新输入'}
        else:
            if check_password_hash(user.password, pwd) == False:  # 检查密码,返回布尔值
                return {
                    'msg': '密码错误'
                }
            else:
                return {
                    'msg': 'success'
                }, 200

    def put(self):  # 整合，将updatepwd整合进来，用put方法修饰
        up_args = update_parser.parse_args()
        pwd = up_args.get('newpwd')
        rpwd = up_args.get('renewpwd')
        phone_num = up_args.get('phone')
        phonevcode = up_args.get('vcode')  # 因为这里copy的parser里头写的就是vcode,所以直接这样写就行,还有就是因为没有真正的短信验证所以这里用假的。。。
        if pwd != rpwd:
            return {
                'msg': '两次输入密码不一致'
            }, 400
        if phonevcode != '1234':
            return {
                'msg': '请输入正确的短信验证码'
            }, 400

        # 如果成功后要对密码进行数据库级别的更新
        # 因为我们做了.copy(),所以不用验证有没有存在用户了，接下来直接查询就行
        user = User.query.filter(User.phone == phone_num).first()
        user.password = generate_password_hash(pwd, salt_length=8)  # 将密码加密
        db.session.commit()
        return {
            'msg': '密码更新成功!'
        }, 200


# tips:定义用户信息页面
class UserProfileCBV(Resource):
    @login_required
    def get(self):
        user_id = request.current_user_id
        # user_id=g.current_user_id tips:或者使用g
        user = User.query.get(user_id)
        if not user:
            abort(400, message='用户不存在')
        return marshal(user, resp_fields)


usrApi.add_resource(UserProfileCBV, '/profile', endpoint='profile')
usrApi.add_resource(LoginAndRegisterCBV, '/login_vc', endpoint='loginvc')  # tips:设置的这个是通过验证码登陆的
usrApi.add_resource(MofyPwdCBV, '/mofycode', endpoint='mofycode')
# usrApi.add_resource(UpdatePwdCBV, '/update_pwd', endpoint='update_pwd') #整合掉了
# usrApi.add_resource(LoginCBV,'/login', endpoint='login') #整合掉了
usrApi.add_resource(USRCBV, '/user', endpoint='user')
