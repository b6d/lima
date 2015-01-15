===========
Linked Data
===========

Lets model a relationship between a book and a book review:

.. code-block:: python
    :emphasize-lines: 16

    class Book:
        def __init__(self, isbn, author, title):
            self.isbn = isbn
            self.author = author
            self.title = title

    # A review links to a book via the "book" attribute
    class Review:
        def __init__(self, rating, text, book=None):
            self.rating = rating
            self.text = text
            self.book = book

    book = Book('0-684-80122-1', 'Hemingway', 'The Old Man and the Sea')
    review = Review(10, 'Has lots of sharks.')
    review.book = book

To serialize this construct, we have to tell lima that a :class:`Review` object
links to a :class:`Book` object via the :attr:`book` attribute (many ORMs
represent related objects in a similar way).


Embedding linked Objects
========================

We can use a field of type :class:`lima.fields.Embed` to *embed* the serialized
book into the serialization of the review. For this to work we have to tell the
:class:`~lima.fields.Embed` field what to expect by providing the ``schema``
parameter:

.. code-block:: python
    :emphasize-lines: 9,15-17

    from lima import fields, Schema

    class BookSchema(Schema):
        isbn = fields.String()
        author = fields.String()
        title = fields.String()

    class ReviewSchema(Schema):
        book = fields.Embed(schema=BookSchema)
        rating = fields.Integer()
        text = fields.String()

    review_schema = ReviewSchema()
    review_schema.dump(review)
    # {'book': {'author': 'Hemingway',
    #           'isbn': '0-684-80122-1',
    #           'title': 'The Old Man and the Sea'},
    #  'rating': 10,
    #  'text': 'Has lots of sharks.'}

Along with the mandatory keyword-only argument ``schema``,
:class:`~lima.fields.Embed` accepts the optional keyword-only-arguments we
already know (``attr``, ``get``, ``val``). All other keyword arguments provided
to :class:`~lima.fields.Embed` get passed through to the constructor of the
associated schema. This allows us to do stuff like the following:

.. code-block:: python
    :emphasize-lines: 4-6,10-11

    class ReviewSchemaPartialBook(Schema):
        rating = fields.Integer()
        text = fields.String()
        partial_book = fields.Embed(attr='book',
                                    schema=BookSchema,
                                    exclude='isbn')

    review_schema_partial_book = ReviewSchemaPartialBook()
    review_schema_partial_book.dump(review)
    # {'partial_book': {'author': 'Hemingway',
    #                   'title': 'The Old Man and the Sea'},
    #  'rating': 10,
    #  'text': 'Has lots of sharks.'}


Referencing linked Objects
==========================

Embedding linked objects is not always what we want. If we just want to
reference linked objects, we can use a field of type
:class:`lima.fields.Reference`. This field type yields the value of a single
field of the linked object's serialization.

Referencing is similar to embedding save one key difference: In addition to the
schema of the linked object we also provide the name of the field that acts as
our reference to the linked object. We may, for example, reference a book via
its ISBN like this:

.. code-block:: python
    :emphasize-lines: 2,8

    class ReferencingReviewSchema(Schema):
        book = fields.Reference(schema=BookSchema, field='isbn')
        rating = fields.Integer()
        text = fields.String()

    referencing_review_schema = ReferencingReviewSchema()
    referencing_review_schema.dump(review)
    # {'book': '0-684-80122-1',
    #  'rating': 10,
    #  'text': 'Has lots of sharks.'}


Hyperlinks
==========

One application of :class:`~lima.fields.Reference` is linking to ressources via
hyperlinks in RESTful Web Services. Here is a quick sketch:

.. code-block:: python
    :emphasize-lines: 6,12,18

    # your framework should provide something like this
    def book_url(book):
        return 'https://my.service/books/{}'.format(book.isbn)

    class BookSchema(Schema):
        url = fields.String(get=book_url)
        isbn = fields.String()
        author = fields.String()
        title = fields.String()

    class ReviewSchema(Schema):
        book = fields.Reference(schema=BookSchema, field='url')
        rating = fields.Integer()
        text = fields.String()

    review_schema = ReviewSchema()
    review_schema.dump(review)
    # {'book': 'https://my.service/books/0-684-80122-1',
    #  'rating': 10,
    #  'text': 'Has lots of sharks.'}

If you want to do `JSON-LD <http://json-ld.org>`_ and you want to have fields
with names like ``"@id"`` or ``"@context"``, have a look at the section on
:ref:`field_name_mangling` for an easy way to accomplish this.



Two-way Relationships
=====================

Up until now, we've only dealt with one-way relationships (*From* a review *to*
its book). If not only a review should link to its book, but a book should
also link to it's most popular review, we can adapt our model like this:

.. code-block:: python
    :emphasize-lines: 7,19-20

    # books now link to their most popular review
    class Book:
        def __init__(self, isbn, author, title, pop_review=None):
            self.isbn = isbn
            self.author = author
            self.title = title
            self.pop_review = pop_review

    # unchanged: reviews still link to their books
    class Review:
        def __init__(self, rating, text, book=None):
            self.rating = rating
            self.text = text
            self.book = book

    book = Book('0-684-80122-1', 'Hemingway', 'The Old Man and the Sea')
    review = Review(4, "Why doesn't he just kill ALL the sharks?")

    book.pop_review = review
    review.book = book


If we want to construct schemas for models like this, we will have to adress
two problems:

