'''Schema class and related code.'''

import collections.abc
import textwrap

from lima import abc
from lima import exc
from lima import registry


### Helper functions ##########################################################

def _into_list_if_str(obj):
    '''Return [obj] if obj is a string, else return obj unchanged.

    This is for convenience: It allows to specify a single string (like
    ``'foo'``) instead of a list containing a single string (like ``['foo']``)
    in cases where iterables of strings are required.

    It is also to guard against iterating over the individual characters of a
    single string when forgetting the brackets.

    '''
    return [obj] if isinstance(obj, str) else obj


def _ensure_iterable(obj):
    '''Raise TypeError if obj is not iterable.'''
    if not isinstance(obj, collections.abc.Iterable):
        msg = 'value is not iterable.'
        raise TypeError(msg)


def _ensure_mapping(obj):
    '''Raise TypeError if obj is no mapping'''
    if not isinstance(obj, collections.abc.Mapping):
        msg = 'value is not a mapping.'
        raise TypeError(msg)


def _ensure_disjoint(a, b):
    '''Raise ValueError if collections a and b are not disjoint'''
    common = set(a) & set(b)
    if common:
        msg = 'Collections contain common element(s).'
        raise ValueError('{}: {}'.format(msg, common))


def _ensure_subset(a, b):
    '''Raise ValueError if collection a is no subset of collection b'''
    missing = set(a) - set(b)
    if missing:
        msg = 'Collection contains element(s) not present in other.'
        raise ValueError('{}: {}'.format(msg, missing))


def _fields_include(fields, include):
    '''Validate args and return union of field dicts.'''
    _ensure_mapping(include)
    _ensure_disjoint(fields, include)
    return dict(fields, **include)  # union of 2 dicts


def _fields_exclude(fields, remove):
    '''Return a copy of fields with fields mentioned in exclude missing.'''
    _ensure_iterable(remove)
    _ensure_subset(remove, fields)
    return {k: v for k, v in fields.items() if k not in remove}


def _fields_only(fields, only):
    '''Return a copy of fields containing only fields mentioned in only.'''
    _ensure_iterable(only)
    _ensure_subset(only, fields)
    return {k: fields[k] for k in only}


### Schema Metaclass ##########################################################

class SchemaMeta(type):
    '''Metaclass of Schema.

    .. note::
       The metaclass :class:`SchemaMeta` is used internally to simplify the
       configuration of new :class:`Schema` classes. For users of the library
       there should be no need to use :class:`SchemaMeta` directly.

    When defining a new :class:`Schema` (sub)class, :class:`SchemaMeta` makes
    sure that the new class has a class attribute :attr:`__fields__` of type
    ``dict`` containing the fields for the new Schema.

    :attr:`__fields__` is determined like this:

    - The :attr:`__fields__` dicts of all base classes are copied (with base
      classes specified first having precedence). (Note that the fields
      themselves are not copied - changing an inherited field changes this
      field for all the base classes as well. This behaviour might change in
      the future. In general, it's good practice *not* to change fields once
      created.)
    - Fields (Class variables of type :class:`lima.abc.FieldABC`) are moved out
      of the class dict and into the :attr:`__fields__` dict.
    - If present, the class attribute :attr:`__lima_args__` is removed from the
      class dict and evaluated as follows:

      - Fields specified via an optional dict ``__lima_args__['include']`` are
        added (overriding any fields of the same name present therein).
      - Fields named in an optional sequence ``__lima_args__['exclude']`` are
        removed. If only one field is to be removed, it's ok to supply a simple
        string instead of a list containing only one string.

    :class:`SchemaMeta` also makes sure the new Schema class is registered with
    the lima class registry :mod:`lima.registry` (at least if the Schema isn't
    defined inside a local namespace, where we wouldn't find it later on).

    '''
    def __new__(mcls, name, bases, dct):
        # determine Schema base classes
        schema_bases = [b for b in bases if isinstance(b, SchemaMeta)]

        # fields of base classes (bases listed first have precedence)
        fields = {}
        for base in reversed(schema_bases):
            fields.update(base.__fields__)

        # pop fields defined as class vars from the new class's dict
        for k, v in list(dct.items()):
            if isinstance(v, abc.FieldABC):
                fields[k] = dct.pop(k)

        # pop and evaluate __lima_args__ (if specified)
        if '__lima_args__' in dct:
            args = dct.pop('__lima_args__')

            # fail on unknown args
            unknown_args = set(args) - {'include', 'exclude'}
            if unknown_args:
                msg = 'Illegal key(s) for __lima_args__: {}'
                raise ValueError(msg.format(unknown_args))

            # add fields specified via include
            if 'include' in args:
                fields = _fields_include(fields, args['include'])

            # remove fields specified via exclude
            if 'exclude' in args:
                exclude = _into_list_if_str(args['exclude'])
                fields = _fields_exclude(fields, exclude)

        # set new _fields class variable
        dct['__fields__'] = fields

        # Try to register class. Classes defined in local namespaces can not
        # be registered. We're ok with this.
        cls = super().__new__(mcls, name, bases, dct)
        try:
            registry.global_registry.register(cls)
        except exc.RegisterLocalClassError:
            pass

        #return class
        return cls


