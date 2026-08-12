# flake8-datetimez

A plugin for flake8 to ban the usage of unsafe naive datetime class.


## List of warnings

- **DTZ001** : The use of `datetime.datetime()` without `tzinfo` argument is not allowed.

- **DTZ002** : The use of `datetime.datetime.today()` is not allowed. Use `datetime.datetime.now(tz=)` instead.

- **DTZ003** : The use of `datetime.datetime.utcnow()` is not allowed. Use `datetime.datetime.now(tz=)` instead.

- **DTZ004** : The use of `datetime.datetime.utcfromtimestamp()` is not allowed. Use `datetime.datetime.fromtimestamp(, tz=)` instead.

- **DTZ005** : The use of `datetime.datetime.now()` without `tz` argument is not allowed.

- **DTZ006** : The use of `datetime.datetime.fromtimestamp()` without `tz` argument is not allowed.

- **DTZ007** : The use of `datetime.datetime.strptime()` without %z must be followed by `.replace(tzinfo=)` or `.astimezone()`.

- **DTZ011** : The use of `datetime.date.today()` is not allowed. Use `datetime.datetime.now(tz=).date()` instead.

- **DTZ012** : The use of `datetime.date.fromtimestamp()` is not allowed. Use `datetime.datetime.fromtimestamp(, tz=).date()` instead.


## Install

Install with pip

```
$ pip install flake8-datetimez
```

## Requirements
- Python 3.8 or above (tested on 3.8 through 3.14)
- flake8 3.0.0 or above


## Development

Run the test suite and the linter against every supported Python version with
[tox](https://tox.wiki) (interpreters are downloaded automatically by
[uv](https://docs.astral.sh/uv/)):

```
$ uvx --with tox-uv tox
```

To run a single environment, or the tests with the current interpreter only:

```
$ uvx --with tox-uv tox -e py314
$ uvx --with tox-uv tox -e lint
$ python -m unittest discover -p "test_*.py" -v
```

CI runs the very same environments, one job per `tox` environment.

The code is formatted and linted with [ruff](https://docs.astral.sh/ruff/):

```
$ uvx ruff format .
$ uvx ruff check .
```


## License

MIT
