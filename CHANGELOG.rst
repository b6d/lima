=========
Changelog
=========

0.4 (unreleased)
================

.. note::

    While unreleased, the changelog of lima 0.4 is itself subject to change.

- Remove ``fields.type_mapping``. Use ``fields.TYPE_MAPPING`` instead.

- Deprecate ``fields.Nested`` in favour of ``fields.Embed``.

- Small speed improvement when serializing collections.

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
