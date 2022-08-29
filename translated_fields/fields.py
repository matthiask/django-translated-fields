import contextvars
import re
from contextlib import contextmanager

from django.conf import settings
from django.db.models import Field
from django.utils.functional import lazy
from django.utils.text import capfirst
from django.utils.translation import get_language


__all__ = [
    "show_language_code",
    "TranslatedField",
    "to_attribute",
    "translated_attrgetter",
    "translated_attrsetter",
    "translated_attributes",
]

_show_language_code = contextvars.ContextVar("show_language_code")


@contextmanager
def show_language_code(show):
    token = _show_language_code.set(show)
    yield
    _show_language_code.reset(token)


def _verbose_name_maybe_language_code(verbose_name, language_code):
    def verbose_name_fn():
        _default_show_language_code = False
        if hasattr(settings, 'TRANSLATED_FIELDS'):
            _default_show_language_code = settings.TRANSLATED_FIELDS.get(
                'SHOW_LANGUAGE_CODE',  _default_show_language_code)
        if _show_language_code.get(_default_show_language_code):
            return f"{capfirst(verbose_name)} [{language_code}]"
        return str(verbose_name)

    return lazy(verbose_name_fn, str)()


def to_attribute(name, language_code=None):
    language = language_code or get_language()
    return re.sub(r"[^a-z0-9_]+", "_", (f"{name}_{language}").lower())


def translated_attrgetter(name, field):
    def getter(self):
        language = get_language()
        ret = getattr(
            self,
            to_attribute(name, language),
        )
        if ret is not None and ret != '':
            return ret

        default_fallback_to_sibling_languages = False
        default_fallback_to_default_language = False
        if hasattr(settings, 'TRANSLATED_FIELDS'):
            default_fallback_to_sibling_languages = settings.TRANSLATED_FIELDS.get(
                'GET_FALLBACK_TO_SIBLING_LANGUAGES',  default_fallback_to_sibling_languages)
            default_fallback_to_default_language = settings.TRANSLATED_FIELDS.get(
                'GET_FALLBACK_TO_DEFAULT_LANGUAGE',  default_fallback_to_default_language)

        if default_fallback_to_sibling_languages:
            language_parts = language.split('-')
            del language_parts[-1]  # remove last
            while len(language_parts) != 0:
                language = '-'.join(language_parts)
                att_name = to_attribute(name, language)
                print(language)
                if not hasattr(self, att_name):
                    del language_parts[-1]  # remove last
                    continue

                ret = getattr(
                    self,
                    att_name,
                )
                if ret is not None and ret != '':
                    return ret

                del language_parts[-1]  # remove last

        if default_fallback_to_default_language:
            print(field.languages[0])
            return getattr(
                self,
                to_attribute(name, field.languages[0]),
            )

        return None

    return getter


def translated_attrgetter2(name, field):
    return lambda self: getattr(
        self, to_attribute(name, get_language() or field.languages[0])
    )


def translated_attrsetter(name, field):
    return lambda self, value: setattr(self, to_attribute(name), value)


def translated_attributes(*names, attrgetter=translated_attrgetter):
    # Allow accessing field.languages etc. in the getter
    field = TranslatedField(None)

    def decorator(cls):
        for name in names:
            setattr(cls, name, property(attrgetter(name, field)))
        return cls

    return decorator


class TranslatedField:
    def __init__(
        self, field, specific=None, *, languages=None, attrgetter=None, attrsetter=None
    ):
        self._field = field
        self._specific = specific or {}
        self._attrgetter = attrgetter or translated_attrgetter
        self._attrsetter = attrsetter or translated_attrsetter
        self.languages = list(languages or (
            lang[0] for lang in settings.LANGUAGES))

        # Make space for our fields.
        self.creation_counter = Field.creation_counter
        Field.creation_counter += len(self.languages)

    def contribute_to_class(self, cls, name):
        _n, _p, args, kwargs = self._field.deconstruct()
        fields = []
        verbose_name = kwargs.pop("verbose_name", name)
        for index, language_code in enumerate(self.languages):
            field_kw = dict(kwargs, **self._specific.get(language_code, {}))
            field_kw.setdefault(
                "verbose_name",
                _verbose_name_maybe_language_code(verbose_name, language_code),
            )
            f = self._field.__class__(*args, **field_kw)
            f._translated_field_language_code = language_code
            f.creation_counter = self.creation_counter + index
            attr = to_attribute(name, language_code)
            f.contribute_to_class(cls, attr)
            fields.append(attr)

        setattr(cls, name, self)
        self.fields = fields
        self.short_description = verbose_name

        self._getter = self._attrgetter(name, field=self)
        self._setter = self._attrsetter(name, field=self)

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        return self._getter(obj)

    def __set__(self, obj, value):
        self._setter(obj, value)
