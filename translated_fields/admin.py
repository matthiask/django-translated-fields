from django.contrib.admin.options import BaseModelAdmin
from django.contrib.admin.utils import display_for_field
from django.core.exceptions import FieldDoesNotExist
from django.utils.text import capfirst


__all__ = ("TranslatedFieldAdmin",)


class TranslatedFieldAdmin(BaseModelAdmin):
    def translated_field_label(self, db_field, language_code):
        return "%s [%s]" % (capfirst(db_field.verbose_name), language_code)

    def translated_field_column(self, field_name):
        try:
            db_field = self.model._meta.get_field(field_name)
        except FieldDoesNotExist:
            return field_name

        language_code = getattr(db_field, "_translated_field_language_code", "")
        if not language_code:
            return field_name

        empty_value_display = self.get_empty_value_display()

        def value(instance):
            return display_for_field(
                db_field.value_from_object(instance), db_field, empty_value_display
            )

        value.admin_order_field = field_name
        value.short_description = self.translated_field_label(db_field, language_code)
        return value

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        language_code = getattr(db_field, "_translated_field_language_code", "")
        if language_code:
            kwargs["label"] = self.translated_field_label(db_field, language_code)
        return super().formfield_for_dbfield(db_field, request, **kwargs)

    def get_list_display(self, request):
        return [self.translated_field_column(f) for f in self.list_display]
