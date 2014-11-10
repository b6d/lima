===============
Advanced Topics
===============


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
        at__foo = fields.String(attr='foo')
        hash__bar = fields.String(attr='bar')
        nil__class = fields.String(attr='cls')  # Python Keyword

    list(FancyFieldNamesSchema.__fields__)
    # ['@foo', '#bar', 'class']

.. note::

   When using field names that aren't Python identifiers, lima obviously can't
   look for attributes with those same names, so make sure to specify
   explicitly how the data for these fields should be determined (see
   :ref:`field_data_sources`).

   Also, quotes in field names are currently not allowed in lima, regardless
   of how they are specified.


Advanced Topics Recap
=====================

- You are now able to create schemas automatically
  (``__lima_args__['include']`` with some model-specific code).

- You can specify a field named ``'@context'`` as a schema class attribute
  (using field name mangling: ``'at__context'``).
