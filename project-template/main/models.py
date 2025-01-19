from django.db import models
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.utils import timezone

from main.auth.instances import UserPrincipal


class User(UserPrincipal, AbstractBaseUser):
    """
    Use a custom user right from the start since it in theory
    lets us avoid installing the django.contrib.auth app and
    more easily ties into our auth system.
    """

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = BaseUserManager()

    email = models.EmailField(
        unique=True
    )
    is_active = models.BooleanField(
        default=True
    )
    date_joined = models.DateTimeField(default=timezone.now)
