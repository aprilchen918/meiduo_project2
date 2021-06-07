from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.


class User(AbstractUser):
    """Custom user model class"""

    mobile = models.CharField(max_length=11, unique=True, verbose_name='手机号')

    class Meta:
        db_table = 'tb_user'   # Custom table name
        verbose_name = '用户'
        verbose_name_plural = verbose_name      # Show the name in Admin site

    def __str__(self):
        return self.username   # Used for test
