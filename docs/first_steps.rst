===========
First Steps
===========

lima tries to be lean, consistent, and easy to learn. Assuming you already have
:doc:`installed <installation>` lima, this section should help you getting
started.

.. note::

    Throughout this documentation, the terms *marshalling* and *serialization*
    will be used synonymously.


A simple Example
================

Let's say we want to expose our data to the world via a web API and we've
chosen JSON as our preferred serialization format. We have defined a data model
in the ORM of our choice. It might behave something like this:

.. code-block:: python

    class Person:
        def __init__(self, first_name, last_name, date_of_birth):
            self.first_name = first_name
            self.last_name = last_name
            self.date_of_birth = date_of_birth

Our person objects look like this:

.. code-block:: python

    import datetime
    person = Person('Ernest', 'Hemingway', datetime.date(1899, 7, 21))

If we want to serialize such person objects, we can't just feed them to
Python's :func:`json.dumps` function: per default it only knows how to deal
with a very basic set of data types.

Here's where lima comes in: Defining an appropriate :class:`Schema
<lima.schema.Schema>`, we can convert person objects into data structures
accepted by :func:`json.dumps`.

.. code-block:: python

    from lima import fields, Schema

    class PersonSchema(Schema):
        first_name = fields.String()
        last_name = fields.String()
        date_of_birth = fields.Date()

    schema = PersonSchema()
    serialized = schema.dump(person)
    # {'date_of_birth': '1899-07-21',
    #  'first_name': 'Ernest',
    #  'last_name': 'Hemingway'}


... and to conclude our example:

.. code-block:: python

    import json
    json.dumps(serialized)
    # '{"last_name": "Hemingway", "date_of_birth": "1899-07-21", ...


First Steps Recap
=================

- You now know how to do basic marshalling (Create a schema class with
  appropriate fields. Create a schema object. Pass the object(s) to marshal to
  the schema object's :meth:`dump` method.

- You now know how to get JSON for arbitrary objects (pass the result of a
  schema object's :meth:`dump` method to :func:`json.dumps`).
