from django.contrib.admin.options import BaseModelAdmin

from translated_fields.fields import show_language_code


__all__ = ("TranslatedFieldAdmin",)


class TranslatedFieldAdmin(BaseModelAdmin):
    def changelist_view(self, *args, **kwargs):
        with show_language_code(True):  # noqa: FBT003
            response = super().changelist_view(*args, **kwargs)
            if hasattr(response, "render"):
                response.render()
            return response

    def changeform_view(self, *args, **kwargs):
        with show_language_code(True):  # noqa: FBT003
            response = super().changeform_view(*args, **kwargs)
            if hasattr(response, "render"):
                response.render()
            return response
