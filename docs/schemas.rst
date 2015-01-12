====================
Working with Schemas
====================

Schemas collect fields for object serialization.


Defining Schemas
================

We already know how to define schemas: subclass :class:`lima.Schema` (the
shortcut for :class:`lima.schema.Schema`) and add fields as class attributes.

But there's more to schemas than this. First of all -- schemas are composible:

.. code-block:: python
    :emphasize-lines: 11-12,15

    from lima import Schema, fields

    class PersonSchema(Schema):
        first_name = fields.String()
        last_name = fields.String()

    class AccountSchema(Schema):
        login = fields.String()
        password_hash = fields.String()

    class UserSchema(PersonSchema, AccountSchema):
        pass

    list(UserSchema.__fields__)
    # ['first_name', 'last_name', 'login', 'password_hash']

Secondly, it's possible to *remove* fields from subclasses that are present in
superclasses. This is done by setting a special class attribute
:attr:`__lima_args__` like so:

.. code-block:: python
    :emphasize-lines: 2,5

    class UserProfileSchema(UserSchema):
        __lima_args__ = {'exclude': ['last_name', 'password_hash']}

    list(UserProfileSchema.__fields__)
    # ['first_name', 'login']

If there's only one field to exclude, you don't have to put its name inside a
list - lima does that for you:

.. code-block:: python
    :emphasize-lines: 2

    class NoLastNameSchema(UserSchema):
        __lima_args__ = {'exclude': 'last_name'}  # string instead of list

    list(NoLastNameSchema.__fields__)
    # ['first_name', 'login', 'password_hash']

If, on the other hand, there are lots of fields to exclude, you *could* provide
``__lima_args__['only']`` (Note that ``"exclude"`` and ``"only"`` are mutually
exclusive):


.. code-block:: python
    :emphasize-lines: 2

    class JustNameSchema(UserSchema):
        __lima_args__ = {'only': ['first_name', 'last_name']}

    list(JustNameSchema.__fields__)
    # ['first_name', 'last_name']


.. warning::

    Having to provide ``"only"`` on Schema definition hints at bad design - why
    would you add a lot of fields just to remove them quickly afterwards? Have
    a look at :ref:`schema_objects` for the preferred way to selectively
    remove fields.

And finally, we can't just *exclude* fields, we can *include* them too. So
here is a user schema with fields provided via ``__lima_args__``:

.. code-block:: python

    class UserSchema(Schema):
        __lima_args__ = {
            'include': {
                'first_name': fields.String(),
                'last_name': fields.String(),
                'login': fields.String(),
                'password_hash': fields.String()
            }
        }

    list(UserSchema.__fields__)
    # ['password_hash', 'last_name', 'first_name', 'login']

.. note::

    It's possible to mix and match all those features to your heart's content.
    lima tries to fail early if something doesn't add up (remember,
    ``"exclude"`` and ``"only"`` are mutually exclusive).

.. note::

    The inheritance and precedence rules for fields are intuitive, but should
    there ever arise the need for clarification, you can read about how a
    schema's fields are determined in the documentation of
    :class:`lima.schema.SchemaMeta`.


.. _schema_objects:

Schema Objects
==============

Up until now we only ever needed a single instance of a schema class to marshal
the fields defined in this class. But schema objects can do more.

Providing the keyword-only argument ``exclude``, we may exclude certain fields
from being serialized. 

.. include:: keyword_only_args.rst.inc

.. code-block:: python
    :emphasize-lines: 27,29

    import datetime
    from lima import Schema, fields

    # again, our model
    class Person:
        def __init__(self, first_name, last_name, birthday):
            self.first_name = first_name
            self.last_name = last_name
            self.birthday = birthday

    # again, our schema
    class PersonSchema(Schema):
        first_name = fields.String()
        last_name = fields.String()
        date_of_birth = fields.Date(attr='birthday')

    # again, our person
    person = Person('Ernest', 'Hemingway', datetime.date(1899, 7, 21))

    # as before, for reference
    person_schema = PersonSchema()
    person_schema.dump(person)
    # {'date_of_birth': '1899-07-21',
    #  'first_name': 'Ernest',
    #  'last_name': 'Hemingway'}

    birthday_schema = PersonSchema(exclude=['first_name', 'last_name'])
    birthday_schema.dump(person)
    # {'date_of_birth': '1899-07-21'}

