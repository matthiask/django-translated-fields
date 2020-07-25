import inspect
import re
import warnings
import contextvars
from contextlib import contextmanager

from django.conf import settings
from django.db.models import Field
from django.utils.translation import get_language
from django.utils.functional import lazy
from django.utils.text import capfirst


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
def show_language_code(show=True):
    token = _show_language_code.set(show)
    yield
    _show_language_code.reset(token)


def _verbose_name_maybe_language_code(verbose_name, language_code):
    def verbose_name_fn():
        if _show_language_code.get(False):
            return "%s [%s]" % (capfirst(verbose_name), language_code)
        return str(verbose_name)

    return lazy(verbose_name_fn, str)()


def to_attribute(name, language_code=None):
    language = language_code or get_language()
    return re.sub(r"[^a-z0-9_]+", "_", ("%s_%s" % (name, language)).lower())


def translated_attrgetter(name, field):
    return lambda self: getattr(
        self,
        to_attribute(
            name, field.languages[0] if get_language() is None else get_language()
        ),
    )


def translated_attrsetter(name, field):
    return lambda self, value: setattr(self, to_attribute(name), value)


def translated_attributes(*names, attrgetter=translated_attrgetter):
    def decorator(cls):
        for name in names:
            setattr(cls, name, property(attrgetter(name, None)))
        return cls

    return decorator


def _optional_keywords(fn, *args, **kwargs):
    params = inspect.signature(fn).parameters
    if kwargs.keys() - params.keys():
        warnings.warn(
            "%s has unsupported arguments: %s"
            % (
                getattr(fn, "__name__", fn),
                ", ".join(sorted(kwargs.keys() - params.keys())),
            ),
            DeprecationWarning,
        )
    return fn(*args, **{key: value for key, value in kwargs.items() if key in params})


class TranslatedField(object):
    def __init__(
        self, field, specific=None, *, languages=None, attrgetter=None, attrsetter=None
    ):
        self._field = field
        self._specific = specific or {}
        self._attrgetter = attrgetter or translated_attrgetter
        self._attrsetter = attrsetter or translated_attrsetter
        self.languages = list(languages or (lang[0] for lang in settings.LANGUAGES))

        # Make space for our fields. Can be removed when dropping support
        # for Python<3.6
        self.creation_counter = Field.creation_counter
        Field.creation_counter += len(settings.LANGUAGES)

    def contribute_to_class(self, cls, name):
        _n, _p, args, kwargs = self._field.deconstruct()
        fields = []
        verbose_name = kwargs.get("verbose_name", name)
        for index, language_code in enumerate(self.languages):
            f = self._field.__class__(
                *args, **dict(kwargs, **self._specific.get(language_code, {}))
            )
            f._translated_field_language_code = language_code
            f.creation_counter = self.creation_counter + index
            f.verbose_name = _verbose_name_maybe_language_code(
                verbose_name, language_code
            )
            attr = to_attribute(name, language_code)
            f.contribute_to_class(cls, attr)
            fields.append(attr)

        setattr(cls, name, self)
        self.fields = fields
        self.short_description = verbose_name

        self._getter = _optional_keywords(self._attrgetter, name, field=self)
        self._setter = _optional_keywords(self._attrsetter, name, field=self)

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        return self._getter(obj)

    def __set__(self, obj, value):
        self._setter(obj, value)
