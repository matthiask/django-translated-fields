from django.contrib import admin

from translated_fields import TranslatedFieldAdmin, list_display_column

from . import models


@admin.register(models.TestModel)
class TestModelAdmin(TranslatedFieldAdmin, admin.ModelAdmin):
    list_display = ("name", "other")


@admin.register(models.ListDisplayModel)
class ListDisplayModelAdmin(admin.ModelAdmin):
    list_display = [
        list_display_column(models.ListDisplayModel, f)
        for f in [
            *models.ListDisplayModel.name.fields,
            *models.ListDisplayModel.choice.fields,
            *models.ListDisplayModel.is_active.fields,
            *models.ListDisplayModel.file.fields,
            "ordering",
            "stuff",
        ]
    ]

    def stuff(self, instance):
        return "stuff"
