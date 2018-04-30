import re

from django.conf import settings
from django.db.models import Field
from django.utils.functional import keep_lazy_text
from django.utils.module_loading import import_string
from django.utils.translation import get_language


__all__ = ('TranslatedField', 'translated_attributes')


def to_attribute(name, language):
    return re.sub(r'[^a-z0-9_]+', '_', ('%s_%s' % (name, language)).lower())


def translated_attrgetter(name):
    return lambda self: getattr(self, to_attribute(name, get_language()))


def translated_attributes(*names):
    def decorator(cls):
        for name in names:
            setattr(cls, name, property(translated_attrgetter(name)))
        return cls

    return decorator


@keep_lazy_text
def verbose_name_with_language(verbose_name, language_code):
    return '%s [%s]' % (verbose_name, language_code)


class TranslatedField(object):
    def __init__(
            self,
            field,
            specific=None,
            *,
            verbose_name_with_language=True,
            languages=None,
            attrgetter=None
    ):
        self.name, self.path, self.args, self.kwargs = field.deconstruct()
        self.verbose_name = self.kwargs.pop('verbose_name', None)
        self._specific = specific or {}
        self._verbose_name_with_language = verbose_name_with_language
        self._languages = languages or [l[0] for l in settings.LANGUAGES]
        self._attrgetter = attrgetter or translated_attrgetter

        # Make space for our fields. Can be removed when dropping support
        # for Python<3.6
        self.creation_counter = Field.creation_counter
        Field.creation_counter += len(settings.LANGUAGES)

    def contribute_to_class(self, cls, name):
        field = import_string(self.path)

        for language_code in self._languages:
            f = field(
                verbose_name=verbose_name_with_language(
                    self.verbose_name or self.name,
                    language_code,
                ) if self._verbose_name_with_language else self.verbose_name,
                *self.args,
                **dict(self.kwargs, **self._specific.get(language_code, {})),
            )
            f.creation_counter = self.creation_counter
            self.creation_counter += 1
            f.contribute_to_class(cls, to_attribute(name, language_code))

        getter = self._attrgetter(name)
        getter.short_description = self.verbose_name or self.name
        setattr(cls, name, property(getter))
