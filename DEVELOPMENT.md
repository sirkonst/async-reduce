Development
===========

Requires:

* python >= 3.7


Prepare the environment
-----------------------

- Setup and activate virtual environment like:

```bash
$ python3 -m venv .venv

# for bash
$ source .venv/bin/activate

# for fish
$ . .venv/bin/activate.fish
```

- Update pre-install dependencies:

```bash
$ pip install 'setuptools >= 30.4' -U
$ pip install pip -U
```

- Install development version:

```bash
$ make install_dev
```


Run tests
---------

```bash
# Full-tests in a clean environment:
$ make test

# Re-run full-tests in exists environment (more quickly):
$ tox

# Run simple tests on local environment:
$ pytest
```
