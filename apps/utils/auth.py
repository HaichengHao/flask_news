from functools import wraps
from flask_restful import abort
from flask import request,g
from .jwt_helper import verify_token


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):

        #tips 开始被装饰函数执行前的检查
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            abort(401, message='缺少或格式错误的 Token')

        token = auth_header.split(' ')[1]
        payload = verify_token(token) #tips:对token进行检查
        if not payload:
            abort(401, message='Token 无效或已过期')

        #tips:检查成功后
        # 将用户 ID 注入到 request 上，供后续使用
        request.current_user_id = payload['user_id']
        #tips:或者使用g
        # g.current_user_id = payload['user_id']
        return f(*args, **kwargs) #然后执行被装饰器装饰的函数

    return decorated  #tips:将装饰器返回