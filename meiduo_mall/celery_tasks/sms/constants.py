# 图形验证码有效期，单位：秒
IMAGE_CODE_REDIS_EXPIRES = 300

# 短信验证码有效期，单位：秒
SMS_CODE_REDIS_EXPIRES = 300

# 短信模板
SEND_SMS_TEMPLATE_ID = 1


def body(user_code, time_limit, tempID):
    body_lib = {
        1: f'Hi, Your user and verification code is {user_code}! Please enter correctly within {time_limit} minutes',
    }
    return body_lib[tempID]

# 60s内是否重复发送的标记
SEND_SMS_CODE_INTERVAL = 60