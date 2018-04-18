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
