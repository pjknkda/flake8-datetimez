# flake8-datetimez

Check for python unsafe naive `datetime` module usages.


## List of warnings

**DTZ001**: The use of `datetime.datetime.utcnow()` is not allowed.

**DTZ002**: The use of `datetime.datetime.utcfromtimestamp()` is not allowed.

**DTZ003**: The use of `datetime.datetime.now()` without `tz` argument is not allowed.

**DTZ004**: The use of `datetime.datetime.fromtimestamp()` without `tz` argument is not allowed.

**DTZ005**: The use of `datetime.datetime.strptime()` must be followed by `.replace(tzinfo=)`


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
