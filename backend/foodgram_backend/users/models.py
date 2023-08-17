from django.contrib.auth.models import AbstractUser
from django.db import models

from constants import MAX_USERNAME_FIRST_LAST_PASS_LENGTH, MAX_EMAIL_LENGTH
from .validators import regex_validator


class User(AbstractUser):
    class Meta:
        verbose_name = 'Пользователь'
        ordering = ['username']

    email = models.EmailField(
        verbose_name='Email',
        max_length=MAX_EMAIL_LENGTH,
        unique=True,
        blank=False,
    )
    username = models.CharField(
        verbose_name='Username',
        max_length=MAX_USERNAME_FIRST_LAST_PASS_LENGTH,
        unique=True,
        blank=False,
        validators=[regex_validator],
    )
    first_name = models.CharField(
        verbose_name='Имя',
        max_length=MAX_USERNAME_FIRST_LAST_PASS_LENGTH,
        blank=False,
    )
    last_name = models.CharField(
        verbose_name='Фамилия',
        max_length=MAX_USERNAME_FIRST_LAST_PASS_LENGTH,
        blank=False,
    )
    password = models.CharField(
        verbose_name='Пароль',
        max_length=MAX_USERNAME_FIRST_LAST_PASS_LENGTH,
        blank=False,
    )

    def __str__(self):
        return self.username
