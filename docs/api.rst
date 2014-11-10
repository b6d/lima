.. _api:

============
The lima API
============

Please note that the lima API uses a relatively uncommon feature of Python 3:
*Keyword-only arguments.*

.. include:: keyword_only_args.rst.inc


.. _api_abc:

lima.abc
========

.. automodule:: lima.abc
    :members:


.. _api_exc:

lima.exc
========

.. automodule:: lima.exc
    :members:


.. _api_fields:

lima.fields
===========

.. automodule:: lima.fields
    :members:
    :exclude-members: TYPE_MAPPING, type_mapping

    .. autodata:: lima.fields.TYPE_MAPPING
        :annotation: =dict(...)

    .. autodata:: lima.fields.type_mapping
        :annotation: =dict(...)


.. _api_registry:

lima.registry
=============

.. automodule:: lima.registry
    :members:
    :exclude-members: global_registry

    .. autodata:: lima.registry.global_registry
        :annotation: =lima.registry.Registry()


.. _api_schema:

lima.schema
===========

.. automodule:: lima.schema
   :members:


.. _api_util:

lima.util
=========

.. automodule:: lima.util
   :members:
