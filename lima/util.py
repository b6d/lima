'''Internal utilities.

.. warning::

    For users of lima there should be no need to use anything within
    :mod:`lima.util` directly. Name and contents of this module may change at
    any time without deprecation notice or upgrade path.

'''
from collections import abc, OrderedDict
from contextlib import contextmanager
from keyword import iskeyword
from textwrap import dedent


@contextmanager
def complain_about(name):
    '''A Context manager that makes every Exception about name'''
    try:
        yield
    except Exception as e:
        # adapted from http://stackoverflow.com/a/17677938
        msg = '{}: {}'.format(name, e) if e.args else name
        e.args = (msg, ) + e.args[1:]
        raise


# The code for this class is taken from pyramid.decorator (with negligible
# alterations), licensed under the Repoze Public License (see
# http://www.pylonsproject.org/about/license)
class reify:
    '''Like property, but saves the underlying method's result for later use.

    Use as a class method decorator. It operates almost exactly like the Python
    ``@property`` decorator, but it puts the result of the method it decorates
    into the instance dict after the first call, effectively replacing the
    function it decorates with an instance variable. It is, in Python parlance,
    a non-data descriptor. An example:

    .. code-block:: python

       class Foo(object):
           @reify
           def jammy(self):
               print('jammy called')
               return 1

    And usage of Foo:

    >>> f = Foo()
    >>> v = f.jammy
    'jammy called'
    >>> print(v)
    1
    >>> f.jammy
    1
    >>> # jammy func not called the second time; it replaced itself with 1

    Taken from pyramid.decorator (see source for license info).

    '''
    def __init__(self, wrapped):
        self.wrapped = wrapped
        self.__doc__ = wrapped.__doc__

    def __get__(self, instance, owner):
        if instance is None:
            return self
        val = self.wrapped(instance)
        setattr(instance, self.wrapped.__name__, val)
        return val


# The code for this class is taken directly from the Python 3.4 standard
# library (to support Python 3.3), licensed under the PSF License (see
# https://docs.python.org/3/license.html)
class suppress:
    '''Context manager to suppress specified exceptions

    After the exception is suppressed, execution proceeds with the next
    statement following the with statement.

         with suppress(FileNotFoundError):
             os.remove(somefile)
         # Execution still resumes here if the file was already removed

    Backported for Python 3.3 from Python 3.4 (see source for license info).

    '''
    def __init__(self, *exceptions):
        self._exceptions = exceptions

    def __enter__(self):
        pass

    def __exit__(self, exctype, excinst, exctb):
        # Unlike isinstance and issubclass, CPython exception handling
        # currently only looks at the concrete type hierarchy (ignoring
        # the instance and subclass checking hooks). While Guido considers
        # that a bug rather than a feature, it's a fairly hard one to fix
        # due to various internal implementation details. suppress provides
        # the simpler issubclass based semantics, rather than trying to
        # exactly reproduce the limitations of the CPython interpreter.
        #
        # See http://bugs.python.org/issue12029 for more details
        return exctype is not None and issubclass(exctype, self._exceptions)


def vector_context(obj):
    '''Return obj if obj is a vector, or [obj] in case obj is a scalar.

    For this function, a *vector* is an iterable that's no string. Everything
    else counts as a *scalar*.

    Inspired by Perl's list context (this has nothing to do with Python context
    managers). Useful to provide scalar values to operations that expect
    vectors (so there's no need to put brackets around single elements).

    Args:
        obj: Any object

    Returns:
        ``obj`` if obj is a vector, otherwise ``[obj]``.

    '''
    if isinstance(obj, abc.Iterable) and not isinstance(obj, str):
        return obj
    return [obj]


def ensure_iterable(obj):
    '''Raise TypeError if obj is not iterable.'''
    if not isinstance(obj, abc.Iterable):
        raise TypeError('{!r} is not iterable.'.format(obj))


def ensure_mapping(obj):
    '''Raise TypeError if obj is no mapping.'''
    if not isinstance(obj, abc.Mapping):
        raise TypeError('{!r} is not a mapping.'.format(obj))


def ensure_only_one_of(collection, elements):
    '''Raise ValueError if collection contains more than one of elements.

    Only distinct elements are considered. For mappings, the keys are
    considered.

    Args:
        collection: An iterable container.

        elements: A set of elements that must not appear together.

    Raises:
        ValueError: If *collection* contains more than one (distinct) element
            of *elements*.

    '''
    found = set(collection) & set(elements)
    if len(found) > 1:
        raise ValueError('Mutually exclusive: {!r}'.format(found))


def ensure_subset_of(collection, superset):
    '''Raise ValueError if collection is no subset of superset

    Only distinct elements are considered. For mappings, only the keys are
    considered.

    Args:
        collection: An iterable container.

        superset: A set of allowed elements.

    Raises:
        ValueError: If *collection* contains more than one (distinct) element
            of *elements*.

    '''
    excess = set(collection) - set(superset)
    if excess:
        raise ValueError('Excess element(s): {!r}'.format(excess))


