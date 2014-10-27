.. admonition:: Keyword-only arguments
    :class: note

    Keyword-only arguments can be recognized by their position in a
    method/function signature: Every argument coming after the varargs argument
    like ``*args`` (or after a single ``*``) is a keyword-only argument.

    A function that is defined as ``def foo(*, x, y): pass`` *must* be called
    like this: ``foo(x=1, y=2)``; calling ``foo(1, 2)`` will raise a
    ``TypeError``.

    It is the author's opinion that enforcing keyword arguments in the right
    places makes the resulting code more readable.

    For more information about keyword-only arguments, see `PEP 3102
    <https://python.org/dev/peps/pep-3102>`_

