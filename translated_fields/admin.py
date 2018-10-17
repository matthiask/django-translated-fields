from django.contrib.admin.options import BaseModelAdmin
from django.db import models
from django.utils.functional import lazy
from django.utils.text import capfirst


__all__ = ("TranslatedFieldAdmin", "list_display_column")


def list_display_column(model, field_name):
    try:
        db_field = model._meta.get_field(field_name)
    except models.FieldDoesNotExist:
        return field_name

    language_code = getattr(db_field, "_translated_field_language_code", "")
    if not language_code:
        return field_name

    def value(instance):
        if hasattr(instance, "get_%s_display" % db_field.name):
            return getattr(instance, "get_%s_display" % db_field.name)()
        return getattr(instance, field_name)

    value.admin_order_field = field_name
    value.boolean = isinstance(db_field, models.BooleanField)
    value.short_description = lazy(
        lambda: "%s [%s]" % (capfirst(db_field.verbose_name), language_code), str
    )

    return value


class TranslatedFieldAdmin(BaseModelAdmin):
    def formfield_for_dbfield(self, db_field, request, **kwargs):
        language_code = getattr(db_field, "_translated_field_language_code", "")
        if language_code:
            kwargs["label"] = "%s [%s]" % (
                capfirst(db_field.verbose_name),
                language_code,
            )
        return super().formfield_for_dbfield(db_field, request, **kwargs)