def ensure_only_instances_of(collection, cls):
    '''Raise TypeError, if collection contains elements not of type cls.'''
    found = [obj for obj in collection if not isinstance(obj, cls)]
    if found:
        raise TypeError('No instances of {}: {!r}'.format(cls, found))


def make_function(name, code, globals_=None):
    '''Return a function created by executing a code string in a new namespace.

    This is not much more than a wrapper around :func:`exec`.

    Args:
        name: The name of the function to create. Must match the function name
            in ``code``.

        code: A String containing the function definition code. The name of the
            function must match ``name``.

        globals_: A dict of globals to mix into the new function's namespace.
            ``__builtins__`` must be provided explicitly if required.

    .. warning:

        All pitfalls of using :func:`exec` apply to this function as well.

    '''
    namespace = dict(__builtins__={})
    if globals_:
        namespace.update(globals_)
    exec(code, namespace)
    return namespace[name]


def _cns_field_value(field, field_name, field_num):
    '''Return (code, namespace)-tuple for determining a field's serialized val.

    Args:
        field: A :class:`lima.fields.Field` instance.

        field_name: The name (key) of the field.

        field_num: A schema-wide unique number for the field

    Returns:
        A tuple consisting of: a) a fragment of Python code to determine the
        field's value for an object called ``obj`` and b) a namespace dict
        containing the objects necessary for this code fragment to work.

    For a field ``myfield`` that has a ``pack`` and a ``get`` callable defined,
    the output of this function could look something like this:

    .. code-block:: python

        (
            'pack3(get3(obj))',  # the code
            {'get3': myfield.get, 'pack3': myfield.pack}  # the namespace
        )
    '''
    namespace = {}
    if hasattr(field, 'val'):
        # add constant-field-value-shortcut to namespace
        name = 'val{}'.format(field_num)
        namespace[name] = field.val

        # later, get value using this shortcut
        val_code = name

    elif hasattr(field, 'get'):
        # add getter-shortcut to namespace
        name = 'get{}'.format(field_num)
        namespace[name] = field.get

        # later, get value by calling this shortcut
        val_code = '{}(obj)'.format(name)

    else:
        # neither constant val nor getter: try to get value via attr
        # (if attr is not specified, use field name as attr)
        obj_attr = getattr(field, 'attr', field_name)

        if not str.isidentifier(obj_attr) or iskeyword(obj_attr):
            msg = 'Not a valid attribute name: {!r}'
            raise ValueError(msg.format(obj_attr))

        # later, get value using this attr
        val_code = 'obj.{}'.format(obj_attr)

    if hasattr(field, 'pack'):
        # add pack-shortcut to namespace
        name = 'pack{}'.format(field_num)
        namespace[name] = field.pack

        # later, pass field value to this shortcut
        val_code = '{}({})'.format(name, val_code)

    return val_code, namespace


def _cns_dump_field(field, field_name):
    '''Return (code, namespace)-tuple for a customized dump_field function.

    Args:
        field: The field.

        field_name: The name (key) of the field.

    Returns:
        A tuple consisting of: a) Python code to define the function and b) a
        namespace dict containing objects necessary for this code to work.

    '''
    func_tpl = dedent(
        '''\
        def dump_field(obj, many):
            if many:
                return [{val_code} for obj in obj]
            return {val_code}
        '''
    )
    val_code, namespace = _cns_field_value(field, field_name, 0)
    code = func_tpl.format(val_code=val_code)
    return code, namespace


def _cns_dump_fields(fields, ordered):
    '''Return (code, namespace)-tuple for a customized dump_fields function.

    Args:
        fields: An ordered mapping of field names to fields.

        ordered: If True, make the resulting function return OrderedDict
            objects, else make it return ordinary dicts.

    Returns:
        A tuple consisting of: a) Python code to define a dump function for
        fields and b) a namespace dict containing objects necessary for this
        code to work.

    '''
    # Namespace must contain OrderedDict if we want ordered output.
    namespace = {'OrderedDict': OrderedDict} if ordered else {}

    # Get correct templates depending on "ordered"
    if ordered:
        func_tpl = dedent(
            '''\
            def dump_fields(obj, many):
                if many:
                    return [OrderedDict([{joined_entries}]) for obj in obj]
                return OrderedDict([{joined_entries}])
            '''
        )
        entry_tpl = '("{key}", {val_code})'
    else:
        func_tpl = dedent(
            '''\
            def dump_fields(obj, many):
                if many:
                    return [{{{joined_entries}}} for obj in obj]
                return {{{joined_entries}}}
            '''
        )
        entry_tpl = '"{key}": {val_code}'

    # one entry per field
    entries = []

    # iterate over fields to fill up entries
    for field_num, (field_name, field) in enumerate(fields.items()):
        val_code, val_ns = _cns_field_value(field, field_name, field_num)
        namespace.update(val_ns)

        # try to guard against code injection via quotes in key
        key = str(field_name)
        if '"' in key or "'" in key:
            msg = 'Quotes are not allowed in field names: {}'
            raise ValueError(msg.format(key))

        # add entry
        entries.append(entry_tpl.format(key=key, val_code=val_code))

    code = func_tpl.format(joined_entries=', '.join(entries))
    return code, namespace
