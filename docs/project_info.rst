============
Project Info
============

lima was started in 2014 by Bernhard Weitzhofer.


Acknowledgements
================

lima is heavily inspired by `marshmallow
<http://marshmallow.readthedocs.org>`_, from which it lifts most of its
concepts from.

.. note::

    The key differences between lima and marshmallow are (from my, Bernhard's
    point of view):

    - marshmallow supports Python 2 as well, lima is Python 3 only.

    - marshmallow has more features, foremost among them deserialization and
      validation.

    - :ref:`Skipping validation <data_validation>` and doing internal stuff
      differently, lima is (at the time of writing this) noticeably faster.

    Although greatly inspired by marshmallow's API, the lima API differs from
    marshmallow's. lima is not a drop-in replacement for marshmallow and it
    does not intend to become one.

The lima sources include a copy of the  `Read the Docs Sphinx Theme
<https://github.com/snide/sphinx_rtd_theme>`_.

The author believes to have benefited a lot from looking at the documentation
and source code of other awesome projects, among them
`django <https://www.djangoproject.com>`_,
`morepath <https://morepath.readthedocs.org>`_,
`Pyramid <http://www.pylonsproject.org>`_
(:class:`lima.util.reify` was taken from there) and
`SQLAlchemy <http://www.sqlalchemy.org>`_ as well as the Python standard
library itself. (Seriously, look in there!)


About the Image
===============

The Vicuña is the smallest and lightest camelid in the world. In this 1914
illustration [#]_, it is depicted next to its bigger and heavier relatives, the
Llama and the Alpaca.

Despite its delicate frame, the Vicuña is perfectly adapted to the harsh
conditions in the high alpine regions of the Andes. It is a mainly wild animal
long time believed to never have been domesticated. Reports of Vicuñas
breathing fire are exaggerated.

.. [#] Beach, C. (Ed.). (1914). The New Student's Reference Work. Chicago: F.
   E. Compton and Company (via `Wikisource <http://en.wikisource.org/wiki/
   The_New_Student%27s_Reference_Work>`_).
