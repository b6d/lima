============
Installation
============

The recommended way to install lima is via `pip <https://www.pip.pypa.io>`_.

Just make sure you have at least Python 3.3 and a matching version of pip
available and installing lima becomes a one-liner:

.. code-block:: sh

    $ pip install lima

Most of the time it's also a good idea to do this in an isolated virtual
environment.

Starting with version 3.4, Python handles all of this (creation of virtual
environments, ensuring the availability of pip) out of the box:

.. code-block:: sh

    $ python3 -m venv /path/to/my_venv
    $ source /path/to/my_venv/bin/activate
    (my_venv) $ pip install lima

If you should run into trouble, the `Tutorial on Installing Distributions
<https://packaging.python.org/en/latest/installing.html>`_ from the `Python
Packaging User Guide <https://packaging.python.org/en/latest/index.html>`_
might be helpful.
