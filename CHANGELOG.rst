Change log
==========

`Next version`_
~~~~~~~~~~~~~~~


`0.7`_ (2018-10-17)
~~~~~~~~~~~~~~~~~~~

- Reused Django's own machinery for displaying data in the changelist
  instead of playing catch-up ourselves.
- Moved the ``list_display_column`` helper functionality into the
  ``TranslatedFieldAdmin`` class and made its application automatic as
  long as you're not overriding ``get_list_display``.


`0.6`_ (2018-10-17)
~~~~~~~~~~~~~~~~~~~

- Added an example and an explanation how to best customize the
  administration interface when using django-translated-fields.
- Added Django 2.1 to the Travis CI test matrix (no changes were
  necessary for compatibility).
- Made pull requests not following the black coding style fail.
- Added the "production/stable" development status trove identifier.
- Dropped Python 3.4 from the build matrix.
- Added a ``list_display_column`` helper for showing language codes in
  column titles.


`0.5`_ (2018-06-14)
~~~~~~~~~~~~~~~~~~~

- Replaced the ``verbose_name_with_language`` option and the
  ``verbose_name`` mangling it does with ``TranslatedFieldAdmin`` which
  offers the same functionality, but restricted to the admin interface.


`0.4`_ (2018-06-14)
~~~~~~~~~~~~~~~~~~~

- Switched the preferred quote to ``"`` and started using `black
  <https://pypi.org/project/black/>`_ to automatically format Python
  code.
- Added Python 3.4 to the test matrix.
- Made documentation better.


`0.3`_ (2018-05-03)
~~~~~~~~~~~~~~~~~~~

- Added documentation.
- Converted the ``TranslatedField`` into a descriptor, and made
  available a few useful fields on the descriptor instance.
- Made it possible to set the value of the current language's field, and
  added another keyword argument for replacing the default
  ``attrsetter``.
- Made ``to_attribute`` fall back to the current language.
- Added exports for ``to_attribute``, ``translated_attrgetter`` and
  ``translated_attrsetter`` to ``translated_fields``.
- Added an ``attrgetter`` argument to ``translated_attributes``.


`0.2`_ (2018-04-30)
~~~~~~~~~~~~~~~~~~~

- By default the language is appended to the ``verbose_name`` of
  fields created by ``TranslatedField``. Added the
  ``verbose_name_with_language=True`` parameter to ``TranslatedField``
  which allows skipping this behavior.
- Added a ``languages`` keyword argument to ``TranslatedField`` to
  allow specifying a different set of language-specific fields than the
  default of the ``LANGUAGES`` setting.
- Added a ``attrgetter`` keyword argument to ``TranslatedField`` to
  replace the default implementation of language-specific attribute
  getting.
- Added the possibility to override field keyword arguments for specific
  languages, e.g. to only make a single language field mandatory and
  implement your own fallback via ``attrgetter``.


`0.1`_ (2018-04-18)
~~~~~~~~~~~~~~~~~~~

- Initial release!

.. _0.1: https://github.com/matthiask/django-translated-fields/commit/0710fc8244
.. _0.2: https://github.com/matthiask/django-translated-fields/compare/0.1...0.2
.. _0.3: https://github.com/matthiask/django-translated-fields/compare/0.2...0.3
.. _0.4: https://github.com/matthiask/django-translated-fields/compare/0.3...0.4
.. _0.5: https://github.com/matthiask/django-translated-fields/compare/0.4...0.5
.. _0.6: https://github.com/matthiask/django-translated-fields/compare/0.5...0.6
.. _0.7: https://github.com/matthiask/django-translated-fields/compare/0.6...0.7
.. _Next version: https://github.com/matthiask/django-translated-fields/compare/0.7...master
