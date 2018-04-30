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
            # The language is appended to the verbose_name of fields by
            # default . If you do not want this, add the following
            # argument:
            # verbose_name_with_language=False,

            # The default is to take [lang[0] for lang in LANGUAGES]
            # languages=None,

            # The default implementation returns the attribute related
            # to ``translation.get_language``. Pass a callable receiving
            # the translated field's name and returning a callable which
            # has ``self`` as its only argument.
            # attrgetter=None,
        )

        def __str__(self):
            return self.question


Model fields are automatically created from the field passed to
``TranslatedField``, one field per language. The ``TranslatedField``
instance itself is replaced with a property which returns the current
language's attribute. There are no default values or fallbacks, only a
wrapped attribute access.

If model field creation is not desired, you may also use the
``translated_attributes`` class decorator. This only creates the
attribute getter property::

    from translated_fields import translated_attributes

    @translated_attributes('attribute', 'anything', ...)
    class Test(object):
        attribute_en = 'some value'
        attribute_de = 'some other value'


There is no support for automatically referencing the current language's
field in queries or automatically adding fields to admin fieldsets and
whatnot. The code required for these features isn't too hard to write,
but it is hard to maintain down the road which contradicts my goal of
writing `low maintenance software
<https://406.ch/writing/low-maintenance-software/>`_. Still, feedback
and pull requests are very welcome! Please run the style checks and test
suite locally before submitting a pull request though -- all that this
requires is running `tox <https://tox.readthedocs.io/>`_.
