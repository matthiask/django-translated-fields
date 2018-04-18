import re

from django.utils.functional import keep_lazy_text
from django.utils.translation import get_language


def to_attr(name):
    return re.sub(r'[^a-z0-9_]+', '_', name.lower())


def translated_attributes(*attributes):
    def prop(attr):
        return property(lambda self: getattr(
            self,
            to_attr('%s_%s' % (attr, get_language())),
        ))

    def decorator(cls):
        for attribute in attributes:
            setattr(cls, attribute, prop(attribute))
        return cls

    return decorator


@keep_lazy_text
def verbose_name_with_language(verbose_name, language_code):
    return '%s (%s)' % (verbose_name, language_code.upper())


class TranslatedField(object):
    def __init__(self, field):
        self.name, self.path, self.args, self.kwargs = field.deconstruct()
        self.verbose_name = self.kwargs.pop('verbose_name', None)

    def contribute_to_class(self, cls, name):
        from django.conf import settings
        from django.utils.module_loading import import_string

        field = import_string(self.path)

        for language_code, _l in settings.LANGUAGES:
            field(
                verbose_name=verbose_name_with_language(
                    self.verbose_name or self.name,
                    language_code,
                ),
                *self.args,
                **self.kwargs
            ).contribute_to_class(
                cls,
                to_attr('%s_%s' % (name, language_code)),
            )

        def getter(self):
            return getattr(
                self,
                to_attr('%s_%s' % (name, get_language())),
            )
        getter.short_description = self.verbose_name or self.name
        setattr(cls, name, property(getter))
