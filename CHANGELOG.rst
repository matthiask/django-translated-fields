==========
Change log
==========

`Next version`_
~~~~~~~~~~~~~~~

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
.. _Next version: https://github.com/matthiask/django-translated-fields/compare/0.2...master