1. **Definition order:** If we define our :class:`BookSchema` first, its
   :attr:`pop_review` attribute will have to reference a :class:`ReviewSchema`
   - but this doesn't exist yet, since we decided to define :class:`BookSchema`
   first. If we decide to define :class:`ReviewSchema` first instead, we run
   into the same problem with its :attr:`book` attribute.

2. **Recursion:** A review links to a book that links to a review that links to
   a book that links to a review that links to a book that links to a review
   that links to a book ``RuntimeError: maximum recursion depth exceeded``

lima makes it easy to deal with those problems:

To overcome the problem of recursion, just exclude the attribute on the other
side that links back.

To overcome the problem of definition order, lima supports lazy evaluation of
schemas. Just pass the *qualified name* (or the *fully module-qualified name*)
of a schema class to :class:`~lima.fields.Embed` instead of the class itself:

.. code-block:: python
    :emphasize-lines: 5,8

    class BookSchema(Schema):
        isbn = fields.String()
        author = fields.String()
        title = fields.String()
        pop_review = fields.Embed(schema='ReviewSchema', exclude='book')

    class ReviewSchema(Schema):
        book = fields.Embed(schema=BookSchema, exclude='pop_review')
        rating = fields.Integer()
        text = fields.String()

Now embedding works both ways:

.. code-block:: python
    :emphasize-lines: 5-6,11-13

    book_schema = BookSchema()
    book_schema.dump(book)
    # {'author': 'Hemingway',
    #  'isbn': '0-684-80122-1',
    #  'pop_review': {'rating': 4,
    #                 'text': "Why doesn't he just kill ALL the sharks?"},
    #  'title': The Old Man and the Sea'}

    review_schema = ReviewSchema()
    review_schema.dump(review)
    # {'book': {'author': 'Hemingway',
    #           'isbn': '0-684-80122-1',
    #           'title': 'The Old Man and the Sea'},
    #  'rating': 4,
    #  'text': "Why doesn't he just kill ALL the sharks?"}

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
        qualified name is simply ``Foo``. Qualified names were introduced with
        Python 3.3 via `PEP 3155 <https://python.org/dev/peps/pep-3155>`_

    The fully module-qualified name
        This is the qualified name of the class prefixed with the full name of
        the module the class is defined in. If you define ``class Qux: pass``
        within a class :class:`Baz` (resulting in the qualified name
        ``Baz.Qux``) at the top level of your ``foo.bar`` module, the class's
        fully module-qualified name is ``foo.bar.Baz.Qux``.

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
    :emphasize-lines: 5,10

    class MarriedPerson:
        def __init__(self, first_name, last_name, spouse=None):
            self.first_name = first_name
            self.last_name = last_name
            self.spouse = spouse

    class MarriedPersonSchema(Schema):
        first_name = fields.String()
        last_name = fields.String()
        spouse = fields.Embed(schema='MarriedPersonSchema', exclude='spouse')


One-to-many and many-to-many Relationships
==========================================

Until now, we've only dealt with one-to-one relations. What about one-to-many
and many-to-many relations? Those link to collections of objects.

We know the necessary building blocks already: Providing additional keyword
arguments to :class:`~lima.fields.Embed` (or :class:`~lima.fields.Reference`
respectively) passes them through to the specified schema's constructor. And
providing ``many=True`` to a schema's construtor will have the schema
marshalling collections - so if our model looks like this:


.. code-block:: python
    :emphasize-lines: 7,16-20

    # books now have a list of reviews
    class Book:
        def __init__(self, isbn, author, title):
            self.isbn = isbn
            self.author = author
            self.title = title
            self.reviews = []

    class Review:
        def __init__(self, rating, text, book=None):
            self.rating = rating
            self.text = text
            self.book = book

    book = Book('0-684-80122-1', 'Hemingway', 'The Old Man and the Sea')
    book.reviews = [
        Review(10, 'Has lots of sharks.', book),
        Review(4, "Why doesn't he just kill ALL the sharks?", book),
        Review(8, 'Better than the movie!', book),
    ]

... we wourld define our schemas like this:

.. code-block:: python
    :emphasize-lines: 5-7,10

    class BookSchema(Schema):
        isbn = fields.String()
        author = fields.String()
        title = fields.String()
        reviews = fields.Embed(schema='ReviewSchema',
                               many=True,
                               exclude='book')

    class ReviewSchema(Schema):
        book = fields.Embed(schema=BookSchema, exclude='reviews')
        rating = fields.Integer()
        text = fields.String()

... which enables us to serialize a book object with many reviews:

.. code-block:: python
    :emphasize-lines: 5-8

    book_schema = BookSchema()
    book_schema.dump(book)
    # {'author': 'Hemingway',
    #  'isbn': '0-684-80122-1',
    #  'reviews': [
    #       {'rating': 10, 'text': 'Has lots of sharks.'},
    #       {'rating': 4, 'text': "Why doesn't he just kill ALL the sharks?"},
    #       {'rating': 8, 'text': 'Better than the movie!'}],
    #  'title': The Old Man and the Sea'


Linked Data Recap
=================

- You now know how to marshal embedded linked objects (via a field of type
  :class:`lima.fields.Embed`)

- You now know how to marshal references to linked objects (via a field of
  type :class:`lima.fields.References`)

- You know about lazy evaluation of linked schemas and how to specify those via
  qualified and fully module-qualified names.

- You know how to implement two-way relationships between objects (pass
  ``exclude`` or ``only`` to the linked schema through
  :class:`lima.fields.Embed`)

- You know how to marshal linked collections of objects (pass ``many=True`` to
  the linked schema through :class:`lima.fields.Embed`)
