from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

from bold_voice.common.models import TimestampModel


class User(AbstractUser):
    email = models.EmailField(verbose_name=_('email address'))
    email_verified = models.BooleanField(verbose_name=_('email verified'), default=False)

    avatar = models.URLField(verbose_name=_('avatar'), max_length=2048, blank=True)

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')

    def __str__(self):
        return self.email
