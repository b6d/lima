=================================================
lima: Lightweight Marshalling of Python 3 Objects
=================================================

**lima** takes arbitrary Python objects and converts them into data structures
native to Python. The result can easily be serialized into JSON, XML, and all
sorts of other things. lima is Free Software, lightweight and fast.


Key Features
============

Lightweight
    lima has only a few hundred SLOC. lima has no external dependencies.

Fast
    lima tries to be as fast as possible while still remaining pure Python 3.

Focused
    lima doesn't try to do an ORM's job and it doesn't try to do a JSON
    library's job.

Extensible
    Build complex schemas out of simpler ones. Extend existing fields types or
    define your own.

Easy to learn
    lima is not only fast but also fast (and easy) to learn.

Well documented
    lima has a comprehensive tutorial and more than one line of docstring per
    line of Python code

Free
    lima is Free Software, licensed under the terms of the MIT license (see the
    LICENSE file for details).


lima at a Glance
================

.. code-block:: python

    import datetime
    import lima

    # a model
    class Book:
        def __init__(self, title, date_published):
            self.title = title
            self.date_published = date_published

    # a marshalling schema
    class BookSchema(lima.Schema):
        title = lima.fields.String()
        published = lima.fields.Date(attr='date_published')

    book = Book('The Old Man and the Sea', datetime.date(1952, 9, 1))
    schema = BookSchema()
    schema.dump(book)
    # {'published': '1952-09-01', 'title': 'The Old Man and the Sea'}


Requirements
============

Python 3.3 or newer. That's it.


Installation
============

::

  $ pip install lima

See the documentation for more comprehensive install instructions.
