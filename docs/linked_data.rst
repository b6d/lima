===========
Linked Data
===========

Most ORMs represent linked objects nested under an attribute of the linking
object. As an example, lets model the relationship between a book and its
author:

.. code-block:: python
    :emphasize-lines: 10,14

    class Person:
        def __init__(self, first_name, last_name):
            self.first_name = first_name
            self.last_name = last_name

    # A book links to its author via a nested Person object
    class Book:
        def __init__(self, title, author=None):
            self.title = title
            self.author = author

    person = Person('Ernest', 'Hemingway')
    book = Book('The Old Man and the Sea')
    book.author = person


One-way Relationships
=====================

Currently, this relationship is one way only: *From* a book *to* its author.
The author doesn't know anything about books yet (well, in our model at least).

To serialize this construct, we have to tell lima that a :class:`Book` object
has a :class:`Person` object nested inside, designated via the :attr:`author`
attribute.

For this we use a field of type :class:`lima.fields.Embed` and tell lima what
data to expect by providing the ``schema`` parameter:

.. code-block:: python
    :emphasize-lines: 9,13

    from lima import fields, Schema

    class PersonSchema(Schema):
        first_name = fields.String()
        last_name = fields.String()

    class BookSchema(Schema):
        title = fields.String()
        author = fields.Embed(schema=PersonSchema)

    schema = BookSchema()
    schema.dump(book)
    # {'author': {'first_name': 'Ernest', 'last_name': 'Hemingway'},
    #  'title': The Old Man and the Sea'}

Along with the mandatory keyword-only argument ``schema``,
:class:`lima.fields.Embed` accepts the optional keyword-only-arguments we
already know (``attr`` or ``get``). All other keyword arguments provided to
:class:`lima.fields.Embed` get passed through to the constructor of the linked
schema. This allows us to do stuff like the following:

.. code-block:: python
    :emphasize-lines: 3, 7

    class BookSchema(Schema):
        title = fields.String()
        author = fields.Embed(schema=PersonSchema, only='last_name')

    schema = BookSchema()
    schema.dump(book)
    # {'author': {'last_name': 'Hemingway'},
    #  'title': The Old Man and the Sea'}


Two-way Relationships
=====================

If not only a book should link to its author, but an author should also link to
his/her bestselling book, we can adapt our model like this:

.. code-block:: python
    :emphasize-lines: 5,11,15-16

    # authors link to their bestselling book
    class Author(Person):
        def __init__(self, first_name, last_name, bestseller=None):
            super().__init__(first_name, last_name)
            self.bestseller = bestseller

    # books link to their authors
    class Book:
        def __init__(self, title, author=None):
            self.title = title
            self.author = author

    author = Author('Ernest', 'Hemingway')
    book = Book('The Old Man and the Sea')
    book.author = author
    author.bestseller = book

If we want to construct schemas for models like this, we will have to adress
two problems:

1. **Definition order:** If we define our :class:`AuthorSchema` first, its
   :attr:`bestseller` attribute will have to reference a :class:`BookSchema` -
   but this doesn't exist yet, since we decided to define :class:`AuthorSchema`
   first. If we decide to define :class:`BookSchema` first instead, we run into
   the same problem with its :attr:`author` attribute.

2. **Recursion:** An author links to a book that links to an author that links
   to a book that links to an author that links to a book that links to an
   author that links to a book that links to an author that links to a book
   that links to an author ``RuntimeError: maximum recursion depth exceeded``

lima makes it easy to deal with those problems:

To overcome the problem of recursion, just exclude the attribute on the other
side that links back.

To overcome the problem of definition order, lima supports lazy evaluation of
schemas. Just pass the *qualified name* (or the *fully module-qualified name*)
of a schema class to :class:`lima.fields.Embed` instead of the class itself:

.. code-block:: python
    :emphasize-lines: 2,6,12,16

    class AuthorSchema(PersonSchema):
        bestseller = fields.Embed(schema='BookSchema', exclude='author')

    class BookSchema(Schema):
        title = fields.String()
        author = fields.Embed(schema=AuthorSchema, exclude='bestseller')

    author_schema = AuthorSchema()
    author_schema.dump(author)
    # {'first_name': 'Ernest',
    #  'last_name': 'Hemingway',
    #  'bestseller': {'title': The Old Man and the Sea'}

    book_schema = BookSchema()
    book_schema.dump(book)
    # {'author': {'first_name': 'Ernest', 'last_name': 'Hemingway'},
    #  'title': The Old Man and the Sea'}

