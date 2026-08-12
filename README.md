# flake8-datetimez

A plugin for flake8 to ban the usage of unsafe naive datetime class.


## Consider using Ruff instead

The checks of this plugin have been adopted into [Ruff](https://docs.astral.sh/ruff/)
as its [`flake8-datetimez` (`DTZ`) rule set](https://docs.astral.sh/ruff/rules/#flake8-datetimez-dtz).
Many thanks to the Ruff project for carrying these rules forward — their
implementation is faster, more actively maintained, and handles more cases than
this plugin does.

If you are starting a new project, or already run Ruff, please prefer it:

```toml
# pyproject.toml
[tool.ruff.lint]
extend-select = ["DTZ"]
```

This plugin remains for codebases that are still on flake8, and is maintained on
a **best-effort basis for backward compatibility** — keeping the existing rules
working across the supported Python and flake8 versions, rather than growing new
ones.


## List of warnings

- **DTZ001** : The use of `datetime.datetime()` without `tzinfo` argument is not allowed.

- **DTZ002** : The use of `datetime.datetime.today()` is not allowed. Use `datetime.datetime.now(tz=)` instead.

- **DTZ003** : The use of `datetime.datetime.utcnow()` is not allowed. Use `datetime.datetime.now(tz=)` instead.

- **DTZ004** : The use of `datetime.datetime.utcfromtimestamp()` is not allowed. Use `datetime.datetime.fromtimestamp(, tz=)` instead.

- **DTZ005** : The use of `datetime.datetime.now()` without `tz` argument is not allowed.

- **DTZ006** : The use of `datetime.datetime.fromtimestamp()` without `tz` argument is not allowed.

- **DTZ007** : The use of `datetime.datetime.strptime()` without %z must be followed by `.replace(tzinfo=)`.

- **DTZ011** : The use of `datetime.date.today()` is not allowed. Use `datetime.datetime.now(tz=).date()` instead.

- **DTZ012** : The use of `datetime.date.fromtimestamp()` is not allowed. Use `datetime.datetime.fromtimestamp(, tz=).date()` instead.

- **DTZ901** : The use of `datetime.datetime.min` or `datetime.datetime.max` without `.replace(tzinfo=)` is not allowed.


## About `.astimezone()`

Calling `.astimezone()` on a naive datetime attaches the **local** timezone to it, so it is
accepted as a way to resolve **DTZ001**, **DTZ002**, **DTZ005**, **DTZ006** and **DTZ007**:

```python
datetime.datetime.now().astimezone()  # ok
datetime.datetime(2000, 1, 1).astimezone()  # ok
```

It is deliberately *not* accepted for the remaining warnings:

- **DTZ003**, **DTZ004** : `utcnow()` and `utcfromtimestamp()` return a UTC wall clock. Reading
  that value as local time shifts the instant, so `utcnow().astimezone()` is off by the local UTC
  offset, which is exactly what these two warnings are meant to prevent.

- **DTZ011**, **DTZ012** : `datetime.date` has no `.astimezone()` at all.

- **DTZ901** : `datetime.min` and `datetime.max` overflow when converted to another timezone.


## Install

Install with pip

```
$ pip install flake8-datetimez
```

## Requirements
- Python 3.8 or above (tested on 3.8 through 3.14)
- flake8 3.0.0 or above


## Running the tests

The test suite runs against every supported Python version with
[tox](https://tox.wiki). No interpreter has to be installed beforehand, they are
downloaded automatically by [uv](https://docs.astral.sh/uv/):

```
$ uvx --with tox-uv tox
```

That covers `py38` through `py314` plus a `lint` environment, and it is exactly
what CI runs, one job per environment. To run a single environment, or the tests
with the current interpreter only:

```
$ uvx --with tox-uv tox -e py314
$ python -m unittest discover -p "test_*.py" -v
```


## Linting and formatting

The code is formatted and linted with [ruff](https://docs.astral.sh/ruff/):

```
$ uvx ruff format .
$ uvx ruff check .
```


## License

MIT
