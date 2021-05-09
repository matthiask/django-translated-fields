from django.db import models
from django.utils.translation import gettext_lazy as _

from translated_fields import (
    TranslatedField,
    TranslatedFieldWithFallback,
    translated_attributes,
)
from translated_fields.utils import fallback_to_any


@translated_attributes("stuff")
class TestModel(models.Model):
    name = TranslatedField(models.CharField(_("name"), max_length=200))
    other = TranslatedField(
        models.CharField(_("other field"), max_length=200, blank=True)
    )

    def __str__(self):
        return self.name

    stuff_en = "eng"
    stuff_de = "ger"


def custom_attrgetter(name, field):
    # Nonsense example.
    return lambda self: self.name_fr or self.name_it or "NO VALUE"


class CustomLanguagesModel(models.Model):
    name = TranslatedField(
        models.CharField(_("name"), max_length=200),
        languages=("fr", "it"),
        attrgetter=custom_attrgetter,
    )


class SpecificModel(models.Model):
    name = TranslatedField(
        models.CharField(_("name"), max_length=200, blank=True),
        {"en": {"blank": False}, "de": {"verbose_name": "Der Name"}},
    )


class ListDisplayModel(models.Model):
    name = TranslatedField(models.CharField(_("name"), max_length=200))
    choice = TranslatedField(
        models.CharField(
            _("choice"), max_length=3, choices=[("a", "Andrew"), ("b", "Betty")]
        )
    )
    is_active = TranslatedField(models.BooleanField(_("is active"), default=True))
    file = TranslatedField(models.FileField(_("file"), blank=True))
    ordering = models.IntegerField(_("ordering"), default=0)


class ModelWithFallback(models.Model):
    required = TranslatedFieldWithFallback(
        models.CharField(_("required"), max_length=20)
    )
    optional = TranslatedFieldWithFallback(
        models.CharField(_("optional"), max_length=20, blank=True)
    )

    def __str__(self):
        return self.required


class ModelWithAnyFallback(models.Model):
    optional = TranslatedField(
        models.CharField(_("optional"), max_length=20, blank=True),
        attrgetter=fallback_to_any,
    )
