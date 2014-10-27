'''Field classes and related code.'''

import datetime

from lima import abc
from lima import registry


class Field(abc.FieldABC):
    '''Base class for fields.

    Args:
        attr: The optional name of the corresponding attribute.

        get: An optional getter function accepting an object as its only
            parameter and returning the field value.

    When a :class:`Field` has both ``attr`` *and* ``get`` defined (either via
    passing them to the constructor of :class:`Field` or because the subclass
    implements ``attr`` or ``get`` on the class level, ``get`` *always* takes
    precedence.

    If neither ``get`` nor ``attr`` are defined (not per instance and not at
    the class level), :meth:`lima.schema.Schema.dump` tries to get the field
    value by looking for an attribute of the same name the Field has within the
    corresponding :class:`lima.schema.Schema` instance.

    '''
    def __init__(self, *, attr=None, get=None):
        if attr and get:
            msg = 'attr and get must not be provided at the same time.'
            raise ValueError(msg)

        if attr:
            if not isinstance(attr, str) or not str.isidentifier(attr):
                msg = 'attr is not a valid Python identifier: {}'.format(attr)
                raise ValueError(msg)
            self.attr = attr
        if get:
            if not callable(get):
                raise ValueError('get is not callable.')
            self.get = get


class Boolean(Field):
    '''A boolean field.

    currently this class has no additional functionality compared to
    :class:`Field`. Nevertheless it should be used over :class:`Field` when
    referencing boolean values as an indicator for a field's type and to keep
    code future-proof.

    '''
    pass


class Float(Field):
    '''A float field.

    currently this class has no additional functionality compared to
    :class:`Field`. Nevertheless it should be used over :class:`Field` when
    referencing float values as an indicator for a field's type and to keep
    code future-proof.

    '''
    pass


class Integer(Field):
    '''An integer field.

    currently this class has no additional functionality compared to
    :class:`Field`. Nevertheless it should be used over :class:`Field` when
    referencing integer values as an indicator for a field's type and to keep
    code future-proof.

    '''
    pass


class String(Field):
    '''A string field.

    currently this class has no additional functionality compared to
    :class:`Field`. Nevertheless it should be used over :class:`Field` when
    referencing string values as an indicator for a field's type and to keep
    code future-proof.

    '''
    pass


class Date(Field):
    '''A date field.

    '''
    @staticmethod
    def pack(val):
        '''Return a string representation of ``val``.

        Args:
            val: The :class:`datetime.date` object to convert.

        Returns:
            The ISO 8601-representation of ``val`` (``YYYY-MM-DD``).
        '''
        return val.isoformat() if val is not None else None


class DateTime(Field):
    '''A DateTime field.

    '''
    @staticmethod
    def pack(val):
        '''Return a string representation of ``val``.

        Args:
            val: The :class:`datetime.datetime` object to convert.

        Returns:
            The ISO 8601-representation of ``val``
            (``YYYY-MM-DD%HH:MM:SS.mmmmmm+HH:MM`` for
            :class:`datetime.datetime` objects with Timezone
            information and microsecond precision).

        '''
        return val.isoformat() if val is not None else None


class Nested(Field):
    '''A Field referencing another object with it's respective schema.

    Args:
        schema: The schema of the referenced object. This can be specified via
            a schema *object,* a schema *class* (that will get instantiated
            immediately) or the qualified *name* of a schema class (for when
            the named schema has not been defined at the time of the
            :class:`Nested` object's creation). If two or more schema classes
            with the same name exist in different modules, the schema class
            name has to be fully module-qualified (see the :ref:`entry on class
            names <on_class_names>` for clarification of these concepts).
            Schemas defined within a local namespace can not be referenced by
            name.

        attr: The optional name of the corresponding attribute.

        get: An optional getter function accepting an object as its only
            parameter and returning the field value.

        kwargs: Optional keyword arguments to pass to the :class:`Schema`'s
            constructor when the time has come to instance it. Must be empty if
            ``schema`` is a :class:`lima.schema.Schema` object.

    Raises:
        ValueError: If ``kwargs`` are specified even if ``schema`` is a
            :class:`lima.schema.Schema` *object.*

    Examples: ::

        # refer to PersonSchema class
        author = Nested(schema=PersonSchema)

        # refer to PersonSchema class with additional params
        artists = Nested(schema=PersonSchema, exclude='email', many=True)

        # refer to PersonSchema object
        author = Nested(schema=PersonSchema())

        # refer to PersonSchema object with additional params
        # (note that Nested() gets no kwargs)
        artists = Nested(schema=PersonSchema(exclude='email', many=true))

        # refer to PersonSchema per name
        author = Nested(schema='PersonSchema')

        # refer to PersonSchema per name with additional params
        author = Nested(schema='PersonSchema', exclude='email', many=True)

        # refer to PersonSchema per module-qualified name
        # (in case of ambiguity)
        author = Nested(schema='project.persons.PersonSchema')

        # specify attr name as well
        user = Nested(attr='login_user', schema=PersonSchema)

    '''
    def __init__(self, *, schema, attr=None, get=None, **kwargs):
        super().__init__(attr=attr, get=get)

        # in case schema is a Schema object
        if isinstance(schema, abc.SchemaABC):
            if kwargs:
                msg = ('No keyword args must be supplied'
                       'if schema is a Schema object.')
                raise ValueError(msg)
            self.schema_inst = schema

        # in case schema is a schema class
        elif (isinstance(schema, type) and issubclass(schema, abc.SchemaABC)):
            self.schema_inst = schema(**kwargs)

        # in case schema is a schema name: save args for later instantiation
        elif isinstance(schema, str):
            self.schema_inst = None
            self.schema_name = schema
            self.schema_kwargs = kwargs

        # otherwise fail
        else:
            msg = 'Illegal type for schema param: {}'
            raise TypeError(msg.format(type(schema)))

    def pack(self, val):
        '''Return the output of the referenced object's schema's dump method.

        If the referenced object's schema was specified by name at the
        :class:`Nested` field's creation, this is the time when this schema is
        instantiated (this is done only once).

        Args:
            val: The nested object to convert.

        Returns:
            The output of the referenced :class:`lima.schema.Schema`'s
            :meth:`lima.schema.Schema.dump` method.

        '''
        # if schema_inst doesn't exist yet (because a schema class name was
        # supplied to the constructor), find the schema class in the global
        # registry and instantiate it.
        if not self.schema_inst:
            cls = registry.global_registry.get(self.schema_name)
            self.schema_inst = cls(**self.schema_kwargs)

        return self.schema_inst.dump(val) if val is not None else None


type_mapping = {
    bool: Boolean,
    float: Float,
    int: Integer,
    str: String,
    datetime.date: Date,
    datetime.datetime: Date,
}
'''A mapping of native Python types to :class:`Field` classes.

This can be used to automatically create fields for objects you know the
attribute's types of.

'''
