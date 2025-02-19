from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager

# Create your models here.
class User(AbstractUser):
    username    = models.CharField('username', max_length=150, blank=False, null=False, unique=True)
    password    = models.CharField('password', max_length=128)
    email       = models.EmailField('email', unique=True)
    is_active   = models.BooleanField(default=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    last_login  = models.DateTimeField(default=None, null=True)
    # default fields
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'account_user'