from django.db import models
from django.utils.translation import gettext_lazy as _

from translated_fields import TranslatedField, translated_attributes


@translated_attributes('stuff')
class TestModel(models.Model):
    name = TranslatedField(
        models.CharField(_('name'), max_length=200),
    )
    other = TranslatedField(
        models.CharField(_('other'), max_length=200, blank=True),
    )

    def __str__(self):
        return self.name

    stuff_en = 'eng'
    stuff_de = 'ger'
