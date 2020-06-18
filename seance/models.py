from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class AdvUser(AbstractUser):
    email = models.EmailField(verbose_name=_('email address'), blank=True, null=True)
    wallet = models.FloatField(blank=True, null=True, verbose_name=_('wallet'))
    was_deleted = models.BooleanField(default=False, verbose_name=_('was deleted?'))
    last_activity = models.DateTimeField(auto_now_add=True, blank=True, null=True,
                                         verbose_name=_('user\'s last activity was: '))

    def delete(self, *args, **kwargs):
        self.is_active = False
        self.was_deleted = True
        self.save()