### Schema ####################################################################

class Schema(abc.SchemaABC, metaclass=SchemaMeta):
    '''Base class for Schemas.

    Args:
        exclude: A sequence of field names to be removed from the fields of the
            new :class:`Schema` instance. If only one field is to be removed,
            it's ok to supply a simple string instead of a list containing only
            one string for ``exclude``. ``exclude`` may not be specified
            together with ``only``.

        only: A sequence of the names of the only fields that shall remain for
            the new :class:`Schema` instance.  If just one field is to remain,
            it's ok to supply a simple string instead of a list containing only
            one string for ``only``. ``only`` may not be specified together
            with ``exclude``.

        many: A boolean indicating if the new Schema will be serializing single
            objects (``many=False``) or collections of objects (``many=True``)
            per default. This can later be overridden in the :meth:`dump`
            Method.

    Upon creation, each Schema object gets an internal mapping of field names
    to fields.

    This mapping starts out as a copy of the classes :attr:`__fields__`
    attribute. (Note that the fields themselves are not copied - changing a
    field for a Schema instance changes this field for the class and all base
    classes as well. This behaviour might change in the future. In general,
    it's good practice *not* to change fields once created.)

    The internal mapping and is then modified depending the arguments supplied
    to the :class:`Schema`'s constructor:

    For an explanation on how the class's :attr:`__fields__` attribute is
    determined, see :class:`SchemaMeta`.

    Also upon creation, each Schema object gets an individually created dump
    function that aims to unroll most of the loops and to minimize the number
    of attribute lookups, resulting in a little speed gain on serialization.

    :class:`Schema` classes defined outside of local namespaces can be
    referenced by name (used by :class:`lima.fields.Nested`).

    '''
    def __init__(self, *, exclude=None, only=None, many=False):
        fields = self.__class__.__fields__.copy()
        if exclude and only:
            msg = "Can't specify exclude and only at the same time."
            raise ValueError(msg)
        if exclude:
            exclude = _into_list_if_str(exclude)
            fields = _fields_exclude(fields, exclude)
        if only:
            only = _into_list_if_str(only)
            fields = _fields_only(fields, only)

        self._fields = fields
        self.many = many

        code = self._get_dump_function_code()

        # this defines _dump_function in self's namespace
        exec(code, self.__dict__)

    def _get_dump_function_code(self):
        '''Add a dump function to self.

        Args:
            verbose:
                If True, print the code of the created dump function to stdout.
        '''
        # note that even though dump_function looks like a method at first
        # glance, it is NOT, since it will tied to a specific Schema instance
        # instead of to the Schema class like a method would be. This means
        # that ten Schema objects will have ten separate dump functions
        # associated with them.
        tpl = textwrap.dedent(
            '''def _dump_function(ser, obj):
                return {{
                    {dict_contents}
                }}
            '''
        )
        parts = []
        for field_num, (field_name, field) in enumerate(self._fields.items()):

            if hasattr(field, 'get'):
                # in case the field has a getter, add getter-shortcut to self
                getter_name = '__get_{}'.format(field_num)
                setattr(self, getter_name, field.get)

                # determine val to serialize by calling the shortcut later on
                determine_val = 'ser.{}(obj)'.format(getter_name)

            elif hasattr(field, 'attr'):
                # otherwise if attr is specified, use it to determine val

                # try to guard against code injection
                if not str.isidentifier(field.attr):
                    msg = 'Not a valid identifier: "{}"'
                    raise ValueError(msg.format(field.attr))

                determine_val = 'obj.{}'.format(field.attr)

            else:
                # otherwise the attribute name is assumed to be the field name

                # try to guard against code injection
                if not str.isidentifier(field_name):
                    msg = 'Not a valid identifier: "{}"'
                    raise ValueError(msg.format(field_name))

                determine_val = 'obj.{}'.format(field_name)

            if hasattr(field, 'pack'):
                # in case the field has a "pack" method, add shortcut to self
                packer_name = '__pack_{}'.format(field_num)
                setattr(self, packer_name, field.pack)

                # determine serialized value by calling packer shortcut on
                # result of determine_val-call later on
                determine_val = 'ser.{}({})'.format(packer_name, determine_val)

            # try to guard against code injection
            key = str(field_name)
            if '"' in key or "'" in key:
                msg = 'Quotes are not allowed in field names: {}'
                raise ValueError(msg.format(key))

            parts.append('"{}": {}'.format(key, determine_val))

        sep = ',\n        '
        code = tpl.format(dict_contents=sep.join(parts))
        return code

    def dump(self, obj, *, many=None):
        '''Return a marshalled representation of obj.

        Args:
            obj: The object (or collection of objects) to marshall.

            many: Wether obj is a single object or a collection of objects. If
                ``many`` is ``None``, the value of the instance's
                :attr:`many` attribute is used.

        Returns:
            A representation of ``obj`` in the form of a JSON-serializable
            dict, with each entry corresponding to one of the :class:`Schema`'s
            fields. (Or a list of such dicts in case a collection of objects
            was marshalled)

        '''
        dump_function = self._dump_function
        if many is None:
            many = self.many
        if many:
            return [dump_function(self, o) for o in obj]
        else:
            return dump_function(self, obj)
