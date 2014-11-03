=========
Changelog
=========

0.3 (unreleased)
================

.. note::

    While unreleased, the changelog of lima 0.3 is itself subject to change.

- Support dumping of ``OrderedDict`` objects by providing ``ordered=True`` to
  Schema constructor

- Add New possibilities to specify a schema's fields:

    - Add support for ``__lima_args__['only']`` on schema definition

    - Add *include* parameter to Schema constructor

  This makes specifying fields on schema definition (``__lima_args__`` -
  options *include*, *exclude*, *only*) consistent with specifying fields on
  schema instantiation (schema constructor args *include*, *exclude*, *only*).


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
