====================
Working with Schemas
====================

Now that we know about fields, let's focus on schemas:


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
    # ['password_hash', 'login', 'last_name', 'first_name']

Secondly, it's possible to *remove* fields from subclasses that are present in
superclasses. This is done by setting a special class attribute
:attr:`__lima_args__` like so:

.. code-block:: python
    :emphasize-lines: 2,5

    class UserProfileSchema(UserSchema):
        __lima_args__ = {'exclude': ['last_name', 'password_hash']}

    list(UserProfileSchema.__fields__)
    # ['login', 'first_name']

If there's only one field to exclude, you don't have to put its name inside a
list - lima does that for you:

.. code-block:: python
    :emphasize-lines: 2

    class NoLastNameSchema(UserSchema):
        __lima_args__ = {'exclude': 'last_name'}  # string instead of list

    list(NoLastNameSchema.__fields__)
    # ['password_hash', 'login', 'first_name']

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


Automated Schema Definition
===========================

Validating ORM agnosticism for a moment, let's see how we could utilize
``__lima_args__['include']`` to create our Schema automatically.

We start with this `SQLAlchemy <http://www.sqlalchemy.org>`_ model (skip this
section if you don't want to install SQLAlchemy):

.. code-block:: python

    import sqlalchemy as sa
    from sqlalchemy.ext.declarative import declarative_base

    Base = declarative_base()

    class Account(Base):
        __tablename__ = 'accounts'
        id = sa.Column(sa.Integer, primary_key=True)
        login = sa.Column(sa.String)
        password_hash = sa.Column(sa.String)

:mod:`lima.fields` defines a mapping :data:`lima.fields.type_mapping` of some
Python types to field classes. We can utilize this as follows:

.. code-block:: python
    :emphasize-lines: 6

    from lima import fields

    def fields_for_model(model):
        result = {}
        for name, col in model.__mapper__.columns.items():
            field_class = fields.type_mapping[col.type.python_type]
            result[name] = field_class()
        return result

Defining lima schemas becomes a piece of cake now:

.. code-block:: python
    :emphasize-lines: 4

    from lima import Schema

    class AccountSchema(Schema):
        __lima_args__ = {'include': fields_for_model(Account)}

    AccountSchema.__fields__
    # {'id': <lima.fields.Integer at 0x...>,
    #  'login': <lima.fields.String at 0x...>,
    #  'password_hash': <lima.fields.String at 0x...>}

... and of course you still can manually add, exclude or inherit anything you
like.

.. warning::

    Neither :data:`lima.fields.type_mapping` nor the available field classes
    are as exhaustive as they should be. Expect above code to fail on slightly
    exotic column types. There is still work to be done.

.. _schema_objects:

Schema Objects
==============

Up until now we only ever needed a single instance of a schema class to marshal
the fields defined in this class. But schema objects can do more.

Providing the keyword-only argument ``exclude``, we may exclude certain fields
from being serialized. This saves the need to define lots of almost similar
schema classes:

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
to do this for us - either for a single call (by specifying ``many=True`` to
the :meth:`dump` method), or for every call of :meth:`dump` (by specifying
``many=True`` to the schema's constructor):

.. code-block:: python
    :emphasize-lines: 2,7

    person_schema = PersonSchema(only='last_name')
    person_schema.dump(persons, many=True)
    # [{'last_name': 'Hemingway'},
    #  {'last_name': 'Woolf'},
    #  {'last_name': 'Zweig'}]

    many_persons_schema =  PersonSchema(only='last_name', many=True)
    many_persons_schema.dump(persons)
    # [{'last_name': 'Hemingway'},
    #  {'last_name': 'Woolf'},
    #  {'last_name': 'Zweig'}]


Field Name Mangling
===================

Fields specified via ``__lima_args__['include']`` can have arbitrary names.
Fields provided via class attributes have a drawback: class attribute names
have to be valid Python identifiers.

lima implements a simple name mangling mechanism to allow the specification of
some common non-Python-identifier field names (like JSON-LD's ``"@id"``) as
class attributes.

The following table shows how name prefixes will be replaced by lima when
specifying fields as class attributes:

============ =========================
name prefix  replacement
============ =========================
``'at__'``   ``'@'``
``'dash__'`` ``'-'``
``'dot__'``  ``'.'``
``'hash__'`` ``'#'``
``'plus__'`` ``'+'``
``'nil__'``  ``''`` (the emtpy String)
============ =========================

This enables us to do the following:

.. code-block:: python

    class FancyFieldNamesSchema(Schema):
        at__foo = fields.String()
        dash__bar = fields.String()
        dot__baz = fields.String()
        hash__qux = fields.String()
        plus__qup = fields.String()
        nil__class = fields.String()  # Python Keyword

    list(FancyFieldNamesSchema.__fields__)
    # ['@foo', '-bar', '.baz', '#qux', '+qup', 'class']

.. note:: Quotes in field names are currently not allowed in lima, regardless
   of how they are specified.


Schema Recap
============

- You now know how to compose bigger schemas from smaller ones (inheritance of
  schema classes).

- You know how to exclude certain fields from schemas
  (``__lima_args__['exclude']``).

- You know three different ways to add fields to schemas (class attributes,
  ``__lima_args__['include']`` and inheriting from other schemas).

- You are now able to create schemas automatically
  (``__lima_args__['include']`` with some model-specific code).

- You can fine-tune what gets dumped by a schema object (``only`` and
  ``exclude`` keyword-only arguments) and you can serialize collections of
  objects (``many=True``).

- You can specify a field named ``'@context'`` as a schema class attribute
  (using field name mangling: ``'at__context'``).
