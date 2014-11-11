'''Schema class and related code.'''
import keyword
import textwrap
from collections import OrderedDict

from lima import abc
from lima import exc
from lima import registry
from lima import util


# Helper functions ############################################################

def _fields_from_bases(bases):
    '''Return fields determined from a list of base classes'''
    fields = OrderedDict()

    # determine base classes that are actually Schemas by checking if they
    # inherit from abc.SchemaABC
    schema_bases = [b for b in bases if (issubclass(b, abc.SchemaABC) and
                                         b != abc.SchemaABC)]

    # Add fields of base schemas. Bases listed first have precedence (to
    # reflect how python inherits class attributes). Their items are also
    # placed first in the fields OrderedDict (to reflect the order in which the
    # bases are written down in the class definition).
    for base in schema_bases:
        for k, v in base.__fields__.items():
            if k not in fields:
                fields[k] = v

    return fields


def _fields_include(fields, include):
    '''Return a copy of fields with fields in include included.'''
    util.ensure_mapping(include)
    util.ensure_only_instances_of(include, str)
    util.ensure_only_instances_of(include.values(), abc.FieldABC)
    result = fields.copy()
    result.update(include)
    return result


def _fields_exclude(fields, remove):
    '''Return a copy of fields with fields mentioned in exclude missing.'''
    util.ensure_only_instances_of(remove, str)
    util.ensure_subset_of(remove, fields)
    result = OrderedDict()
    for k, v in fields.items():
        if k not in remove:
            result[k] = v
    return result


def _fields_only(fields, only):
    '''Return a copy of fields containing only fields mentioned in only.'''
    util.ensure_only_instances_of(only, str)
    util.ensure_subset_of(only, fields)
    result = OrderedDict()
    for k, v in fields.items():
        if k in only:
            result[k] = v
    return result


def _mangle_name(name):
    '''Return mangled field name.

    Mangled field names have some name prefixes replaced with others (see
    mapping in code). This is to allow some field names with special chars in
    them to be defined via Schema class attributes.

    '''
    mapping = dict(at='@', dash='-', dot='.', hash='#', plus='+', nil='')
    if '__' not in name:
        return name
    before, after = name.split('__', 1)
    if before not in mapping:
        return name
    return mapping[before] + after


# Schema Metaclass ############################################################

