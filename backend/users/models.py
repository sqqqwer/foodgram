from django.contrib.auth.models import AbstractUser
from django.db import models

from foodgram.constants import (STR_OUTPUT_LIMIT, USER_CHAR_MAX_LENGHT,
                                USER_EMAIL_MAX_LENGHT)


class User(AbstractUser):
    email = models.EmailField(
        'Почта',
        unique=True,
        max_length=USER_EMAIL_MAX_LENGHT
    )
    first_name = models.CharField('Имя', max_length=USER_CHAR_MAX_LENGHT)
    last_name = models.CharField('Фамилия', max_length=USER_CHAR_MAX_LENGHT)
    avatar = models.ImageField('Аватар', null=True,
                               default='', upload_to='users/')
# Зачем переопределять username поле
    REQUIRED_FIELDS = ['email', 'first_name', 'last_name']


class Subscribe(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='subscribe',
        verbose_name='Пользователь'
    )
    subscribe_to = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='subscribes',
        verbose_name='Подписан на'
    )

    class Meta:
        verbose_name = 'подписка'
        verbose_name_plural = 'Подписки'
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'subscribe_to'),
                name='%(app_label)s_%(class)s_prevent_not_unique_subscribe'
            ),
            models.CheckConstraint(
                check=~models.Q(user=models.F('subscribe_to')),
                name='%(app_label)s_%(class)s_prevent_self_subscribe',
            ),
        )

    def __str__(self):
        return f'{self.user}-{self.subscribe_to}'[:STR_OUTPUT_LIMIT]
