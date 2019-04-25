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

    def test_DTZ001(self):
        errors = self.write_file_and_run_checker(
            'datetime.datetime.utcnow()'
        )
        self.assert_codes(errors, ['DTZ001'])

    # DTZ002

    def test_DTZ002(self):
        errors = self.write_file_and_run_checker(
            'datetime.datetime.utcfromtimestamp(1234)'
        )
        self.assert_codes(errors, ['DTZ002'])

    # DTZ003

    def test_DTZ003_args_good(self):
        errors = self.write_file_and_run_checker(
            'datetime.datetime.now(datetime.timezone.utc)'
        )
        self.assert_codes(errors, [])

    def test_DTZ003_keywords_good(self):
        errors = self.write_file_and_run_checker(
            'datetime.datetime.now(tz=datetime.timezone.utc)'
        )
        self.assert_codes(errors, [])

    def test_DTZ003_no_args(self):
        errors = self.write_file_and_run_checker(
            'datetime.datetime.now()'
        )
        self.assert_codes(errors, ['DTZ003'])

    def test_DTZ003_wrong_keywords(self):
        errors = self.write_file_and_run_checker(
            'datetime.datetime.now(bad=datetime.timezone.utc)'
        )
        self.assert_codes(errors, ['DTZ003'])

    def test_DTZ003_none_arg(self):
        errors = self.write_file_and_run_checker(
            'datetime.datetime.now(None)'
        )
        self.assert_codes(errors, ['DTZ003'])

    def test_DTZ003_none_keywords(self):
        errors = self.write_file_and_run_checker(
            'datetime.datetime.now(tz=None)'
        )
        self.assert_codes(errors, ['DTZ003'])

    # DTZ004

    def test_DTZ004_args_good(self):
        errors = self.write_file_and_run_checker(
            'datetime.datetime.fromtimestamp(1234, datetime.timezone.utc)'
        )
        self.assert_codes(errors, [])

    def test_DTZ004_keywords_good(self):
        errors = self.write_file_and_run_checker(
            'datetime.datetime.fromtimestamp(1234, tz=datetime.timezone.utc)'
        )
        self.assert_codes(errors, [])

    def test_DTZ004_no_args(self):
        errors = self.write_file_and_run_checker(
            'datetime.datetime.fromtimestamp(1234)'
        )
        self.assert_codes(errors, ['DTZ004'])

    def test_DTZ004_wrong_keywords(self):
        errors = self.write_file_and_run_checker(
            'datetime.datetime.fromtimestamp(1234, bad=datetime.timezone.utc)'
        )
        self.assert_codes(errors, ['DTZ004'])

    def test_DTZ004_none_arg(self):
        errors = self.write_file_and_run_checker(
            'datetime.datetime.fromtimestamp(1234, None)'
        )
        self.assert_codes(errors, ['DTZ004'])

    def test_DTZ004_none_keywords(self):
        errors = self.write_file_and_run_checker(
            'datetime.datetime.fromtimestamp(1234, tz=None)'
        )
        self.assert_codes(errors, ['DTZ004'])

    # DTZ005

    def test_DTZ005_good(self):
        errors = self.write_file_and_run_checker(
            'datetime.datetime.strptime(something, something).replace(tzinfo=datetime.timezone.utc)'
        )
        self.assert_codes(errors, [])

    def test_DTZ005_no_replace(self):
        errors = self.write_file_and_run_checker(
            'datetime.datetime.strptime(something, something)'
        )
        self.assert_codes(errors, ['DTZ005'])

    def test_DTZ005_wrong_replace(self):
        errors = self.write_file_and_run_checker(
            'datetime.datetime.strptime(something, something).replace(hour=1)'
        )
        self.assert_codes(errors, ['DTZ005'])

    def test_DTZ005_none_replace(self):
        errors = self.write_file_and_run_checker(
            'datetime.datetime.strptime(something, something).replace(tzinfo=None)'
        )
        self.assert_codes(errors, ['DTZ005'])
