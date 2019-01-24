import itertools

from django.contrib import admin

from translated_fields import TranslatedFieldAdmin

from . import models


@admin.register(models.TestModel)
class TestModelAdmin(TranslatedFieldAdmin, admin.ModelAdmin):
    list_display = ("name", "other")


@admin.register(models.ListDisplayModel)
class ListDisplayModelAdmin(TranslatedFieldAdmin, admin.ModelAdmin):
    list_display = list(
        itertools.chain.from_iterable(
            [
                models.ListDisplayModel.name.fields,
                models.ListDisplayModel.choice.fields,
                models.ListDisplayModel.is_active.fields,
                models.ListDisplayModel.file.fields,
                ["ordering", "stuff"],
            ]
        )
    )

    def stuff(self, instance):
        return "stuff"
