try:
    import unittest
except ImportError:
    import unittest2 as unittest

import os
import datetime

from rtbot34 import Config


class TestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.root_path = os.path.dirname(os.path.dirname(__file__))
        cls.home_path = os.path.expanduser('~')
        cls.test_path = os.path.dirname(__file__)
        cls.config_filename = '/tmp/.configrc'
        cls.tmp_config_filename = os.path.join(cls.test_path, '.tmprc')
        cls.report_filename = '/tmp/.report.html'
        cls.tmp_report_filename = os.path.join(cls.test_path, '.tmp.html')
        cls.env_report_filename = os.path.join(cls.test_path, '.env.html')
        cls.default_report_filename = os.path.join(
            cls.home_path, 'rtbot34.html')

    def setUp(self):
        if os.path.exists(self.config_filename):
            os.remove(self.config_filename)
        with open(self.config_filename, 'w+') as f:
            f.writelines('''
[hubstaff]
app_token=MMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMM
auth_token=NNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNN
username=conf@hubstaff.com
password=conf123456

[report]
html_file=/tmp/.report.html
date=2012-03-04
days_ago=2
            ''')
        if os.path.exists(self.tmp_config_filename):
            os.remove(self.tmp_config_filename)
        if os.path.exists(self.report_filename):
            os.remove(self.report_filename)
        if os.path.exists(self.tmp_report_filename):
            os.remove(self.tmp_report_filename)
        if os.path.exists(self.env_report_filename):
            os.remove(self.env_report_filename)
        self._clear_env_variables()

    @classmethod
    def _clear_env_variables(cls):
        os.environ.pop('HUBSTAFF_APP_TOKEN', None)
        os.environ.pop('HUBSTAFF_AUTH_TOKEN', None)
        os.environ.pop('HUBSTAFF_USERNAME', None)
        os.environ.pop('HUBSTAFF_PASSWORD', None)
        os.environ.pop('REPORT_FILENAME', None)
        os.environ.pop('REPORT_DATE', None)
        os.environ.pop('REPORT_DAYS_AGO', None)

    @classmethod
    def _set_env_variables(cls):
        os.environ['HUBSTAFF_APP_TOKEN'] = 'A' * 43
        os.environ['HUBSTAFF_AUTH_TOKEN'] = 'B' * 43
        os.environ['HUBSTAFF_USERNAME'] = 'env@hubstaff.com'
        os.environ['HUBSTAFF_PASSWORD'] = 'env123456'
        os.environ['REPORT_FILENAME'] = 'tests/.env.html'
        os.environ['REPORT_DATE'] = '2001-02-03'
        os.environ['REPORT_DAYS_AGO'] = '3'

    def test_constructor_var_is_preferred_than_env_var(self):
        self._set_env_variables()

        config = Config(config_filename=self.tmp_config_filename,
                        hubstaff_app_token='X' * 43,
                        hubstaff_auth_token='Y' * 43,
                        hubstaff_username='test@hubstaff.com',
                        hubstaff_password='test123456',
                        report_filename=self.tmp_report_filename,
                        report_date='2000-01-02',
                        report_days_ago=4)
        config.load()

        self.assertEqual(config.hubstaff_app_token, 'X' * 43)
        self.assertEqual(config.hubstaff_auth_token, 'Y' * 43)
        self.assertEqual(config.hubstaff_username, 'test@hubstaff.com')
        self.assertEqual(config.hubstaff_password, 'test123456')
        self.assertEqual(config.report_filename, self.tmp_report_filename)
        self.assertEqual(config.report_date, datetime.date(2000, 1, 2))
        self.assertEqual(config.report_days_ago, 4)

    def test_env_var_is_preferred_than_conf_var(self):
        self._set_env_variables()

        config = Config(config_filename=self.config_filename)
        config.load()

        self.assertEqual(config.hubstaff_app_token, 'A' * 43)
        self.assertEqual(config.hubstaff_auth_token, 'B' * 43)
        self.assertEqual(config.hubstaff_username, 'env@hubstaff.com')
        self.assertEqual(config.hubstaff_password, 'env123456')
        self.assertEqual(config.report_filename, self.env_report_filename)
        self.assertEqual(config.report_date, datetime.date(2001, 2, 3))
        self.assertEqual(config.report_days_ago, 3)

    def test_conf_var_is_preferred_than_default_var(self):
        config = Config(config_filename=self.config_filename)
        config.load()

        self.assertEqual(config.hubstaff_app_token, 'M' * 43)
        self.assertEqual(config.hubstaff_auth_token, 'N' * 43)
        self.assertEqual(config.hubstaff_username, 'conf@hubstaff.com')
        self.assertEqual(config.hubstaff_password, 'conf123456')
        self.assertEqual(config.report_filename, self.report_filename)
        self.assertEqual(config.report_date, datetime.date(2012, 3, 4))
        self.assertEqual(config.report_days_ago, 2)

    def test_load_default_var(self):
        config = Config(config_filename=self.tmp_config_filename,
                        hubstaff_app_token='X' * 43)
        config.load()

        self.assertEqual(config.hubstaff_app_token, 'X' * 43)
        self.assertIsNone(config.hubstaff_auth_token)
        self.assertIsNone(config.hubstaff_username, 'conf@hubstaff.com')
        self.assertIsNone(config.hubstaff_password, 'conf123456')
        self.assertEqual(config.report_filename, self.default_report_filename)
        self.assertIsNone(config.report_date)
        self.assertEqual(config.report_days_ago, 1)


if __name__ == '__main__':
    unittest.main()
