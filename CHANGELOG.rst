=========
Changelog
=========

0.4 (unreleased)
================

.. note::

    While unreleased, the changelog of lima 0.4 is itself subject to change.

- **Breaking Change:** The ``Schema.dump`` method no longer supports the
  ``many`` argument. This makes ``many`` consistent with ``ordered`` and
  simplifies internals.

- Improve support for serializing linked data:

    - Add new field type ``fields.Reference`` for references to linked objects.

    - Add new name for ``fields.Nested``: ``fields.Embed``. Deprecate
      ``fields.Nested`` in favour of ``fields.Embed``.

- Add read-only properties ``many`` and ``ordered`` for schema objects.

- Don't generate docs for internal modules any more - those did clutter up the
  documentation of the actual API (the docstrings remain though).

- Implement lazy evaluation and caching of some attributes (affects methods:
  ``Schema.dump``, ``Embed.pack`` and ``Reference.pack``). This means stuff is
  only evaluated if and when really needed, but it also means:

    - The very first time data is dumped/packed by a Schema/Embed/Reference
      object, there will be a tiny delay. Keep objects around to mitigate this
      effect.

    - Some errors might surface at a later time. lima mentions this when
      raising exceptions though.

- Allow quotes in field names.

- Small speed improvement when serializing collections.

- Remove deprecated field ``fields.type_mapping``. Use ``fields.TYPE_MAPPING``
  instead.

- Overall cleanup, improvements and bug fixes.


0.3.1 (2014-11-11)
==================

- Fix inconsistency in changelog.


0.3 (2014-11-11)
================

- Support dumping of ``OrderedDict`` objects by providing ``ordered=True`` to
  a Schema constructor.

- Implement field name mangling: ``at__foo`` becomes ``@foo`` for fields
  specified as class attributes.

- Support constant field values by providing ``val`` to a Field constructor.

- Add new ways to specify a schema's fields:

    - Add support for ``__lima_args__['only']`` on schema definition

    - Add *include* parameter to Schema constructor

  This makes specifying fields on schema definition (``__lima_args__`` -
  options *include*, *exclude*, *only*) consistent with specifying fields on
  schema instantiation (schema constructor args *include*, *exclude*, *only*).

- Deprecate ``fields.type_mapping`` in favour of ``fields.TYPE_MAPPING``.

- Improve the documentation.

- Overall cleanup, improvements and bug fixes.


0.2.2 (2014-10-27)
==================

- Fix issue with package not uploading to PYPI

- Fix tiny issues with illustration


0.2.1 (2014-10-27)
==================

- Fix issues with docs not building on readthedocs.org


0.2 (2014-10-27)
================

- Initial release
