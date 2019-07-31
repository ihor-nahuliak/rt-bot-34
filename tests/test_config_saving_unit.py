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
        cls.report_filename = '/tmp/.report.html'

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

    def test_save_var(self):
        config = Config(config_filename=self.config_filename,
                        hubstaff_app_token='A' * 43,
                        hubstaff_auth_token='B' * 43,
                        hubstaff_username='test@hubstaff.com',
                        hubstaff_password='test123456',
                        report_filename='/tmp/.test.html',
                        report_date=datetime.date(2001, 2, 3),
                        report_days_ago=3)
        config.save()

        with open(self.config_filename) as f:
            config_text = f.read()

        self.assertIn('''[hubstaff]
app_token = AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
auth_token = BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB
username = test@hubstaff.com
password = test123456
''', config_text)
        self.assertIn('''[report]
html_file = /tmp/.test.html
date = 2001-02-03
days_ago = 3
''', config_text)


if __name__ == '__main__':
    unittest.main()
