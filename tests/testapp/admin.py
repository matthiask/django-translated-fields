from django.contrib import admin

from translated_fields import TranslatedFieldAdmin

from . import models


@admin.register(models.TestModel)
class TestModelAdmin(TranslatedFieldAdmin, admin.ModelAdmin):
    list_display = ["name", "other", *models.TestModel.name.fields]
    list_display_links = ["name_en"]
    list_editable = ["name_de"]
    readonly_fields = [*models.TestModel.other.fields]


@admin.register(models.ListDisplayModel)
class ListDisplayModelAdmin(TranslatedFieldAdmin, admin.ModelAdmin):
    list_display = [
        *models.ListDisplayModel.name.fields,
        *models.ListDisplayModel.choice.fields,
        *models.ListDisplayModel.is_active.fields,
        *models.ListDisplayModel.file.fields,
        "ordering",
        "stuff",
    ]

    def stuff(self, instance):
        return "stuff"
