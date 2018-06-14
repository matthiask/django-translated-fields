from django.contrib.admin.options import BaseModelAdmin
from django.utils.text import capfirst


__all__ = ("TranslatedFieldAdmin",)


class TranslatedFieldAdmin(BaseModelAdmin):
    def formfield_for_dbfield(self, db_field, request, **kwargs):
        language_code = getattr(db_field, "_translated_field_language_code", "")
        if language_code:
            kwargs["label"] = "%s [%s]" % (
                capfirst(db_field.verbose_name),
                language_code,
            )
        return super().formfield_for_dbfield(db_field, request, **kwargs)
