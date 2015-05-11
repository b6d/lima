'''tests for the registry module'''

import pytest

from lima import exc, schema, registry


@pytest.fixture
def reg():
    return registry.Registry()


# mock Schema class to register later on
class Schema:
    pass


def test_register1(reg):
    '''Test if mock Schema class can be registered without raising.'''
    reg.register(Schema)


def test_get1(reg):
    '''Test if registered classes can be retrieved again (1).'''
    reg.register(Schema)
    assert reg.get('Schema') is Schema  # via qualname
    assert reg.get(__name__ + '.Schema') is Schema  # via fullname


def test_register2(reg):
    '''Test if real Schema exist alongside mock one without raising'''
    reg.register(Schema)
    reg.register(schema.Schema)


def test_get2(reg):
    '''Test if registered classes can be retrieved again (2).'''
    reg.register(Schema)
    reg.register(schema.Schema)

    # try to get via full names
    # (note that lima.Schema's full name is lima.schema.Schema)
    assert reg.get(__name__ + '.Schema') is Schema  # mock Schema
    assert reg.get('lima.schema.Schema') is schema.Schema  # real Schema


def test_class_not_found_error(reg):
    '''Test if registry throws an error when not finding anything.'''

    with pytest.raises(exc.ClassNotFoundError):
        reg.get('NonExistentClass')


def test_ambiguous_class_name_error(reg):
    '''Test if registry throws an error when finding >1 classes w/qualname.'''

    reg.register(Schema)
    reg.register(schema.Schema)

    with pytest.raises(exc.AmbiguousClassNameError):
        reg.get('Schema')


def test_register_local_class_error(reg):
    '''Test if registry rejects classes defined in local namespaces.'''

    class LocallyDefinedClass:
        pass

    with pytest.raises(exc.RegisterLocalClassError):
        reg.register(LocallyDefinedClass)

    with pytest.raises(exc.ClassNotFoundError):
        reg.get('LocallyDefinedClass')
