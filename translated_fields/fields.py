import re

from django.conf import settings
from django.db.models import Field
from django.utils.functional import keep_lazy_text
from django.utils.translation import get_language


__all__ = (
    'TranslatedField', 'to_attribute', 'translated_attrgetter',
    'translated_attrsetter', 'translated_attributes',
)


def to_attribute(name, language_code=None):
    language = language_code or get_language()
    return re.sub(r'[^a-z0-9_]+', '_', ('%s_%s' % (name, language)).lower())


def translated_attrgetter(name):
    return lambda self: getattr(self, to_attribute(name))


def translated_attrsetter(name):
    return lambda self, value: setattr(self, to_attribute(name), value)


def translated_attributes(*names, attrgetter=translated_attrgetter):
    def decorator(cls):
        for name in names:
            setattr(cls, name, property(attrgetter(name)))
        return cls
    return decorator


@keep_lazy_text
def verbose_name_with_language(verbose_name, language_code):
    return '%s [%s]' % (verbose_name, language_code)


class TranslatedField(object):
    def __init__(self, field, specific=None, *,
                 verbose_name_with_language=True,
                 languages=None, attrgetter=None, attrsetter=None):
        self._field = field
        self._specific = specific or {}
        self._verbose_name_with_language = verbose_name_with_language
        self._attrgetter = attrgetter or translated_attrgetter
        self._attrsetter = attrsetter or translated_attrsetter
        self.languages = list(languages or (l[0] for l in settings.LANGUAGES))

        # Make space for our fields. Can be removed when dropping support
        # for Python<3.6
        self.creation_counter = Field.creation_counter
        Field.creation_counter += len(settings.LANGUAGES)

    def contribute_to_class(self, cls, name):
        _n, _p, args, kwargs = self._field.deconstruct()
        verbose_name = kwargs.pop('verbose_name', name)
        fields = []
        for index, language_code in enumerate(self.languages):
            f = self._field.__class__(
                verbose_name=verbose_name_with_language(
                    verbose_name,
                    language_code,
                ) if self._verbose_name_with_language else verbose_name,
                *args,
                **dict(kwargs, **self._specific.get(language_code, {})),
            )
            f.creation_counter = self.creation_counter + index
            attr = to_attribute(name, language_code)
            f.contribute_to_class(cls, attr)
            fields.append(attr)

        setattr(cls, name, self)
        self.fields = fields
        self.short_description = verbose_name
        self._getter = self._attrgetter(name)
        self._setter = self._attrsetter(name)

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        return self._getter(obj)

    def __set__(self, obj, value):
        self._setter(obj, value)
