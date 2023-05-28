Contributing
============

Contributions are welcome.

Local development
-----------------

Dependencies
^^^^^^^^^^^^

You need at least the following list of tools installed:

- Python >= 3.8 (The library supports all Python versions >= 3.8, so all code needs to be backwards compatible with 3.8)
- `Poetry <https://python-poetry.org/>`_ >= 1.3.0
- `Pre-Commit <https://pre-commit.com/>`_ (optional)

Make sure that you install all dependencies, even the optional ones.

.. code-block:: sh

   poetry install --all-extras

In a shell activate the virtual environment from poetry with `poetry shell`, and/or in an IDE set the path to the virtual environment which you can get via `poetry env info`.

Formatting / Linting
^^^^^^^^^^^^^^^^^^^^

Code formatting is done with `Black <https://black.readthedocs.io/en/stable/>`_, linting with `Ruff <https://beta.ruff.rs/>`_.

To get formatting/linting support in your IDE you might need to configure your IDE or install IDE extensions.
However you can also run them in a shell with:

.. code-block:: sh

   # check code style and fix potential issues
   black .

   # lint the code
   ruff .
   # lint and fix autofixable problems
   ruff . --fix

Both tools can also be run automatically before each commit with Pre-Commit.
You just need to activate Pre-Commit once.

.. code-block:: sh

   pre-commit install

Testing / Static type checking
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Testing is done via `pytest`, and static type checks are performed by `Mypy <https://mypy-lang.org/>`_.

Additionally you can use `tox <https://tox.wiki>`_ to run all checks and tests in multiple Python versions.
tox will create new virtual environments for every Python version, make sure that Poetry and all the project's dependencies are installed in it, and then run the checks.
However tox can only work with Python versions that it can find, so you need to install them (e.g. with `pyenv <https://github.com/pyenv/pyenv>`_).

.. code-block:: sh

   # run tests
   pytest

   # run static type checker
   mypy

   # run everything with Python 3.8
   # similar for 3.9, 3.10 and 3.11
   tox -e py38

   # run everything in all supported Python versions
   tox

Continuous Integration
----------------------

All mentioned checks in the section above (formatting, linting, tests, static type checks) are also automatically run for every single Pull Request on Github.

Deployments
-----------

The library is versioned using `Semantic Versioning <https://semver.org/>`_.
To release a new version, create a `Github Release <https://github.com/dataclass-mapper/dataclass-mapper/releases>`_ and specify a new version number (e.g. :code:`v1.7.2`) as tag.
Once the release is published, the new tag is created and a Github Action pipeline is triggered.
The pipeline needs to be approved by a core developer, and afterwards the library is deployed to `Pypi <https://pypi.org/project/dataclass-mapper/>`_.
