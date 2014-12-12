=========
Changelog
=========

0.4 (unreleased)
================

.. note::

    While unreleased, the changelog of lima 0.4 is itself subject to change.

- **Breaking Change:** The ``Schema.dump`` method no longer supports the
  ``many`` argument. Schema instances now either serialize collections of
  objects or single objects, but not both.

- Add new field type ``fields.Reference``.

- Add read-only properties ``Schema.many`` and ``Schema.ordered``.

- Don't create docs for internal modules any more - those did clutter up the
  documentation of the actual API.

- Implement lazy evaluation of some non-public schema and field attributes
  (`Pyramid <http://docs.pylonsproject.org/docs/pyramid/en/latest/api/
  decorator.html#pyramid.decorator.reify>`_ FTW). This means some things (like
  custom dump functions for schema instances) are only evaluated if really
  needed, but it also means that some errors might surface at a later time
  (lima mentions this when raising such exceptions).

- Small speed improvement when serializing collections.

- Deprecate ``fields.Nested`` in favour of ``fields.Embed``.

- Remove ``fields.type_mapping``. Use ``fields.TYPE_MAPPING`` instead.

- Overall cleanup.


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
