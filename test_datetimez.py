import tempfile
import unittest

from flake8_datetimez import DateTimeZChecker


class TestDateTimeZ(unittest.TestCase):
    def assert_codes(self, errors, codes):
        self.assertEqual(len(errors), len(codes))
        for error, code in zip(errors, codes):
            self.assertTrue(error.message.startswith(code + ' '))

    def write_file_and_run_checker(self, content):
        with tempfile.NamedTemporaryFile('w') as f:
            f.write(content)
            f.flush()
            checker = DateTimeZChecker(None, f.name)
            return list(checker.run())

    # DTZ001

    def test_DTZ001_args_good(self):
        errors = self.write_file_and_run_checker(
            'datetime.datetime(2000, 1, 1, 0, 0, 0, 0, datetime.timezone.utc)'
        )
        self.assert_codes(errors, [])

    def test_DTZ001_kwargs_good(self):
        errors = self.write_file_and_run_checker(
            'datetime.datetime(2000, 1, 1, tzinfo=datetime.timezone.utc)'
        )
        self.assert_codes(errors, [])

    def test_DTZ001_no_args(self):
        errors = self.write_file_and_run_checker(
            'datetime.datetime(2000, 1, 1, 0, 0, 0)'
        )
        self.assert_codes(errors, ['DTZ001'])

    def test_DTZ001_no_args_unqualified(self):
        errors = self.write_file_and_run_checker(
            'datetime(2000, 1, 1, 0, 0, 0)'
        )
        self.assert_codes(errors, ['DTZ001'])

    def test_DTZ001_none_args(self):
        errors = self.write_file_and_run_checker(
            'datetime.datetime(2000, 1, 1, 0, 0, 0, 0, None)'
        )
        self.assert_codes(errors, ['DTZ001'])

    def test_DTZ001_no_kwargs(self):
        errors = self.write_file_and_run_checker(
            'datetime.datetime(2000, 1, 1, fold=1)'
        )
        self.assert_codes(errors, ['DTZ001'])

    def test_DTZ001_none_kwargs(self):
        errors = self.write_file_and_run_checker(
            'datetime.datetime(2000, 1, 1, tzinfo=None)'
        )
        self.assert_codes(errors, ['DTZ001'])

    # DTZ002

    def test_DTZ002(self):
        errors = self.write_file_and_run_checker(
            'datetime.datetime.today()'
        )
        self.assert_codes(errors, ['DTZ002'])

    def test_DTZ002_unqualified(self):
        errors = self.write_file_and_run_checker(
            'datetime.today()'
        )
        self.assert_codes(errors, ['DTZ002'])

    # DTZ003

    def test_DTZ003(self):
        errors = self.write_file_and_run_checker(
            'datetime.datetime.utcnow()'
        )
        self.assert_codes(errors, ['DTZ003'])

    def test_DTZ003_unqualified(self):
        errors = self.write_file_and_run_checker(
            'datetime.utcnow()'
        )
        self.assert_codes(errors, ['DTZ003'])

    # DTZ004

    def test_DTZ004(self):
        errors = self.write_file_and_run_checker(
            'datetime.datetime.utcfromtimestamp(1234)'
        )
        self.assert_codes(errors, ['DTZ004'])

    def test_DTZ004_unqualified(self):
        errors = self.write_file_and_run_checker(
            'datetime.utcfromtimestamp(1234)'
        )
        self.assert_codes(errors, ['DTZ004'])

    # DTZ005

    def test_DTZ005_args_good(self):
        errors = self.write_file_and_run_checker(
            'datetime.datetime.now(datetime.timezone.utc)'
        )
        self.assert_codes(errors, [])

    def test_DTZ005_keywords_good(self):
        errors = self.write_file_and_run_checker(
            'datetime.datetime.now(tz=datetime.timezone.utc)'
        )
        self.assert_codes(errors, [])

    def test_DTZ005_no_args(self):
        errors = self.write_file_and_run_checker(
            'datetime.datetime.now()'
        )
        self.assert_codes(errors, ['DTZ005'])

    def test_DTZ005_no_args_unqualified(self):
        errors = self.write_file_and_run_checker(
            'datetime.now()'
        )
        self.assert_codes(errors, ['DTZ005'])

    def test_DTZ005_wrong_keywords(self):
        errors = self.write_file_and_run_checker(
            'datetime.datetime.now(bad=datetime.timezone.utc)'
        )
        self.assert_codes(errors, ['DTZ005'])

    def test_DTZ005_none_args(self):
        errors = self.write_file_and_run_checker(
            'datetime.datetime.now(None)'
        )
        self.assert_codes(errors, ['DTZ005'])

    def test_DTZ005_none_keywords(self):
        errors = self.write_file_and_run_checker(
            'datetime.datetime.now(tz=None)'
        )
        self.assert_codes(errors, ['DTZ005'])

    # DTZ006

    def test_DTZ006_args_good(self):
        errors = self.write_file_and_run_checker(
            'datetime.datetime.fromtimestamp(1234, datetime.timezone.utc)'
        )
        self.assert_codes(errors, [])

    def test_DTZ006_keywords_good(self):
        errors = self.write_file_and_run_checker(
            'datetime.datetime.fromtimestamp(1234, tz=datetime.timezone.utc)'
        )
        self.assert_codes(errors, [])

    def test_DTZ006_no_args(self):
        errors = self.write_file_and_run_checker(
            'datetime.datetime.fromtimestamp(1234)'
        )
        self.assert_codes(errors, ['DTZ006'])

    def test_DTZ006_no_args_unqualified(self):
        errors = self.write_file_and_run_checker(
            'datetime.fromtimestamp(1234)'
        )
        self.assert_codes(errors, ['DTZ006'])

    def test_DTZ006_wrong_keywords(self):
        errors = self.write_file_and_run_checker(
            'datetime.datetime.fromtimestamp(1234, bad=datetime.timezone.utc)'
        )
        self.assert_codes(errors, ['DTZ006'])

    def test_DTZ006_none_args(self):
        errors = self.write_file_and_run_checker(
            'datetime.datetime.fromtimestamp(1234, None)'
        )
        self.assert_codes(errors, ['DTZ006'])

    def test_DTZ006_none_keywords(self):
        errors = self.write_file_and_run_checker(
            'datetime.datetime.fromtimestamp(1234, tz=None)'
        )
        self.assert_codes(errors, ['DTZ006'])

    # DTZ007

    def test_DTZ007_good_replace(self):
        errors = self.write_file_and_run_checker(
            'datetime.datetime.strptime(something, something).replace(tzinfo=datetime.timezone.utc)'
        )
        self.assert_codes(errors, [])

    def test_DTZ007_good_astimezone(self):
        errors = self.write_file_and_run_checker(
            'datetime.datetime.strptime(something, something).astimezone()'
        )
        self.assert_codes(errors, [])

    def test_DTZ007_good_format(self):
        errors = self.write_file_and_run_checker(
            'datetime.datetime.strptime(something, "%H:%M:%S%z")'
        )
        self.assert_codes(errors, [])

    def test_DTZ007_bad_format(self):
        errors = self.write_file_and_run_checker(
            'datetime.datetime.strptime(something, "%H:%M:%S%Z")'
        )
        self.assert_codes(errors, ['DTZ007'])

    def test_DTZ007_no_replace_or_astimezone(self):
        errors = self.write_file_and_run_checker(
            'datetime.datetime.strptime(something, something)'
        )
        self.assert_codes(errors, ['DTZ007'])

    def test_DTZ007_no_replace_or_astimezone_unqualified(self):
        errors = self.write_file_and_run_checker(
            'datetime.strptime(something, something)'
        )
        self.assert_codes(errors, ['DTZ007'])

    def test_DTZ007_wrong_replace(self):
        errors = self.write_file_and_run_checker(
            'datetime.datetime.strptime(something, something).replace(hour=1)'
        )
        self.assert_codes(errors, ['DTZ007'])

    def test_DTZ007_none_replace(self):
        errors = self.write_file_and_run_checker(
            'datetime.datetime.strptime(something, something).replace(tzinfo=None)'
        )
        self.assert_codes(errors, ['DTZ007'])

    # DTZ011

    def test_DTZ011(self):
        errors = self.write_file_and_run_checker(
            'datetime.date.today()'
        )
        self.assert_codes(errors, ['DTZ011'])

    def test_DTZ011_unqualified(self):
        errors = self.write_file_and_run_checker(
            'date.today()'
        )
        self.assert_codes(errors, ['DTZ011'])

    # DTZ012

    def test_DTZ012(self):
        errors = self.write_file_and_run_checker(
            'datetime.date.fromtimestamp(1234)'
        )
        self.assert_codes(errors, ['DTZ012'])

    def test_DTZ012_unqualified(self):
        errors = self.write_file_and_run_checker(
            'date.fromtimestamp(1234)'
        )
        self.assert_codes(errors, ['DTZ012'])
