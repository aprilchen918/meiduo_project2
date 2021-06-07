# Custom user authorization backend: implement multiple accounts login
from django.contrib.auth.backends import ModelBackend
import re

from users.models import User


def get_user_by_account(account):
    """
    Get user by account
    :param account: mobile or username
    :return: user
    """
    try:
        if re.match(r'^\d{10}$', account):
            user = User.objects.get(mobile=account)
        else:
            user = User.objects.get(username=account)
    except User.DoesNotExist:
        return None
    else:
        return user


class UsernameMobileBackend(ModelBackend):
    """Custom user authorization backend"""

    def authenticate(self, request, username=None, password=None, **kwargs):
        """
        Rewrite user authorization method
        :param username: username or mobile
        :param password: password
        :param kwargs: username
        :return: user
        """
        # Query user
        user = get_user_by_account(username)

        # If find user, verify whether password is correct
        if user and user.check_password(password):
            return user
        else:
            return None