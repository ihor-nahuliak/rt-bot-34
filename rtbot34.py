import os
import argparse
import configparser
from datetime import datetime, timedelta

from hubstaff.client_v1 import HubstaffClient


class HubstaffConfig:
    hubstaff_section = 'hubstaff'
    app_token = None
    auth_token = None
    username = None
    password = None
    report_section = 'report'
    report_date = None

    def __init__(self, filename):
        self._filename = filename
        self._config = configparser.ConfigParser()

    def read(self):
        self._config.read_file(self._filename)
        hubstaff_section = self._config.get(self.hubstaff_section, {})
        if not self.app_token:
            self.app_token = hubstaff_section('app_token')
        if not self.auth_token:
            self.auth_token = hubstaff_section.get('auth_token')
        if not self.username:
            self.username = hubstaff_section.get('username')
        if not self.password:
            self.password = hubstaff_section.get('password')

    def write(self):
        self._config[self.hubstaff_section] = {
            'app_token': self.app_token,
            'auth_token': self.auth_token,
            'username': self.username,
            'password': self.password,
        }
        with open(self._filename, 'w') as f:
            self._config.write(f)


class ReportConfig:
    report_section = 'report'
    date_format = '%Y-%m-%d'
    date_from = None
    date_to = None
    delta_days = None
    html_filename = None
    manager_email = None

    def __init__(self, filename):
        self._filename = filename
        self._config = configparser.ConfigParser()

    def read(self):
        self._config.read_file(self._filename)
        report_section = self._config.get(self.report_section, {})
        if not self.delta_days:
            self.delta_days = int(report_section.get('delta_days', 1))
        if not self.date_from:
            if report_section.get('date_from'):
                self.date_from = datetime.strptime(
                    report_section.get('date_from'), self.date_format)
            else:
                self.date_to = datetime.now().replace(
                    hour=0, minute=0, second=0, microsecond=0)
                self.date_from = self.date_to - timedelta(days=self.delta_days)
        if not self.html_filename:
            self.html_filename = report_section.get('html_filename')
        if not self.manager_email:
            self.manager_email = report_section.get('manager_email')

    def write(self):
        self._config[self.report_section] = {
            'date_from': self.date_from.strftime('%Y-%m-%d'),
            'delta_days': self.delta_days,
            'html_filename': self.html_filename,
            'manager_email': self.manager_email,
        }
        with open(self._filename, 'w') as f:
            self._config.write(f)


class HubstaffRepo:
    def __init__(self, app_token, auth_token=None,
                 username=None, password=None):
        self._client = HubstaffClient(app_token=app_token,
                                      auth_token=auth_token,
                                      username=username,
                                      password=password)

    def auth(self):
        auth_token = self._client.authenticate()
        return auth_token

    def get_users_list(self):
        users_list = self._client.get_users_list()
        # todo: convert to list of user entity
        return users_list

    def get_projects_list(self):
        projects_list = self._client.get_projects_list(status='active')
        # todo: convert to list of project entity
        return projects_list

    def get_activities_list(self, from_, to_):
        activities_list = self._client.get_activities_list(from_=from_, to_=to_)
        # todo: convert to list of activity entity
        return activities_list


class ReportRepo:
    def __init__(self, date_from, date_to,
                 html_filename=None,
                 manager_email=None):
        self._date_from = date_from
        self._date_to = date_to
        self._html_filename = html_filename
        self._manager_email = manager_email

    def _get_report_data(self, users_list, projects_list, activities_list):
        # todo: return list of report row entity
        return []

    def _render_html(self, report_data):
        # todo: convert report rows to html table
        return ''

    def _save_to_html_file(self, report_html):
        with open(self._html_filename, 'w+') as f:
            f.write(report_html)

    def _send_by_email(self, report_html):
        # todo: send given html by manager email
        pass

    def build_report(self, users_list, projects_list, activities_list):
        report_data = self._get_report_data(users_list=users_list,
                                            projects_list=projects_list,
                                            activities_list=activities_list)
        report_html = self._render_html(report_data=report_data)
        if self._html_filename:
            self._save_to_html_file(report_html=report_html)
        if self._manager_email:
            self._send_by_email(report_html=report_html)


class Command:
    def __init__(self, config_filename,
                 hubstaff_app_token=None, hubstaff_auth_token=None,
                 hubstaff_username=None, hubstaff_password=None,
                 report_date=None, report_delta=None,
                 html_filename=None, manager_email=None):
        self._hubstaff_config = HubstaffConfig(config_filename)
        self._hubstaff_config.app_token = hubstaff_app_token
        self._hubstaff_config.auth_token = hubstaff_auth_token
        self._hubstaff_config.username = hubstaff_username
        self._hubstaff_config.password = hubstaff_password
        self._hubstaff_repo = None
        self._report_config = ReportConfig(config_filename)
        self._report_config.date = report_date
        self._report_config.delta = report_delta
        self._report_config.html_filename = html_filename
        self._report_config.manager_email = manager_email
        self._report_repo = None

    def _configure_hubstaff(self):
        self._hubstaff_config.read()
        self._hubstaff_repo = HubstaffRepo(
            app_token=self._hubstaff_config.app_token,
            auth_token=self._hubstaff_config.auth_token,
            username=self._hubstaff_config.username,
            password=self._hubstaff_config.password)
        if not self._hubstaff_config.auth_token:
            self._hubstaff_config.auth_token = self._hubstaff_repo.auth()
        self._hubstaff_config.write()

    def _configure_report(self):
        self._report_config.read()
        self._report_repo = ReportRepo(
            date_from=self._report_config.date_from,
            date_to=self._report_config.date_to,
            html_filename=self._report_config.html_filename,
            manager_email=self._report_config.manager_email)
        self._report_config.write()

    def _build_report(self):
        users_list = self._hubstaff_repo.get_users_list()
        projects_list = self._hubstaff_repo.get_projects_list()
        activities_list = self._hubstaff_repo.get_activities_list(
            from_=self._report_config.date_from,
            to_=self._report_config.date_to)
        self._report_repo.build_report(
            users_list=users_list,
            projects_list=projects_list,
            activities_list=activities_list)

    def handle(self):
        self._configure_hubstaff()
        self._configure_report()
        self._build_report()
