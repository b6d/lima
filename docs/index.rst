.. lima documentation master file, created by
   sphinx-quickstart on Mon Oct 20 14:45:54 2014.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

=================================================
lima: Lightweight Marshalling of Python 3 Objects
=================================================

**lima** takes arbitrary Python objects and converts them into data structures
native to Python. The result can easily be serialized into JSON, XML, and all
sorts of other things. lima is Free Software, lightweight and fast.

.. image:: /images/alpaca_llama_vicuna.*
    :alt: Alpaca, Llama, Vicuna (Illustration from The New Student's Reference
          Work, 1914)


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


Key Features
============

Lightweight
    lima has only a few hundred SLOC. lima has no external dependencies.

Fast
    lima tries to be as fast as possible while still remaining pure Python 3.

Well documented
    lima has a comprehensive :doc:`tutorial <first_steps>` and more than one
    line of :doc:`docstring <api>` per line of Python code.

Free
    lima is Free Software, licensed under the terms of the :doc:`MIT license
    <license>`.


Documentation
=============

.. toctree::
   :maxdepth: 2

   installation
   first_steps
   schemas
   fields
   linked_data
   advanced
   api
   project_info
   changelog
   license
