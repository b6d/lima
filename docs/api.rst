.. _api:

============
The lima API
============

.. module:: lima

Please note that the lima API uses a relatively uncommon feature of Python 3:
*Keyword-only arguments.*

.. include:: keyword_only_args.rst.inc


.. _api_fields:

lima.fields
===========

.. automodule:: lima.fields
    :members:
    :exclude-members: type_mapping

    .. autodata:: lima.fields.type_mapping
        :annotation: =dict(...)


.. _api_schema:

lima.schema
===========

.. automodule:: lima.schema
   :members:


.. _api_enums:

lima.enums
=============

.. automodule:: lima.enums
    :members:


.. _api_exc:

lima.exc
=============

.. automodule:: lima.exc
    :members:


.. _api_abc:

lima.abc
=============

.. automodule:: lima.abc
    :members:


.. _api_registry:

lima.registry
=============

.. automodule:: lima.registry
    :members:
    :exclude-members: global_registry

    .. autodata:: lima.registry.global_registry
        :annotation: =lima.registry.Registry()