class SchemaMeta(type):
    '''Metaclass of Schema.

    .. note::
       The metaclass :class:`SchemaMeta` is used internally to simplify the
       configuration of new :class:`Schema` classes. For users of the library
       there should be no need to use :class:`SchemaMeta` directly.

    When defining a new :class:`Schema` (sub)class, :class:`SchemaMeta` makes
    sure that the new class has a class attribute :attr:`__fields__` of type
    :class:`collections.OrderedDict` containing the fields for the new
    Schema.

    :attr:`__fields__` is determined like this:

    - The :attr:`__fields__` of all base classes are copied (with base classes
      specified first having precedence).

      Note that the fields themselves are *not* copied - changing an inherited
      field would change this field for all base classes referencing this field
      as well. In general it is *strongly* suggested to treat fields as
      immutable.

    - Fields (Class variables of type :class:`lima.abc.FieldABC`) are moved out
      of the class namespace and into :attr:`__fields__`, overriding any fields
      of the same name therein.

    - If present, the class attribute :attr:`__lima_args__` is removed from the
      class namespace and evaluated as follows:

      - Fields specified via ``__lima_args__['include']`` (an optional mapping
        of field names to fields) are inserted into :attr:`__fields__`.
        overriding any fields of the same name therein.

        If the order of your fields is important, make sure that
        ``__lima_args__['include']`` is of type
        :class:`collections.OrderedDict` or similar.

        New fields in ``__lima_args__['include']__`` are inserted at the
        position where ``__lima_args__`` is specified in the class.

      - Fields named in an optional sequence ``__lima_args__['exclude']`` are
        removed from :attr:`__fields__`. If only one field is to be removed,
        it's ok to supply a simple string instead of a list containing only one
        string. ``__lima_args__['exclude']`` may not be specified together with
        ``__lima_args__['only']``.

      - If in an optional sequence ``__lima_args__['only']`` is provided, *all
        but* the fields mentioned therein are removed from :attr:`__fields__`.
        If only one field is to remain, it's ok to supply a simple string
        instead of a list containing only one string. ``__lima_args__['only']``
        may not be specified together with ``__lima_args__['exclude']``.

        Think twice before using ``__lima_args__['only']`` - most of the time
        it's better to rethink your Schema than to remove a lot of fields that
        maybe shouldn't be there in the first place.

    .. versionadded:: 0.3
        Support for ``__lima_args__['only']``.

    :class:`SchemaMeta` also makes sure the new Schema class is registered with
    the lima class registry :mod:`lima.registry` (at least if the Schema isn't
    defined inside a local namespace, where we wouldn't find it later on).

    '''
    def __new__(metacls, name, bases, namespace):

        # aggregate fields from base classes
        fields = _fields_from_bases(bases)

        # pop/verify __lima_args__
        args = namespace.get('__lima_args__', {})
        with util.complain_about('__lima_args__'):
            util.ensure_mapping(args)
            util.ensure_subset_of(args, {'include', 'exclude', 'only'})
            util.ensure_only_one_of(args, {'exclude', 'only'})

        # determine individual args (include, exclude, only)
        include = args.get('include', {})
        exclude = util.vector_context(args.get('exclude', []))
        only = util.vector_context(args.get('only', []))

        # loop over copy of namespace items (we mutate namespace in this loop)
        for k, v in list(namespace.items()):
            if k == '__lima_args__':
                # at position of __lima_args__: insert include (if specified)
                if include:
                    with util.complain_about("__lima_args__['include']"):
                        fields = _fields_include(fields, include)
            elif isinstance(v, abc.FieldABC):
                # if a field was found: move it from namespace into fields
                # (also, mangle its name to allow some special field names)
                fields[_mangle_name(k)] = namespace.pop(k)

        if exclude:
            with util.complain_about('__lima_args__["exclude"]'):
                fields = _fields_exclude(fields, exclude)
        elif only:
            with util.complain_about('__lima_args__["only"]'):
                fields = _fields_only(fields, only)

        # add __fields__ to namespace
        namespace['__fields__'] = fields

        # remove __lima_args__ from namespace (if present)
        namespace.pop('__lima_args__', None)

        # Create the new class. Note that the superclass gets the altered
        # namespace as a common dict explicitly - we don't need an OrderedDict
        # namespace any more at this point.
        cls = super().__new__(metacls, name, bases, dict(namespace))

        # Try to register the new class. Classes defined in local namespaces
        # cannot be registerd. We're ok with this.
        with util.suppress(exc.RegisterLocalClassError):
            registry.global_registry.register(cls)

        # return class
        return cls

    @classmethod
    def __prepare__(metacls, name, bases):
        '''Return an OrderedDict as the class namespace.'''
        return OrderedDict()


# Schema ######################################################################

