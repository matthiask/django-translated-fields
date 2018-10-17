from django.conf import settings

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
