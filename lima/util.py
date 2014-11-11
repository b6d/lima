'''Internal utilities.

.. warning::

    For users of lima there should be no need to use anything within
    :mod:`lima.util` directly. Name and contents of this module may change at
    any time without deprecation notice or upgrade path.

'''
from collections import abc
from contextlib import contextmanager


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


class suppress:
    '''Context manager to suppress specified exceptions

    This context manager is taken directly from the Python 3.4 standard library
    to get support for Python 3.3.

    See https://docs.python.org/3.4/library/contextlib.html#contextlib.suppress

    '''
    def __init__(self, *exceptions):
        self._exceptions = exceptions

    def __enter__(self):
        pass

    def __exit__(self, exctype, excinst, exctb):
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
