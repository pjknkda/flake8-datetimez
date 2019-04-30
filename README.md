# flake8-datetimez

A plugin for flake8 to ban the usage of unsafe naive datetime class.


## List of warnings

- **DTZ001** : The use of `datetime.datetime()` without `tzinfo` argument is not allowed.

- **DTZ002** : The use of `datetime.datetime.today()` is not allowed. Use `datetime.datetime.now(tz=)` instead.

- **DTZ003** : The use of `datetime.datetime.utcnow()` is not allowed. Use `datetime.datetime.now(tz=)` instead.

- **DTZ004** : The use of `datetime.datetime.utcfromtimestamp()` is not allowed. Use `datetime.datetime.fromtimestamp(, tz=)` instead.

- **DTZ005** : The use of `datetime.datetime.now()` without `tz` argument is not allowed.

- **DTZ006** : The use of `datetime.datetime.fromtimestamp()` without `tz` argument is not allowed.

- **DTZ007** : The use of `datetime.datetime.strptime()` must be followed by `.replace(tzinfo=)`.

- **DTZ011** : The use of `datetime.date.today()` is not allowed. Use `datetime.datetime.now(tz=).date()` instead.

- **DTZ012** : The use of `datetime.date.fromtimestamp()` is not allowed. Use `datetime.datetime.fromtimestamp(, tz=).date()` instead.


## Install

Install with pip

```
$ pip install flake8-datetimez
```

## Requirements
- Python 3.6 or above
- flake8 3.0.0 or above

## License

MIT
