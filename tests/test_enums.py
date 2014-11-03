'''Tests for lima's poor enum implementation.

PoorEnum is a poor excuse for an enumeration, existing only for compatibility
with Python 3.3. It will be dropped if Python 3.3 support gets removed or
something better comes up. Until then, ensure the most basic functionality with
these tests.

'''
import pytest

from lima.enums import PoorEnum


class Color(PoorEnum):
    red = 1
    green = 2
    blue = 3
    white = 4
    eggshell = 4


class Mood(PoorEnum):
    happy = 1
    sad = 2


def test_creation():
    '''Test if poor enums were created.'''
    assert isinstance(Color.red, Color)
    assert isinstance(Color.green, Color)
    assert isinstance(Color.blue, Color)
    assert isinstance(Mood.happy, Mood)
    assert isinstance(Mood.sad, Mood)
    assert not isinstance(Mood.happy, Color)
    assert not isinstance(Color.red, Mood)


def test_contains():
    '''Test if checking enum membership works.'''
    # Instantiating Enums like this shouldn't even be possible. This is one of
    # the many shortcommings of PoorEnum
    black = Color('black', 99)

    assert Color.red in Color
    assert black not in Color
    assert 1 not in Color
    assert Color.red not in Mood


def test_equals():
    '''Test if equality checks work.'''
    # Instantiating Enums like this shouldn't even be possible. This is one of
    # the many shortcommings of PoorEnum
    fake_red = Color('red', 1)

    assert fake_red == Color.red
    assert Color.white == Color.eggshell
    assert Color.red != Color.green
    assert Color.red != Mood.happy


def test_repr():
    '''Test if __repr__ works.'''
    assert repr(Color.red) == '<Color.red: 1>'
    assert repr(Mood.happy) == '<Mood.happy: 1>'