The same thing can be achieved via the ``only`` keyword-only argument:

.. code-block:: python
    :emphasize-lines: 1,3

    birthday_schema = PersonSchema(only='date_of_birth')
    birthday_schema.dump(person)
    # {'date_of_birth': '1899-07-21'}

You may have already guessed: both ``exclude`` and ``only`` take lists of field
names as well as simple strings for a single field name -- just like
``__lima_args__['exclude']`` and ``__lima_args__['only']``.

For some use cases, ``exclude`` and ``only`` save the need to define lots of
almost similar schema classes.

You *could* also include fields on schema object creation time:

.. code-block:: python
    :emphasize-lines: 3,9

    getter = lambda o: '{}, {}'.format(o.last_name, o.first_name)

    schema = PersonSchema(include={'sort_name': fields.String(get=getter)})

    schema.dump(person)
    # {'date_of_birth': '1899-07-21',
    #  'first_name': 'Ernest',
    #  'last_name': 'Hemingway',
    #  'sort_name': 'Hemingway, Ernest'}

.. warning::

    Having to provide ``include`` on Schema object creation hints at bad design
    - why not just include the fields in the Schema itself?


Field Order
===========

Lima marshals objects to dictionaries. Field order doesn't matter. Unless you
want it to:

.. code-block:: python
    :emphasize-lines: 1

    person_schema = PersonSchema(ordered=True)
    person_schema.dump(person)
    # OrderedDict([
    #     ('first_name', 'Ernest'),
    #     ('last_name', 'Hemingway'),
    #     ('date_of_birth', '1899-07-21')])
    # ])

Just provide the keyword-only argument ``ordered=True`` to a schema's
constructor, and the resulting instance will dump ordered dictionaries.

The order of the resulting key-value-pairs reflects the order in which the
fields were defined at schema definition time.

If you use ``__lima_args__['include']``, make sure to provide an instance of
:class:`collections.OrderedDict` if you care about the order of those fields as
well.

Fields specified via ``__lima_args__['include']`` are inserted at the position
of the :attr:`__lima_args__` class attribute in the Schema class. Here is a
more complex example:

.. code-block:: python

    from collections import OrderedDict

    class FooSchema(Schema):
        one = fields.String()
        two = fields.String()

    class BarSchema(FooSchema):
        three = fields.String()
        __lima_args__ = {
            'include': OrderedDict([
                ('four', fields.String()),
                ('five', fields.String())
            ])
        }
        six = fields.String()

    bar_schema = BarSchema(ordered=True)

``bar_schema`` will dump ordered dictionaries with keys ordered from ``one`` to
``six``.

.. note::

    For the exact rules on how a complex schema's fields are going to be
    ordered, see :class:`lima.schema.SchemaMeta` or have a look at the source
    code.


Marshalling Collections
=======================

Consider this:

.. code-block:: python

    persons = [
        Person('Ernest', 'Hemingway', datetime.date(1899, 7, 21)),
        Person('Virginia', 'Woolf', datetime.date(1882, 1, 25)),
        Person('Stefan', 'Zweig', datetime.date(1881, 11, 28)),
    ]

Instead of looping over this collection ourselves, we can ask the schema object
to do this for us by specifying ``many=True`` to the schema's constructor):

.. code-block:: python
    :emphasize-lines: 1

    many_persons_schema =  PersonSchema(only='last_name', many=True)
    many_persons_schema.dump(persons)
    # [{'last_name': 'Hemingway'},
    #  {'last_name': 'Woolf'},
    #  {'last_name': 'Zweig'}]


Schema Recap
============

- You now know how to compose bigger schemas from smaller ones (inheritance of
  schema classes).

- You know how to exclude certain fields from schemas
  (``__lima_args__['exclude']``).

- You know three different ways to add fields to schemas (class attributes,
  ``__lima_args__['include']`` and inheriting from other schemas).

- You can fine-tune what gets dumped by a schema object (``only`` and
  ``exclude`` keyword-only arguments)

- You can dump ordered dictionaries (``ordered=True``) and you can serialize
  collections of objects (``many=True``).
