from django.db import models
from django.utils.translation import gettext_lazy as _


class Label(models.Model):
    name = models.CharField(max_length=200, unique=True, verbose_name=_('Name'))
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return self.name
