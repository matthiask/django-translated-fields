from django.conf import settings
from django.utils.text import capfirst

from .fields import TranslatedField, to_attribute


__all__ = ["TranslatedFieldWithFallback", "fallback_to_default"]


def fallback_to_default(name):
    def getter(self):
        return getattr(self, to_attribute(name)) or getattr(
            self, to_attribute(name, settings.LANGUAGES[0][0])
        )

    return getter


class TranslatedFieldWithFallback(TranslatedField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("attrgetter", fallback_to_default)
        super().__init__(*args, **kwargs)
        for language in self.languages[1:]:
            # Only the primary language is required
            self._specific.setdefault(language, {})["blank"] = True


def language_code_formfield_callback(db_field, **kwargs):
    language_code = getattr(db_field, "_translated_field_language_code", "")
    if language_code:
        kwargs["label"] = "%s [%s]" % (capfirst(db_field.verbose_name), language_code)
    return db_field.formfield(**kwargs)


def reverse_field(field_name, languages=None, exclude=[]):
    """Reverse a field name to list the field with all the languages

    Args:
        field_name (str): the field to be reversed without language codes.
        languages (list, optional): Reverse only on the provided
            language codes. Defaults to the languages defined in the settings.
        exclude (list, optional): Ignore language codes in this list.

    Examples:

        >>> get_field_names("name", languages=["en", "es"])
        ["name_en", "name_es"]

    Returns:
        A list of field names with appended language codes.

    """
    if not languages:
        languages = (l[0] for l in settings.LANGUAGES)
    return [
        "{0}_{1}".format(field_name, lang) for lang in languages if lang not in exclude
    ]
