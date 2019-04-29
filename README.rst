========================
django-translated-fields
========================

.. image:: https://travis-ci.org/matthiask/django-translated-fields.svg?branch=master
   :target: https://travis-ci.org/matthiask/django-translated-fields

Version |release|

Django model translation without magic-inflicted pain.


Installation and usage
======================

After installing ``django-translated-fields`` in your Python
environment all you have to do is define ``LANGUAGES`` in your
settings and add translated fields to your models:

.. code-block:: python

    from django.db import models
    from django.utils.translation import gettext_lazy as _

    from translated_fields import TranslatedField

    class Question(models.Model):
        question = TranslatedField(
            models.CharField(_("question"), max_length=200),
        )
        answer = TranslatedField(
            models.CharField(_("answer"), max_length=200),
        )

        def __str__(self):
            return self.question


Basic usage
===========

Model fields are automatically created from the field passed to
``TranslatedField``, one field per language.  For example, with
``LANGUAGES = [("en", "English"), ("de", "German"), ("fr", "French")]``,
the following list of fields would be created: ``question_en``,
``question_de``, ``question_fr``, ``answer_en``, ``answer_de``,
and ``answer_fr``.

This implies that when changing ``LANGUAGES`` you'll have to run
``makemigrations`` and ``migrate`` too.

No ``question`` or ``answer`` model field is actually created. The
``TranslatedField`` instance is a `descriptor
<https://docs.python.org/3/howto/descriptor.html>`_ which by default
acts as a property for the current language's field:

.. code-block:: python

    from django.utils.translation import override

    question = Question(
        question_en="How are you?",
        question_de="Wie geht es Dir?",
        question_fr="Ça va?",
    )

    # The default getter automatically returns the value
    # in the current language:
    with override("en"):
        assert question.question == "How are you?"

    with override("de"):
        assert question.question == "Wie geht es Dir?"

    # The default setter can also be used to set the value
    # in the current language:
    with override("fr"):
        question.question = "Comment vas-tu?"

    assert question.question_fr == "Comment vas-tu?"

``TranslatedField`` has a ``fields`` attribute that returns a list of all
the language fields created.

.. code-block:: python

    answer = Question(
        answer_en="Very well!",
        answer_de="Gut!",
        answer_fr="Ça va bien!"
    )

    assert answer.answer.fields == ["answer_en", "answer_de", "answer_fr"]

For more attributes look at the *``TranslatedField`` instance API*
section below.

Changing field attributes per language
======================================

It is sometimes useful to have slightly differing model fields per
language, e.g. for making the primary language mandatory. This can be
achieved by passing a dictionary with keyword arguments per language as
the second positional argument to ``TranslatedField``.

For example, if you add a language to ``LANGUAGES`` when a site is
already running, it might be useful to make the new language
non-mandatory to simplify editing already existing data through Django's
administration interface.

The following example adds ``blank=True`` to the spanish field:

.. code-block:: python

    from translated_fields import TranslatedField

    class Question(models.Model):
        question = TranslatedField(
            models.CharField(_("question"), max_length=200),
            {"es": {"blank": True}},
        )


Overriding attribute access (defaults, fallbacks)
=================================================

There are no default values or fallbacks, only a wrapped attribute
access. The default attribute getter and setter functions simply return
or set the field for the current language (as returned by
``django.utils.translation.get_language``). Note that the default getter
and setter do not check whether a language is activated at all, or
whether the field even exists (which might be the case when overriding
``languages``). This implies that the getter might raise an
``AttributeError`` and the setter might set an attribute on the model
instance not related to a model field.

Both getters and setters can be overridden by specifying your own
``attrgetter`` and ``attrsetter`` functions. E.g. you may want to
specify a fallback to the default language (and at the same time allow
leaving other languages' fields empty):

.. code-block:: python

    from django.conf import settings
    from translated_fields import TranslatedField, to_attribute

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
            models.CharField(_("question"), max_length=200, blank=True),
            {settings.LANGUAGES[0][0]: {"blank": False}},
            attrgetter=fallback_to_default,
        )

A custom ``attrsetter`` which always sets all fields follows (probably
not very useful, but hopefully instructive):

.. code-block:: python

    def set_all_fields(name):
        def setter(self, value):
            for field in getattr(self.__class__, name).fields:
                setattr(self, field, value)
        return setter


``TranslatedField`` instance API
================================

The ``TranslatedField`` descriptor has a few useful attributes (sticking
with the model and field from the examples above):

* ``Question.question.fields`` contains the names of all automatically
  generated fields, e.g. ``["question_en", "question_...", ...]``.
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
attribute getter property:

.. code-block:: python

    from translated_fields import translated_attributes

    @translated_attributes("attribute", "anything", ...)
    class Test(object):
        attribute_en = "some value"
        attribute_de = "some other value"


Model admin support
===================

The ``TranslatedFieldAdmin`` class adds the respective language to the
label of individual fields. Instead of three fields named "Question"
you'll get the fields "Question [en]", "Question [de]" and "Question
[fr]". It intentionally offers no functionality except for modifying the
label of fields:

.. code-block:: python

    from django.contrib import admin
    from translated_fields import TranslatedFieldAdmin
    from .models import Question

    @admin.register(Question)
    class QuestionAdmin(TranslatedFieldAdmin, admin.ModelAdmin):
        pass

    # For inlines:
    # class SomeInline(TranslatedFieldAdmin, admin.StackedInline):
    #     ...

As mentioned above, the ``fields`` attribute on the ``TranslatedField``
instance contains the list of generated fields. This may be useful if
you want to customize various aspects of the ``ModelAdmin`` subclass. An
example showing various techniques follows:

.. code-block:: python

    from django.contrib import admin
    from django.utils.translation import gettext_lazy as _
    from translated_fields import TranslatedFieldAdmin, to_attribute
    from .models import Question

    @admin.register(Question)
    class QuestionAdmin(TranslatedFieldAdmin, admin.ModelAdmin):
        # Pack question and answer fields into their own fieldsets:
        fieldsets = [
            (_("question"), {"fields": Question.question.fields}),
            (_("answer"), {"fields": Question.answer.fields}),
        ]

        # Show all fields in the changelist:
        list_display = [
            *Question.question.fields,
            *Question.answer.fields
        ]

        # Order by current language's question field:
        def get_ordering(self, request):
            return [to_attribute("question")]

.. note::
   It's strongly recommended to set the ``verbose_name`` of fields when
   using ``TranslatedFieldAdmin``, the first argument of most model
   fields. As example relating to the `question model
   <https://github.com/matthiask/django-translated-fields#installation-and-usage>`_,
   use ``verbose_name="Question"`` instead ``_("question")``.
   Otherwise, you'll get duplicated languages, e.g. "Question en
   [en]".


Forms
=====

django-translated-fields provides a helper when you want form fields'
labels to contain the language code. If this sounds useful to you do
this:

.. code-block:: python

    from django import forms
    from translated_fields.utils import language_code_formfield_callback
    from .models import Question

    class QuestionForm(forms.ModelForm):
        formfield_callback = language_code_formfield_callback

        class Meta:
            model = Question
            fields = [
                *Question.question.fields,
                *Question.answer.fields
            ]


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
