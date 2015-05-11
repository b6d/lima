'''Tests for the util module.'''
from collections import OrderedDict

import pytest

from lima import fields
from lima import schema
from lima import util


def test_suppress():
    # this shouldn't be necessary, since the code of suppress is taken from the
    # lima stdlib. nevertheless, why not? so, the next statements should
    # suppress any Exceptions
    with util.suppress(ZeroDivisionError):
        1 / 0
    with util.suppress(ImportError, ZeroDivisionError):
        1 / 0
    with pytest.raises(ZeroDivisionError):
        with util.suppress(ImportError):
            1 / 0


def test_exception_context():
    '''Test if exception_context prefixes exception messages correctly.'''
    with pytest.raises(RuntimeError) as e:
        with util.exception_context('foo'):
            raise RuntimeError()
        assert str(e) == 'foo'

    with pytest.raises(RuntimeError) as e:
        with util.exception_context('bar'):
            raise RuntimeError('my message')
        assert str(e) == 'bar: my message'

    with pytest.raises(ZeroDivisionError) as e:
        with util.exception_context('foo'):
            1 / 0
        assert str(e).startswith('foo')

    with pytest.raises(AssertionError) as e:
        with util.exception_context('bar'):
            assert False
        assert str(e).startswith('bar')


# Adapted from Pyramid's test suite, licensed under the RPL
class TestReify:
    '''Class collecting tests of helper functions.'''

    class Dummy:
        pass

    def test__get__with_instance(self):
        def wrapee(inst):
            return 42
        decorated = util.reify(wrapee)
        inst = TestReify.Dummy()
        result = decorated.__get__(instance=inst, owner=...)
        assert result == 42
        assert inst.__dict__['wrapee'] == 42

    def test__get__without_instance(self):
        decorated = util.reify(None)
        result = decorated.__get__(instance=None, owner=...)
        assert result == decorated

    def test__doc__copied(self):
        def wrapee(inst):
            '''My docstring'''
        decorated = util.reify(wrapee)
        assert decorated.__doc__ == 'My docstring'


def test_vector_context():
    '''Test if vector context boxes scalars into lists.'''
    assert util.vector_context([]) == []
    assert util.vector_context({}) == {}
    assert util.vector_context(set()) == set()
    assert util.vector_context([None]) == [None]
    assert util.vector_context([1, 2, 3]) == [1, 2, 3]
    assert util.vector_context(['foo']) == ['foo']
    assert util.vector_context(['foo', 'bar']) == ['foo', 'bar']
    assert util.vector_context(b'foo') == b'foo'  # bytes count as vectors

    assert util.vector_context(None) == [None]
    assert util.vector_context(42) == [42]
    assert util.vector_context('foo') == ['foo']


def test_ensure_iterable():
    # none of these should raise anything
    util.ensure_iterable([1, 2, 3])
    util.ensure_iterable(range(10))
    util.ensure_iterable(i for i in range(10))

    with pytest.raises(TypeError):
        util.ensure_iterable(3)


def test_ensure_mapping():
    from collections import defaultdict

    # none of these should raise anything
    util.ensure_mapping({})
    util.ensure_mapping({'a': 1})
    util.ensure_mapping(defaultdict(lambda: 1))

    with pytest.raises(TypeError):
        util.ensure_mapping(set([1, 2, 3]))

    with pytest.raises(TypeError):
        util.ensure_mapping(None)


def test_ensure_only_one_of():
    a = ['foo', 'bar', 'baz']
    a2 = ['foo', 'bar', 'baz', 'foo', 'bar', 'baz']
    b = dict(foo='bar', bar='bar', baz='foo')

    # this should not raise anything
    util.ensure_only_one_of(a, ['foo'])
    util.ensure_only_one_of(a2, ['foo'])
    util.ensure_only_one_of(b, ['foo'])

    with pytest.raises(ValueError):
        util.ensure_only_one_of(a, ['foo', 'bar'])

    with pytest.raises(ValueError):
        util.ensure_only_one_of(a2, ['foo', 'bar'])

    with pytest.raises(ValueError):
        util.ensure_only_one_of(b, ['foo', 'bar'])


def test_ensure_subset_of():
    # this should not raise anything
    util.ensure_subset_of([1, 2], {0, 1, 2, 3, 4})
    util.ensure_subset_of([1, 2, 2], (0, 1, 2, 3, 4))

    with pytest.raises(ValueError):
        util.ensure_subset_of([1, 'foo'], [1, 2, 3])

    with pytest.raises(TypeError):
        util.ensure_subset_of(1, [1, 2, 3])


def test_only_instances_of():
    # this should not raise anything
    util.ensure_only_instances_of((1, 2, 3, 4), int)
    util.ensure_only_instances_of({'foo', 'bar', 'baz'}, str)
    util.ensure_only_instances_of({'foo': 1, 'bar': 2, 'baz': 3}, str)

    with pytest.raises(TypeError):
        util.ensure_only_instances_of({'foo', 'bar', b'baz'}, str)

    with pytest.raises(TypeError):
        util.ensure_only_instances_of([1, 2, 3.3, 4], int)
