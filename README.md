# provision_py_proj

Provision an empty Python package.

Create empty Package with following structure:

    test_pkg
    ├── bin
    │   └── test_pkg
    ├── .gitignore
    ├── LICENSE.txt
    ├── MANIFEST.in
    ├── README.md
    ├── requirements.txt
    ├── setup.py
    └── test_pkg
        ├── __init__.py
        └── test
            └── __init__.py


# Installation

python3 -m pip install --index-url https://test.pypi.org/simple/ provision_py_proj
provision_py_proj --help

