========================
django-translated-fields
========================

.. image:: https://travis-ci.org/matthiask/django-translated-fields.svg?branch=master
   :target: https://travis-ci.org/matthiask/django-translated-fields

Django model translation without magic-inflicted pain.


Installation and usage
======================

After installing ``django-translated-fields`` into your Python
environment all you have to do is define ``LANGUAGES`` and adding
translated fields to your models::

    from django.db import models
    from django.utils.translation import gettext_lazy as _

    from translated_fields import TranslatedField

    class Question(models.Model):
        question = TranslatedField(
            models.CharField(_('question'), max_length=200),
        )
        answer1 = TranslatedField(
            models.CharField(_('answer 1'), max_length=200),
        )
        answer2 = TranslatedField(
            models.CharField(_('answer 2'), max_length=200),
        )
        answer3 = TranslatedField(
            models.CharField(_('answer 3'), max_length=200, blank=True),
        )

        def __str__(self):
            return self.question


Basic usage
===========

Model fields are automatically created from the field passed to
``TranslatedField``, one field per language. The ``TranslatedField``
instance is a `descriptor
<https://docs.python.org/3/howto/descriptor.html>`_ which by default
acts as a property for the current language's field::

    question = Question(
        question_en='How are you?',
        question_de='Wie geht es Dir?',
        question_fr='Ça va?',
    )

    with translation.override('en'):
        assert question.question == 'How are you?'
    with translation.override('de'):
        assert question.question == 'Wie geht es Dir?'

    with translation.override('fr'):
        question.question = 'Comment vas-tu?'

    assert question.question_fr == 'Comment vas-tu?'


Overriding attribute access (defaults, fallbacks)
=================================================

There are no default values or fallbacks, only a wrapped attribute
access. This can be overridden by specifying your own ``attrgetter`` and
``attrsetter`` functions. E.g. you may want to specify a fallback to the
default language (and at the same time allow leaving other languages'
fields empty)::

    from translated_fields import to_attribute

    def fallback_to_default(name):
        def getter(self):
            return getattr(
                self,
                to_attribute(name),
            ) or getattr(
                self,
                # First language acts as fallback:
                to_attribute(name, settings.LANGUAGES[0][0]),
            )
        return getter

    class Question(models.Model):
        question = TranslatedField(
            models.CharField(_('question'), max_length=200, blank=True),
            {settings.LANGUAGES[0][0]: {'blank': False}},
            attrgetter=fallback_to_default,
        )

Custom ``attrsetter`` functions are also possible. The difference is
that the function passed as ``attrsetter`` should return a function
which accepts two arguments, the model instance and a value.


Disabling ``verbose_name`` manipulation
=======================================

By default, ``TranslatedField`` appends the language code in brackets to
the localized fields' ``verbose_name`` attribute. If this is not desired
for some reason, add ``verbose_name_with_language=False`` to the
``TranslatedField`` instantiation.


``TranslatedField`` instance API
================================

The ``TranslatedField`` descriptor has a few useful attributes (sticking
with the model and field from the examples above):

* ``Question.question.fields`` contains the names of all automatically
  generated fields, e.g. ``['question_en', 'question_...`, ...]``.
* ``Question.question.languages`` is the list of language codes.
* ``Question.question.short_description`` is set to the ``verbose_name``
  of the base field, so that the translatable attribute can be nicely
  used e.g. in ``ModelAdmin.list_display``.


Using a different set of languages
==================================

It is also possible to override the list of language codes used, for
example if you want to translate a sub- or superset of
``settings.LANGUAGES``. Combined with ``attrgetter`` and ``attrsetter``
there is nothing stopping you from using this field for a different kind
of translations, not necessarily bound to ``django.utils.translation``
or even languages at all.


Translated attributes without model field creation
==================================================

If model field creation is not desired, you may also use the
``translated_attributes`` class decorator. This only creates the
attribute getter property::

    from translated_fields import translated_attributes

    @translated_attributes('attribute', 'anything', ...)
    class Test(object):
        attribute_en = 'some value'
        attribute_de = 'some other value'


Other features
==============

There is no support for automatically referencing the current language's
field in queries or automatically adding fields to admin fieldsets and
whatnot. The code required for these features isn't too hard to write,
but it is hard to maintain down the road which contradicts my goal of
writing `low maintenance software
<https://406.ch/writing/low-maintenance-software/>`_. Still, feedback
and pull requests are very welcome! Please run the style checks and test
suite locally before submitting a pull request though -- all that this
requires is running `tox <https://tox.readthedocs.io/>`_.
