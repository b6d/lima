'''Abstract base classes for fields and schemas.

.. note::

   :mod:`lima.abc` is needed to avoid circular imports of fields needing to
   know about schemas and vice versa. The base classes are used for internal
   type checks. For users of the library there should be no need to use
   :mod:`lima.abc` directly.

'''


class FieldABC:
    '''Abstract base class for fields.

    Inheriting from :class:`FieldABC` marks a class as a field for internal
    type checks.

    (Usually, it's a *way* better Idea to subclass :class:`lima.fields.Field`
    directly)

    '''
    pass


class SchemaABC:
    '''Abstract base class for schemas.

    Inheriting from :class:`SchemaABC` marks a class as a schema for internal
    type checks.

    (Usually, it's a *way* better Idea to subclass :class:`lima.schema.Schema`
    directly)

    '''
    pass
