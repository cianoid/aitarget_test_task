from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    last_name = models.CharField('Фамилия', max_length=150)
    first_name = models.CharField('Имя', max_length=150)
    middle_name = models.CharField('Отчество', max_length=150, blank=True)
    email = models.EmailField('Email')