class Schema(abc.SchemaABC, metaclass=SchemaMeta):
    '''Base class for Schemas.

    Args:
        exclude: An optional sequence of field names to be removed from the
            fields of the new :class:`Schema` instance. If only one field is to
            be removed, it's ok to supply a simple string instead of a list
            containing only one string for ``exclude``. ``exclude`` may not be
            specified together with ``only``.

        only: An optional sequence of the names of the only fields that shall
            remain for the new :class:`Schema` instance.  If just one field is
            to remain, it's ok to supply a simple string instead of a list
            containing only one string for ``only``. ``only`` may not be
            specified together with ``exclude``.

        include: An optional mapping of field names to fields to additionally
            include in the new Schema instance. Think twice before using this
            option - most of the time it's better to include fields at class
            level rather than at instance level.

        ordered: An optional boolean indicating if the :meth:`Schema.dump`
            method should output :class:`collections.OrderedDict` objects
            instead of simple :class:`dict` objects.  Defaults to ``False``.
            This does not influence how nested fields are serialized.

        many: An optional boolean indicating if the new Schema will be
            serializing single objects (``many=False``) or collections of
            objects (``many=True``) per default. This can later be overridden
            in the :meth:`dump` Method.

    .. versionadded:: 0.3
        The ``include`` parameter.

    .. versionadded:: 0.3
        The ``ordered`` parameter.

    Upon creation, each Schema object gets an internal mapping of field names
    to fields. This mapping starts out as a copy of the class's
    :attr:`__fields__` attribute.  (For an explanation on how this
    :attr:`__fields__` attribute is determined, see :class:`SchemaMeta`.)

    Note that the fields themselves are not copied - changing the field of an
    instance would change this field for the other instances and classes
    referencing this field as well. In general it is *strongly* suggested to
    treat fields as immutable.

    The internal field mapping is then modified as follows:

    - If ``include`` was provided, fields specified therein are added
      (overriding any fields of the same name already present)

      If the order of your fields is important, make sure that ``include`` is
      of type :class:`collections.OrderedDict` or similar.

    - If ``exclude`` was provided, fields specified therein are removed.

    - If ``only`` was provided, *all but* the fields specified therein are
      removed (unless ``exclude`` was provided as well, in which case a
      :exc:`ValueError` is raised.)

    Also upon creation, each Schema object gets an individually created dump
    function that aims to unroll most of the loops and to minimize the number
    of attribute lookups, resulting in a little speed gain on serialization.

    :class:`Schema` classes defined outside of local namespaces can be
    referenced by name (used by :class:`lima.fields.Nested`).

    '''
    def __init__(self,
                 *,
                 exclude=None,
                 only=None,
                 include=None,
                 ordered=False,
                 many=False):
        fields = self.__class__.__fields__.copy()
        if exclude and only:
            msg = "Can't specify exclude and only at the same time."
            raise ValueError(msg)

        if include:
            with util.complain_about('include'):
                fields = _fields_include(fields, include)

        if exclude:
            with util.complain_about('exclude'):
                fields = _fields_exclude(fields, util.vector_context(exclude))
        elif only:
            with util.complain_about('only'):
                fields = _fields_only(fields, util.vector_context(only))

        self._fields = fields
        self._ordered = ordered
        self.many = many

        # get code for the customized dump function
        code = self._get_dump_function_code()

        # this defines _dump_function in self's namespace
        exec(code, globals(), self.__dict__)

    def _get_dump_function_code(self):
        '''Get code for a customized dump function.'''
        # note that even _though dump_function might *look* like a method at
        # first glance, it is *not*, since it will tied to a specific Schema
        # instance instead of to the Schema class like a method would be. This
        # means that ten Schema objects will have ten separate dump functions
        # associated with them.

        # get correct templates
        if self._ordered:
            func_tpl = textwrap.dedent(
                '''\
                def _dump_function(schema, obj):
                    return OrderedDict([
                        {contents}
                    ])
                '''
            )
            entry_tpl = '("{key}", {get_val})'
        else:
            func_tpl = textwrap.dedent(
                '''\
                def _dump_function(schema, obj):
                    return {{
                        {contents}
                    }}
                '''
            )
            entry_tpl = '"{key}": {get_val}'

        # one entry per field
        entries = []

        # iterate over fields to fill up entries
        for field_num, (field_name, field) in enumerate(self._fields.items()):

            if hasattr(field, 'val'):
                # add constant-field-value-shortcut to self
                val_name = '__val_{}'.format(field_num)
                setattr(self, val_name, field.val)

                # later, get value using this shortcut
                get_val = 'schema.{}'.format(val_name)

            elif hasattr(field, 'get'):
                # add getter-shortcut to self
                getter_name = '__get_{}'.format(field_num)
                setattr(self, getter_name, field.get)

                # later, get value by calling getter-shortcut
                get_val = 'schema.{}(obj)'.format(getter_name)

            else:
                # neither constant val nor getter: try to get value via attr
                # (if no attr name is specified, use field name as attr name)
                attr = getattr(field, 'attr', field_name)

                if not str.isidentifier(attr) or keyword.iskeyword(attr):
                    msg = 'Not a valid attribute name: {!r}'
                    raise ValueError(msg.format(attr))

                # later, get value using attr
                get_val = 'obj.{}'.format(attr)

            if hasattr(field, 'pack'):
                # add pack-shortcut to self
                packer_name = '__pack_{}'.format(field_num)
                setattr(self, packer_name, field.pack)

                # later, wrap pass result of get_val to pack-shortcut
                get_val = 'schema.{}({})'.format(packer_name, get_val)

            # try to guard against code injection via quotes in key
            key = str(field_name)
            if '"' in key or "'" in key:
                msg = 'Quotes are not allowed in field names: {}'
                raise ValueError(msg.format(key))

            # add entry
            entries.append(entry_tpl.format(key=key, get_val=get_val))

        sep = ',\n        '
        code = func_tpl.format(contents=sep.join(entries))
        return code

    def dump(self, obj, *, many=None):
        '''Return a marshalled representation of obj.

        Args:
            obj: The object (or collection of objects) to marshall.

            many: Wether obj is a single object or a collection of objects. If
                ``many`` is ``None``, the value of the instance's
                :attr:`many` attribute is used.

        Returns:
            A representation of ``obj`` in the form of a JSON-serializable dict
            (or :class:`collections.OrderedDict` if the Schema was created with
            ``ordered==True``), with each entry corresponding to one of the
            :class:`Schema`'s fields. (Or a list of such dicts in case a
            collection of objects was marshalled)

        '''
        dump_function = self._dump_function
        if many is None:
            many = self.many
        if many:
            return [dump_function(self, o) for o in obj]
        else:
            return dump_function(self, obj)
