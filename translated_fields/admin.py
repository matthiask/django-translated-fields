from django.contrib.admin.options import BaseModelAdmin

from translated_fields.fields import show_language_code


__all__ = ("TranslatedFieldAdmin",)


class TranslatedFieldAdmin(BaseModelAdmin):
    def changelist_view(self, *args, **kwargs):
        with show_language_code(True):
            response = super().changelist_view(*args, **kwargs)
            response.render()
            return response

    def changeform_view(self, *args, **kwargs):
        with show_language_code(True):
            response = super().changeform_view(*args, **kwargs)
            response.render()
            return response
