# import uuid
# key = f"captcha:{uuid.uuid4().hex()}"
# print(key)

import uuid
print("uuid module file:", uuid.__file__)
print("uuid.uuid4 type:", type(uuid.uuid4))
print("uuid.uuid4 value:", repr(uuid.uuid4))

# 尝试调用
try:
    result = uuid.uuid4()
    print("Call success:", result.hex)
except Exception as e:
    print("Call failed:", e)