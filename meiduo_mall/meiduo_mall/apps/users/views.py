from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django import http
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import View
from django.db import DatabaseError
from django_redis import get_redis_connection
import re

from users.models import User
from meiduo_mall.utils.response_code import RETCODE

# Create your views here.


class UserInfoView(LoginRequiredMixin,View):
    """User center information page"""

    def get(self, request):
        """Provide user center page"""
        # if request.user.is_authenticated:
        #     return render(request, 'user_center_info.html')
        # else:
        #     return render(reverse('users:login'))
        return render(request, 'user_center_info.html')


class LogoutView(View):
    """User log out"""

    def get(self, request):
        """Implement user logout logic"""
        # Clear status retention information
        logout(request)

        # Logout and then redirect to home page
        response = redirect(reverse('contents:index'))

        # Delete username information in cookies
        response.delete_cookie('username')

        # Response result
        return response


class LoginView(View):
    """User login"""

    def get(self, request):
        return render(request, 'login.html')

    def post(self, request):
        """implement user login logic"""
        # Get and verify parameters
        username = request.POST.get('username')
        password = request.POST.get('password')
        if not all([username, password]):
            return http.HttpResponseForbidden('缺少必传参数')
        if not re.match(r'^[a-zA-Z0-9-_]{5,20}$', username):
            return http.HttpResponseForbidden('请输入5-20个字符的用户名')
        if not re.match(r'^[a-zA-Z0-9]{8,20}$', password):
            return http.HttpResponseForbidden('请输入8-20位的密码')

        remembered = request.POST.get('remembered')

        # Authorize user: use username check whether user is exist, if yes then check password
        user = authenticate(username=username, password=password)
        if user is None:
            return render(request, 'login.html', {'account_errmsg': '密码或账号错误'})

        # Status keep
        login(request, user)
        # Use remembered to determine the status keeping period (implement remember login)
        if remembered != 'on':
            # Not remember login: status keeping will be destroy after end the browser session
            request.session.set_expiry(0)
        else:
            # Remember login: status keeping period is two weeks: default is two weeks
            request.session.set_expiry(None)

        # Response result:
        # Get next
        next = request.GET.get('next')
        # Determine whether next is None
        if next:
            # Redirect to next
            response = redirect(next)
        else:
            # Redirect to home page
            response = redirect(reverse('contents:index'))

            # In order to display the username information in the top right corner of the homepage,
            # we need to cache the username to cookie
            # response.set_cookie('key', 'val', 'expiry')
            response.set_cookie('username', user.username, max_age=3600 * 24 * 14)

        # Response result
        return response


class UsernameCountView(View):
    """Check whether username registered repeatedly"""

    def get(self, request, username):
        """
        :param username: username
        :return: Json
        """
        # Implement main body business logic: use username query the number of response record (filter return set)
        count = User.objects.filter(username=username).count()
        # Response result
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK', 'count': count})


class MobileCountView(View):
    """ Check whether phone number registered repeatedly """

    def get(self, request, mobile):
        count = User.objects.filter(mobile=mobile).count()
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK', 'count': count})



class RegisterView(View):
    """User register"""

    def get(self, request):
        """Provide user register page"""
        return render(request, 'register.html')

    def post(self, request):
        """Implement the user registration business logic"""
        # 1. Receive parameters:
        username = request.POST.get('username')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        mobile = request.POST.get('mobile')
        sms_code_client = request.POST.get('sms_code')
        allow = request.POST.get('allow')

        # 2. Verify parameters: Separate validation on the front and back ends to prevent malicious users from making
        #       requests over the front end logic, To ensure the security of the back end, the validation logic of the
        #       front and back ends is the same.
        # Check if the parameters are complete: all([list]), if one element of the list is none, return false.
        if not all([username, password, password2, mobile, allow]):
            return http.HttpResponseForbidden('缺少必传参数')
        # Determine whether the user name is 5-20 characters
        if not re.match(r'^[a-zA-Z0-9-_]{5,20}$', username):
            return http.HttpResponseForbidden('请输入5-20个字符的用户名')
        # Determine whether the password is 8-20 digits
        if not re.match(r'^[a-zA-Z0-9]{8,20}$', password):
            return http.HttpResponseForbidden('请输入8-20位的密码')
        # Determine whether the two passwords are the same
        if password != password2:
            return http.HttpResponseForbidden('两次输入的密码不一致')
        # Check whether the phone number is valid
        if not re.match(r'^\d{10}$', mobile):
            return http.HttpResponseForbidden('请输入正确的手机号码')
        # Verify sms code
        redis_conn = get_redis_connection('verify_code')
        sms_code_server = redis_conn.get('sms_%s' % mobile)
        if sms_code_server is None:
            return render(request, 'register.html', {'sms_code_errmsg': '短信验证码已失效'})
        sms_code_server = sms_code_server.decode()
        if sms_code_client != sms_code_client:
            return render(request, 'register.html', {'sms_code_errmsg': '输入短信验证码有误'})
        # Check if user protocol is checked
        if allow != 'on':
            return http.HttpResponseForbidden('请勾选用户协议')
        # 3. Store register data: is the core of registration
        # return render(request, 'register.html', {'register_errmsg':'注册失败'})    # for test
        try:
            user = User.objects.create_user(username=username, password=password, mobile=mobile)
        except DatabaseError:
            return render(request, 'register.html', {'register_errmsg':'注册失败'})

        # Implement status keeping
        login(request, user)

        # Response result: redirect to home page
        response = redirect(reverse('contents:index'))

        # In order to display the username information in the top right corner of the homepage,
        # we need to cache the username to cookie
        # response.set_cookie('key', 'val', 'expiry')
        response.set_cookie('username', user.username, max_age=3600 * 24 * 14)

        # 4. Response result
             # return HttpResponse('注册成功，重定向到首页')
            # return redirect('/')
        return response