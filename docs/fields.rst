=======================
A closer Look at Fields
=======================

Fields are the basic building blocks of a Schema. Even though lima fields
follow only the most basic protocol, they are rather powerful.


What Data a Field presents
==========================

The :class:`PersonSchema` from the last chapter contains three field  objects
named *first_name,* *last_name* and *date_of_birth.* These correspond to a
person object's attributes of the same name. What if our model didn't have an
attribute :attr:`date_of_birth` but an attribute :attr:`birthday` instead?

To get the data for our ``date_of_birth`` field from the model's
:attr:`birthday` attribute, we have to tell the field by supplying the
attribute name via the ``attr`` argument:

.. code-block:: python
    :emphasize-lines: 8,15,19

    import datetime
    from lima import Schema, fields

    class Person:
        def __init__(self, first_name, last_name, birthday):
            self.first_name = first_name
            self.last_name = last_name
            self.birthday = birthday

    person = Person('Ernest', 'Hemingway', datetime.date(1899, 7, 21))

    class PersonSchema(Schema):
        first_name = fields.String()
        last_name = fields.String()
        date_of_birth = fields.Date(attr='birthday')

    schema = PersonSchema()
    schema.dump(person)
    # {'date_of_birth': '1899-07-21',
    #  'first_name': 'Ernest',
    #  'last_name': 'Hemingway'}

Providing ``attr`` is the preferred way to deal with attribute names differing
from field names, but ``attr`` is not enough for some other cases. What if we
can't get the information we need from a single attribute? Here *getters* come
in handy.

A getter in this context is a callable that takes an object (in our case: a
person object) and returns the value we're interested in. We tell a field about
the getter via the ``get`` parameter:

.. code-block:: python
    :emphasize-lines: 1-2,7,15

    def sort_name_getter(obj):
        return '{}, {}'.format(obj.last_name, obj.first_name)

    class PersonSchema(Schema):
        first_name = fields.String()
        last_name = fields.String()
        sort_name = fields.String(get=sort_name_getter)
        date_of_birth = fields.Date(attr='birthday')

    schema = PersonSchema()
    schema.dump(person)
    # {'date_of_birth': '1899-07-21',
    #  'first_name': 'Ernest',
    #  'last_name': 'Hemingway'
    #  'sort_name': 'Hemingway, Ernest'}

.. note::

    For getters, `lambda expressions <https://docs.python.org/3/tutorial/
    controlflow.html#lambda-expressions>`_ come in handy. ``sort_name`` could
    just as well have been defined like this:

    .. code-block:: python

        sort_name = fields.String(
            get=lambda obj: '{}, {}'.format(obj.last_name, obj.first_name)
        )

``attr`` and ``get`` are *keyword-only arguments* - a relatively uncommon
feature of Python 3 that the lima API makes heavy use of.

.. include:: keyword_only_args.rst.inc


How a Field presents its Data
=============================

If a field has a static method (or instance method) :meth:`pack`, this method
is used to present a field's data. (Otherwise the field's data is just passed
through on marshalling. Some of the more basic built-in fields behave that
way.)

So by implementing a :meth:`pack` static method (or instance method), we can
support marshalling of any data type we want:

.. code-block:: python
    :emphasize-lines: 8-13,24,29

    from collections import namedtuple
    from lima import fields, Schema

    # a new data type
    GeoPoint = namedtuple('GeoPoint', ['lat', 'long'])

    # a field class for the new date type
    class GeoPointField(fields.Field):
        @staticmethod
        def pack(val):
            ns = 'N' if val.lat > 0 else 'S'
            ew = 'E' if val.long > 0 else 'W'
            return '{}° {}, {}° {}'.format(val.lat, ns, val.long, ew)

    # a model using the new data type
    class Treasure:
        def __init__(self, name, location):
            self.name = name
            self.location = location

    # a schema for that model
    class TreasureSchema(Schema):
        name = fields.String()
        location = GeoPointField()

    treasure = Treasure('The Amber Room', GeoPoint(lat=59.7161, long=30.3956))
    schema = TreasureSchema()
    schema.dump(treasure)
    # {'location': '59.7161° N, 30.3956° E', 'name': 'The Amber Room'}

Or we can change how already supported data types are marshalled:

.. code-block:: python
    :emphasize-lines: 1-4,9,13

    class FancyDate(fields.Date):
        @staticmethod
        def pack(val):
            return val.strftime('%A, the %d. of %B %Y')

    class FancyPersonSchema(Schema):
        first_name = fields.String()
        last_name = fields.String()
        date_of_birth = FancyDate(attr='birthday')

    schema = FancyPersonSchema()
    schema.dump(person)
    # {'date_of_birth': 'Friday, the 21. of July 1899',
    #  'first_name': 'Ernest',
    #  'last_name': 'Hemingway'}

.. warning::

    Make sure the result of your :meth:`pack` methods is JSON serializable (or
    at least in a format accepted by the serializer of your target format).

    Also, don't try to override an existing instance method with a static
    method. Have a look at the source if in doubt (currently only
    :class:`lima.fields.Nested` implements :meth:`pack` as an instance method.


Data Validation
===============

In short: *There is none.*

lima is opinionated in this regard. It assumes you have control over the data
you want to serialize and have already validated it *before* putting it in your
database.

But this doesn't mean it can't be done. You'll just have to do it yourself. The
:meth:`pack` method would be the place for this:


.. code-block:: python
    :emphasize-lines: 6-7

    import re

    class ValidEmailField(fields.String):
        @staticmethod
        def pack(val):
            if not re.match(r'[^@]+@[^@]+\.[^@]+', val):
                raise ValueError('Not an email address: {!r}'.format(val))
            return val

.. note::

    If - depending on demand and developer time - lima ever gets
    deserialization support, sensible validation of incoming data would be a
    key component of this feature.

    If you need full-featured validation of your existing data at marshalling
    time, have a look at `marshmallow <http://marshmallow.readthedocs.org>`_.


Fields Recap
============

- You now know how a field gets its data (in order of precedence: getter >
  ``attr`` parameter > field name).

- You know how a field presents its data (:meth:`pack` method).

- You know how to support your own data types (subclass
  :class:`lima.fields.Field`) and implement :meth:`pack`

- And you know how to change the marshalling of already supported data types
  (subclass the appropriate field class and override :meth:`pack`)

- Also, you're able to implement data validation should the need arise
  (implement/override :meth:`pack`).
