import jwt
from datetime import datetime,timedelta
from flask import current_app
from settings import Config
#tips:从配置中读取SECRET_KEY
SECRET_KEY = Config.SECRET_KEY
print(SECRET_KEY)
def generate_token(user_id:int)->str:
    payload={
        'user_id':user_id,
        'exp':datetime.utcnow() + timedelta(hours=24), #24小时过期
        'iat':datetime.utcnow(),
    }
    return jwt.encode(payload,SECRET_KEY,algorithm='HS256')

def verify_token(token:str)->dict|None:
    try:
        payload=jwt.decode(token,SECRET_KEY,algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return None  #过期
    except jwt.InvalidTokenError:
        return None  #无效
