=================================================
lima: Lightweight Marshalling of Python 3 Objects
=================================================

|pypi| |docs| |build| |coverage|

**lima** takes arbitrary Python objects and converts them into data structures
native to Python. The result can easily be serialized into JSON, XML, and all
sorts of other things. lima is Free Software, lightweight and fast.


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
    lima has a comprehensive tutorial and more than one line of docstring per
    line of Python code (see `documentation`_).

Free
    lima is Free Software, licensed under the terms of the MIT license.


Requirements
============

Python 3.3 or newer. That's it.


Installation
============

::

  $ pip install lima

See the `documentation`_  for more comprehensive install instructions.


.. |pypi| image:: https://img.shields.io/pypi/v/lima.svg
    ?style=flat-square
    :target: https://pypi.python.org/pypi/lima
    :alt: PyPi Package

.. |docs| image:: https://readthedocs.org/projects/lima/badge/
    ?version=latest&style=flat-square
    :target: https://lima.readthedocs.org
    :alt: Documentation Status

.. |build| image:: https://img.shields.io/travis/b6d/lima/master.svg
    ?style=flat-square
    :target: https://travis-ci.org/b6d/lima
    :alt: Build Status

.. |coverage| image:: https://img.shields.io/coveralls/b6d/lima/master.svg
    ?style=flat-square
    :target: https://coveralls.io/r/b6d/lima
    :alt: Test Coverage

.. _documentation: https://lima.readthedocs.org/en/latest/
