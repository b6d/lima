'''tests for the lima module (without submodules)'''

import pytest

import lima


def test_namespace_pollution():
    '''Test if all shortcuts are present in package.'''
    from lima.schema import Schema as _Schema
    assert hasattr(lima, 'exc')
    assert hasattr(lima, 'fields')
    assert hasattr(lima, 'schema')
    assert hasattr(lima, 'Schema')