.. _on_class_names:

.. admonition:: On class names
    :class: note

    For referring to classes via their name, the lima documentation only ever
    talks about two different kinds of class names: the *qualified name*
    (*qualname* for short) and the *fully module-qualified name*:

    The qualified name
        This is the value of the class's :attr:`__qualname__` attribute. Most
        of the time, it's the same as the class's :attr:`__name__` attribute
        (except if you define classes within classes or functions ...). If you
        define ``class Foo: pass`` at the top level of your module, the class's
        qualified name is simply *Foo*. Qualified names were introduced with
        Python 3.3 via `PEP 3155 <https://python.org/dev/peps/pep-3155>`_

    The fully module-qualified name
        This is the qualified name of the class prefixed with the full name of
        the module the class is defined in. If you define ``class Qux: pass``
        within a class :class:`Baz` (resulting in the qualified name *Baz.Qux*)
        at the top level of your ``foo.bar`` module, the class's fully
        module-qualified name is *foo.bar.Baz.Qux*.

.. warning::

    If you define schemas in local namespaces (at function execution time),
    their names become meaningless outside of their local context.  For
    example:

    .. code-block:: python

        def make_schema():
            class FooSchema(Schema):
                foo = fields.String()
            return FooSchema

        schemas = [make_schema() for i in range(1000)]

    Which of those one thousend schemas would we refer to, would we try to link
    to a ``FooSchema`` by name? To avoid ambiguity, lima will refuse to link to
    schemas defined in local namespaces.

By the way, there's nothing stopping us from using the idioms we just learned
for models that link to themselves - everything works as you'd expect:

.. code-block:: python
    :emphasize-lines: 4,7

    class MarriedPerson(Person):
        def __init__(self, first_name, last_name, spouse=None):
            super().__init__(first_name, last_name)
            self.spouse = spouse

    class MarriedPersonSchema(PersonSchema):
        spouse = fields.Embed(schema='MarriedPersonSchema', exclude='spouse')


One-to-many and many-to-many Relationships
==========================================

Until now, we've only dealt with one-to-one relations. What about one-to-many
and many-to-many relations? Those link to collections of objects.

We know the necessary building blocks already: Providing additional keyword
arguments to :class:`lima.fields.Embed` passes them through to the specified
schema's constructor. And providing ``many=True`` to a schema's construtor will
have the schema marshalling collections - so:


.. code-block:: python
    :emphasize-lines: 5,15,19

    # authors link to their books now
    class Author(Person):
        def __init__(self, first_name, last_name, books=None):
            super().__init__(first_name, last_name)
            self.books = books

    author = Author('Virginia', 'Woolf')
    author.books = [
        Book('Mrs Dalloway', author),
        Book('To the Lighthouse', author),
        Book('Orlando', author)
    ]

    class AuthorSchema(PersonSchema):
        books = fields.Embed(schema='BookSchema', exclude='author', many=True)

    class BookSchema(Schema):
        title = fields.String()
        author = fields.Embed(schema=AuthorSchema, exclude='books')

    schema = AuthorSchema()
    schema.dump(author)
    # {'books': [{'title': 'Mrs Dalloway'},
    #            {'title': 'To the Lighthouse'},
    #            {'title': 'Orlando'}],
    #  'last_name': 'Woolf',
    #  'first_name': 'Virginia'}


Linked Data Recap
=================

- You now know how to marshal linked objects (via a field of type
  :class:`lima.fields.Embed`)

- You know about lazy evaluation of linked schemas and how to specify those via
  qualified and fully module-qualified names.

- You know how to implement two-way relationships between objects (pass
  ``exclude`` or ``only`` to the linked schema through
  :class:`lima.fields.Embed`)

- You know how to marshal linked collections of objects (pass ``many=True`` to
  the linked schema through :class:`lima.fields.Embed`)
