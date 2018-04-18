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
    return '%s (%s)' % (verbose_name, language_code.upper())


class TranslatedField(object):
    def __init__(self, field):
        # TODO allow disabling append_language_to_verbose_name?
        self.name, self.path, self.args, self.kwargs = field.deconstruct()
        self.verbose_name = self.kwargs.pop('verbose_name', None)

        # Make space for our fields. Can be removed when dropping support
        # for Python<3.6
        self.creation_counter = Field.creation_counter
        Field.creation_counter += len(settings.LANGUAGES)

    def contribute_to_class(self, cls, name):
        field = import_string(self.path)

        for language_code, _l in settings.LANGUAGES:
            f = field(
                verbose_name=verbose_name_with_language(
                    self.verbose_name or self.name,
                    language_code,
                ),
                *self.args,
                **self.kwargs
            )
            f.creation_counter = self.creation_counter
            self.creation_counter += 1
            f.contribute_to_class(cls, to_attribute(name, language_code))

        getter = translated_attrgetter(name)
        getter.short_description = self.verbose_name or self.name
        setattr(cls, name, property(getter))
