from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


class TimestampModel(models.Model):
    """
    An abstract model that provides self-updating fields 'created_at' and 'modified_at'
    to track the creation and modification timestamps of a model instance.
    """
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='%(class)s_created'
    )
    modified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='%(class)s_modified'
    )

    created_at = models.DateTimeField(verbose_name=_('created at'), auto_now_add=True)
    modified_at = models.DateTimeField(verbose_name=_('modified at'), auto_now=True)

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        if hasattr(self, '_current_user'):
            if not self.pk:
                self.created_by = self._current_user
            self.modified_by = self._current_user
        super().save(*args, **kwargs)
