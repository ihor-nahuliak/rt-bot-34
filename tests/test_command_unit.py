import unittest
from unittest import mock
import os
import logging
import datetime


class TestCase(unittest.TestCase):

    def setUp(self):
        if os.path.exists('/tmp/.rtbot34rc'):
            os.remove('/tmp/.rtbot34rc')

        if os.path.exists('/tmp/.rtbot34.html'):
            os.remove('/tmp/.rtbot34.html')

        patch = mock.patch('rtbot34.Config')
        self.m_config_class = patch.start()
        self.m_config = self.m_config_class.return_value = mock.Mock()
        self.addCleanup(patch.stop)

        patch = mock.patch('rtbot34.HubstaffClient')
        self.m_hubstaff_class = patch.start()
        self.m_hubstaff = self.m_hubstaff_class.return_value = mock.Mock()
        self.auth_token = self.m_hubstaff.authenticate.return_value = 'Y' * 43
        self.m_hubstaff.get_users_list.return_value = [
            {'id': 1, 'name': 'Alice', 'projects': [
                {'id': 101, 'name': 'Project A'},
                {'id': 102, 'name': 'Project B'},
                {'id': 103, 'name': 'Project C'},
            ]},
            {'id': 2, 'name': 'Bob', 'projects': [
                {'id': 101, 'name': 'Project A'},
                {'id': 102, 'name': 'Project B'},
            ]},
            {'id': 3, 'name': 'Clara', 'projects': [
                {'id': 102, 'name': 'Project B'},
                {'id': 103, 'name': 'Project C'},
            ]},
        ]
        self.m_hubstaff.get_activities_list.return_value = [
            # Alice: A: 45min, B: 45min, C: 60min
            {'user_id': 1, 'project_id': 101, 'tracked': 15 * 60},
            {'user_id': 1, 'project_id': 102, 'tracked': 45 * 60},
            {'user_id': 1, 'project_id': 101, 'tracked': 30 * 60},
            {'user_id': 1, 'project_id': 103, 'tracked': 60 * 60},
            # Bob: A: 5min, B: 15min
            {'user_id': 2, 'project_id': 101, 'tracked': 5 * 60},
            {'user_id': 2, 'project_id': 102, 'tracked': 5 * 60},
            {'user_id': 2, 'project_id': 102, 'tracked': 5 * 60},
            {'user_id': 2, 'project_id': 102, 'tracked': 5 * 60},
            # Clara: B: 20min, C: 20min
            {'user_id': 3, 'project_id': 102, 'tracked': 10 * 60},
            {'user_id': 3, 'project_id': 102, 'tracked': 10 * 60},
            {'user_id': 3, 'project_id': 103, 'tracked': 10 * 60},
            {'user_id': 3, 'project_id': 103, 'tracked': 10 * 60},
        ]
        self.alice_spent_time_for_project_a = 45 * 60
        self.alice_spent_time_for_project_b = 45 * 60
        self.alice_spent_time_for_project_c = 60 * 60
        self.bob_spent_time_for_project_a = 5 * 60
        self.bob_spent_time_for_project_b = 15 * 60
        self.clara_spent_time_for_project_b = 20 * 60
        self.clara_spent_time_for_project_c = 20 * 60
        self.addCleanup(patch.stop)

        from rtbot34 import Command

        self.command_class = Command
        self.command = self.command_class(
            config_filename='/tmp/.rtbot34rc',
            hubstaff_app_token='A' * 43,
            hubstaff_auth_token='B' * 43,
            hubstaff_username='test@hubstaff.com',
            hubstaff_password='test123456',
            report_filename='/tmp/.rtbot34.html',
            report_date='2001-02-03',
            report_days_ago=3
        )
        self.command._config.config_filename = '/tmp/.rtbot34rc'
        self.command._config.hubstaff_app_token = 'A' * 43
        self.command._config.hubstaff_auth_token = 'B' * 43
        self.command._config.hubstaff_username = 'test@hubstaff.com'
        self.command._config.hubstaff_password = 'test123456'
        self.command._config.report_filename = '/tmp/.rtbot34.html'
        self.command._config.report_date = datetime.date(2001, 2, 3)
        self.command._config.report_days_ago = 3
        self.command._config.report_date_from = datetime.date(2001, 2, 3)
        self.command._config.report_date_to = datetime.date(2001, 2, 4)
        self.command._hubstaff = self.m_hubstaff

    def test_constructor_creates_logger(self):
        self.assertIsInstance(self.command._logger, logging.Logger)
        self.assertEqual(self.command._logger.level, logging.WARNING)

    def test_constructor_creates_config(self):
        self.m_config_class.assert_called_once_with(
            config_filename='/tmp/.rtbot34rc',
            hubstaff_app_token='A' * 43,
            hubstaff_auth_token='B' * 43,
            hubstaff_username='test@hubstaff.com',
            hubstaff_password='test123456',
            report_filename='/tmp/.rtbot34.html',
            report_date='2001-02-03',
            report_days_ago=3,
        )
        self.assertEqual(self.command._config, self.m_config)

    def test_load_config_calls_config_load_method(self):
        self.command._load_config()

        self.m_config.load.assert_called_once_with()

    def test_init_client_calls_hubstaff_constructor(self):
        self.command._init_client()

        self.m_hubstaff_class.assert_called_once_with(
            app_token='A' * 43,
            auth_token='B' * 43,
            username='test@hubstaff.com',
            password='test123456',
        )

    def test_init_client_calls_hubstaff_authenticate_method(self):
        self.command._init_client()

        self.m_hubstaff.authenticate.assert_called_once_with()
        self.assertEqual(self.command._config.hubstaff_auth_token, 'Y' * 43)

    def test_save_config_calls_config_save_method(self):
        self.command._save_config()

        self.m_config.save.assert_called_once_with()

    def test_get_report_data_returns_expected_data(self):
        report_data = self.command._get_report_data(
            date_from=datetime.date(2001, 2, 3),
            date_to=datetime.date(2001, 2, 4))

        self.assertDictEqual(report_data, {
            'date_from': datetime.date(2001, 2, 3),
            'date_to': datetime.date(2001, 2, 4),
            'users': {
                1: {'id': 1, 'name': 'Alice'},
                2: {'id': 2, 'name': 'Bob'},
                3: {'id': 3, 'name': 'Clara'},
            },
            'projects': {
                101: {'id': 101, 'name': 'Project A'},
                102: {'id': 102, 'name': 'Project B'},
                103: {'id': 103, 'name': 'Project C'},
            },
            'spent_time': {
                (1, 101): self.alice_spent_time_for_project_a,
                (1, 102): self.alice_spent_time_for_project_b,
                (1, 103): self.alice_spent_time_for_project_c,
                (2, 101): self.bob_spent_time_for_project_a,
                (2, 102): self.bob_spent_time_for_project_b,
                (3, 102): self.clara_spent_time_for_project_b,
                (3, 103): self.clara_spent_time_for_project_c,
            },
        })

    def test_render_report_to_html_returns_html(self):
        html = self.command._render_report_to_html(data={
            'date_from': datetime.date(2001, 2, 3),
            'date_to': datetime.date(2001, 2, 4),
            'users': {
                1: {'id': 1, 'name': 'Alice'},
                2: {'id': 2, 'name': 'Bob'},
                3: {'id': 3, 'name': 'Clara'},
            },
            'projects': {
                101: {'id': 101, 'name': 'Project A'},
                102: {'id': 102, 'name': 'Project B'},
                103: {'id': 103, 'name': 'Project C'},
            },
            'spent_time': {
                (1, 101): self.alice_spent_time_for_project_a,
                (1, 102): self.alice_spent_time_for_project_b,
                (1, 103): self.alice_spent_time_for_project_c,
                (2, 101): self.bob_spent_time_for_project_a,
                (2, 102): self.bob_spent_time_for_project_b,
                (3, 102): self.clara_spent_time_for_project_b,
                (3, 103): self.clara_spent_time_for_project_c,
            },
        })

        self.assertEqual(html, '''<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>rt-bot-34 report 2001-02-03 - 2001-02-04</title>
  </head>
  <body>
    <h1>2001-02-03 - 2001-02-04</h1>
    <table>
      <thead>
        <tr>
          <th>&nbsp;</th>
        
          <th>Alice</th>
        
          <th>Bob</th>
        
          <th>Clara</th>
        
        </tr>
      </thead>
      <tbody>
      
        <tr>
          <td>Project A</td>
        
          <td>2700</td>
        
          <td>300</td>
        
          <td>0</td>
        
        </tr>
      
        <tr>
          <td>Project B</td>
        
          <td>2700</td>
        
          <td>900</td>
        
          <td>1200</td>
        
        </tr>
      
        <tr>
          <td>Project C</td>
        
          <td>3600</td>
        
          <td>0</td>
        
          <td>1200</td>
        
        </tr>
      
      </tbody>
    </table>
  </body>
</html>''')

    def test_handle_saves_report(self):
        self.command.handle()

        with open('/tmp/.rtbot34.html', 'r') as f:
            html = f.read()

        self.assertEqual(html, '''<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>rt-bot-34 report 2001-02-03 - 2001-02-04</title>
  </head>
  <body>
    <h1>2001-02-03 - 2001-02-04</h1>
    <table>
      <thead>
        <tr>
          <th>&nbsp;</th>
        
          <th>Alice</th>
        
          <th>Bob</th>
        
          <th>Clara</th>
        
        </tr>
      </thead>
      <tbody>
      
        <tr>
          <td>Project A</td>
        
          <td>2700</td>
        
          <td>300</td>
        
          <td>0</td>
        
        </tr>
      
        <tr>
          <td>Project B</td>
        
          <td>2700</td>
        
          <td>900</td>
        
          <td>1200</td>
        
        </tr>
      
        <tr>
          <td>Project C</td>
        
          <td>3600</td>
        
          <td>0</td>
        
          <td>1200</td>
        
        </tr>
      
      </tbody>
    </table>
  </body>
</html>''')


if __name__ == '__main__':
    unittest.main()
