import os
import argparse
import getpass
import configparser

import marshmallow as ma
from marshmallow import validate as vld
# from hubstaff.client_v1 import HubstaffClient


DEFAULT_CONFIG_FILENAME = '~/.rtbot34rc'
DEFAULT_REPORT_FILENAME = '~/rtbot34.html'


def normalize_path(path, default=None):
    path = path or default
    if not path:
        return None
    if path.startswith('~/'):
        path = os.path.join(os.path.expanduser('~'), path[2:])
    elif not path.startswith('/'):
        path = os.path.join(os.path.dirname(__file__), path)
    path = os.path.abspath(path)
    return path


class HubstaffSectionSchema(ma.Schema):
    hubstaff_app_token = ma.fields.String(
        load_from='app_token', dump_to='app_token',
        required=True, validate=vld.Length(min=43, max=43))
    hubstaff_auth_token = ma.fields.String(
        load_from='auth_token', dump_to='auth_token',
        allow_none=True, validate=vld.Length(min=43, max=43))
    hubstaff_username = ma.fields.Email(
        load_from='username', dump_to='username',
        allow_none=True, validate=vld.Length(min=1, max=255))
    hubstaff_password = ma.fields.String(
        load_from='password', dump_to='password',
        allow_none=True, validate=vld.Length(min=1, max=255))

    class Meta:
        ordered = True


class ReportSectionSchema(ma.Schema):
    report_filename = ma.fields.String(
        load_from='html_file', dump_to='html_file',
        required=True, missing=DEFAULT_REPORT_FILENAME,
        validate=vld.Length(min=1, max=255))
    report_date = ma.fields.Date(
        load_from='date', dump_to='date', format='%Y-%m-%d')
    report_days_ago = ma.fields.Integer(
        load_from='days_ago', dump_to='days_ago', as_string=True,
        required=True, missing=1, validate=vld.Range(min=0, max=7))

    class Meta:
        ordered = True

    @ma.post_load(pass_many=False)
    def load_report_filename(self, data):
        data['report_filename'] = normalize_path(data['report_filename'])
        return data


class Config:
    """Config repo class.
    Can read data from file or environment variables (preferred).
    Values set as constructor parameters have the highest priority.
    """
    hubstaff_app_token = None
    hubstaff_auth_token = None
    hubstaff_username = None
    hubstaff_password = None
    report_filename = None
    report_date = None
    report_days_ago = None

    @property
    def sections(self):
        sections = {
            'hubstaff': HubstaffSectionSchema,
            'report': ReportSectionSchema,
        }
        return sections

    def __init__(self, config_filename,
                 hubstaff_app_token=None,
                 hubstaff_auth_token=None,
                 hubstaff_username=None,
                 hubstaff_password=None,
                 report_filename=None,
                 report_date=None,
                 report_days_ago=None,
                 **kwargs):
        self._config = configparser.ConfigParser()
        self.filename = normalize_path(
            config_filename, default=DEFAULT_CONFIG_FILENAME)
        self.hubstaff_app_token = hubstaff_app_token
        self.hubstaff_auth_token = hubstaff_auth_token
        self.hubstaff_username = hubstaff_username
        self.hubstaff_password = hubstaff_password
        self.report_filename = report_filename
        self.report_date = report_date
        self.report_days_ago = report_days_ago

    def load(self):
        try:
            with open(self.filename, 'r') as f:
                try:
                    self._config.read_file(f)
                except configparser.MissingSectionHeaderError:
                    pass  # bad file format
        except IOError:
            pass  # file not found or can't be open
        for section_name, schema_class in self.sections.items():
            try:
                section_data = self._config[section_name]
            except (KeyError, configparser.NoSectionError):
                section_data = {}
            schema = schema_class(strict=True)
            schema_data = {}
            for field_name, field in schema.fields.items():
                value = (
                    getattr(self, field_name) or
                    os.environ.get(field_name.upper()) or
                    section_data.get(field.load_from, '')
                )
                if value != '':
                    schema_data[field.load_from] = value
            loaded_data, _ = schema.load(schema_data)
            for attr_name, value in loaded_data.items():
                setattr(self, attr_name, value)

    def save(self):
        for section_name, schema_class in self.sections.items():
            if section_name not in self._config:
                self._config[section_name] = {}
            schema = schema_class(strict=True)
            dumped_data, _ = schema.dump(self)
            for key, value in dumped_data.items():
                self._config[section_name][key] = value or ''
        with open(self.filename, 'w+') as f:
            self._config.write(f)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Simple hubstaff activity report.')
    parser.add_argument(
        '-c', '--config-file', dest='config_filename', type=str,
        help='Path to the config file. '
             'Default: %s' % DEFAULT_CONFIG_FILENAME)
    parser.add_argument(
        '--app-token', dest='hubstaff_app_token', type=str,
        help='Hubstaff application token. '
             'You can also setup environment variable: HUBSTAFF_APP_TOKEN')
    parser.add_argument(
        '--auth-token', dest='hubstaff_auth_token', type=str,
        help='Hubstaff authentication token. '
             'You can also setup environment variable: HUBSTAFF_AUTH_TOKEN')
    parser.add_argument(
        '--username', dest='hubstaff_username', type=str,
        help='Hubstaff username (email address). '
             'You can also setup environment variable: HUBSTAFF_USERNAME')
    parser.add_argument(
        '--password', dest='hubstaff_password', action='store_true',
        help='Ask hubstaff password. '
             'You can also setup environment variable: HUBSTAFF_PASSWORD')
    parser.add_argument(
        '-html', '--html-file', dest='report_filename', type=str,
        help='Path to the html report export file. '
             'Default: %s' % DEFAULT_REPORT_FILENAME)
    parser.add_argument(
        '-d', '--date', dest='report_date', type=str,
        help='Report date in format: "YYYY-MM-DD". Default: yesterday')
    parser.add_argument(
        '--days-ago', dest='report_days_ago', type=int,
        help='Instead of use previous param --date you can setup '
             'how many days ago from current date the report should be. '
             'Must be in range of: 0..7')
    args = parser.parse_args()

    # input password
    if args.hubstaff_password:
        args.hubstaff_password = getpass.getpass('Password: ')

    # to do steps:
    # * load config
    # * authenticate
    # * save auth_token to the config
    # * build report
    config = Config(**args.__dict__)
    config.load()
    config.save()
