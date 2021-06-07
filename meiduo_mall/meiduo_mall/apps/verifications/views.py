from django.shortcuts import render
from django.views import View
from django_redis import get_redis_connection
from django import http
import random, logging

from verifications.libs.captcha.captcha import captcha
from meiduo_mall.utils.response_code import RETCODE
from . import constants
from verifications.libs.twilio1.twilio_sms import Twilio
from celery_tasks.sms.tasks import send_sms_code
# Create your views here.


# Create logger
logger = logging.getLogger('django')


class SMSCodeView(View):
    """SMS verify code"""
    def get(self, request, mobile):
        """
        :param mobile: phone number
        :return: JSON
        """
        # Receive parameters(image_code and uuid)
        image_code_client = request.GET.get('image_code')     # Custom key: image_code, which should be the same with front end
        uuid = request.GET.get('uuid')

        # Verify parameters
        if not all([image_code_client, uuid]):
            return http.HttpResponseForbidden('缺少必传参数')

        # Create object which connect redis
        redis_conn = get_redis_connection('verify_code')

        # Check whether user send sms code too often
        send_flag = redis_conn.get('send_flag_%s' % mobile)
        if send_flag:
            return http.JsonResponse({'code': RETCODE.THROTTLINGERR, 'errmsg': '发送短信过于频繁'})

        # Get image code
        image_code_server = redis_conn.get('img_%s' % uuid)
        if image_code_server is None:
            return http.JsonResponse({'code': RETCODE.IMAGECODEERR, 'errmsg': '图形验证码已失效'})
        # Delete image code
        redis_conn.delete(('img_%s' % uuid))
        # Verify image code
        image_code_server = image_code_server.decode()
        if image_code_client.lower() != image_code_server.lower():
            return http.JsonResponse({'code': RETCODE.IMAGECODEERR, 'errmsg': '输入图形验证码有误'})

        # Generate sms code: Random six digits
        sms_code = '%06d' % random.randint(0,999999)
        logger.info(sms_code)  # Manual output log, record sms code
        # # Store sms code
        # redis_conn.setex('sms_%s' % mobile, constants.SMS_CODE_REDIS_EXPIRES, sms_code)
        # # Store the tag of sending sms code
        # redis_conn.setex('send_flag_%s' % mobile, constants.SEND_SMS_CODE_INTERVAL, 1)

        # Create redis pipeline
        pl = redis_conn.pipeline()
        # Add commands to queue
        # Store sms code
        pl.setex('sms_%s' % mobile, constants.SMS_CODE_REDIS_EXPIRES, sms_code)
        # Store the tag of sending sms code
        pl.setex('send_flag_%s' % mobile, constants.SEND_SMS_CODE_INTERVAL, 1)
        # Execute
        pl.execute()

        # Send sms code
        # Twilio().send_sms(sms_code, constants.SMS_CODE_REDIS_EXPIRES//60, mobile, constants.SEND_SMS_TEMPLATE_ID)
        # constants.SMS_CODE_REDIS_EXPIRES//60 = 5
        # Use Celery send sms code
        # send_sms_code(mobile, sms_code)  # Wrong writing
        send_sms_code.delay(mobile, sms_code)  # Don't forget delay

        # Response result
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': '发送短信成功'})


class ImageCodeView(View):
    """ Image code verification """

    def get(self, regest, uuid):
        """

        :param uuid: Uniquely identifies the user to which the graphic CAPTCHA belongs
        :return: image:jpg
        """
        # 1. Generate image code
        text, image = captcha.generate_captcha()

        # 2. Store image text
        redis_conn = get_redis_connection('verify_code')
        # redis_conn.setex('key', 'expires', 'value')
        redis_conn.setex('img_%s' % uuid, constants.IMAGE_CODE_REDIS_EXPIRES, text)

        # 3. Response image code
        return http.HttpResponse(image, content_type='image/jpg')