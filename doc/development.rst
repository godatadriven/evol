.. image:: https://i.imgur.com/7MHcIq1.png
   :align: center

Development
===========

Installing from PyPi
^^^^^^^^^^^^^^^^^^^^

We currently support python3.6 and python3.7 and you can install it via pip.

.. code-block:: bash

   pip install evol

Developing Locally with Makefile
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

You can also fork/clone the repository on Github_ to work on it locally. we've
added a `Makefile` to the project that makes it easy to install everything ready
for development.

.. code-block:: bash

   make develop

There's some other helpful commands in there. For example, testing can be done via;

.. code-block:: bash

   make test

This will pytest and possibly in the future also the docstring tests.

Generating Documentation
^^^^^^^^^^^^^^^^^^^^^^^^

The easiest way to generate documentation is by running:

.. code-block:: bash

    make docs

This will populate the `/docs` folder locally. Note that we ignore the
contents of the this folder per git ignore because building the documentation
is something that we outsource to the read-the-docs service.

.. _Github: https://scikit-learn.org/stable/modules/compose.html

