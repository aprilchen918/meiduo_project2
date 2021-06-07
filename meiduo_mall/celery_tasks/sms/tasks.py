# Define task
from celery_tasks.sms.twilio1.twilio_sms import Twilio
from . import constants
from celery_tasks.main import celery_app


# Use Decorator to decorate asynchronous task to ensure celery recognize task
@celery_app.task(name='send_sms_code')
def send_sms_code(mobile, sms_code):
    """
    Send sms code's asynchronous task
    :param mobile: phone num
    :param sms_code:  sms code
    :return: success:0, fall: -1
    """
    send_ret = Twilio().send_sms(sms_code, constants.SMS_CODE_REDIS_EXPIRES//60, mobile, constants.SEND_SMS_TEMPLATE_ID)
    return send_ret