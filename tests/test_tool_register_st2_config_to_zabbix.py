import os
import re
import sys
import mock

from io import BytesIO
from unittest import TestCase

from urllib2 import URLError
from pyzabbix.api import ZabbixAPIException

sys.path.append(os.path.dirname(os.path.realpath(__file__)) + '/../tools/')
import register_st2_config_to_zabbix


class TestRegisterMediaType(TestCase):
    def setUp(self):
        sys.argv = ['register_st2_config_to_zabbix.py']
        self.io_stdout = BytesIO()
        self.io_stderr = BytesIO()
        sys.stdout = self.io_stdout
        sys.stderr = self.io_stderr

    def tearDown(self):
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__

    def test_register_mediatype_without_argument(self):
        with self.assertRaises(SystemExit):
            register_st2_config_to_zabbix.main()

        self.assertTrue(re.match(r".*Zabbix Server URL is not given",
                                 self.io_stderr.getvalue(),
                                 flags=(re.MULTILINE | re.DOTALL)))

    @mock.patch('register_st2_config_to_zabbix.ZabbixAPI')
    def test_register_mediatype_to_invalid_zabbix_server(self, mock_client):
        sys.argv += ['-z', 'http://invalid-zabbix-host']

        # make an exception that means failure to connect server.
        mock_client.side_effect = URLError('connection error')

        with self.assertRaises(SystemExit):
            register_st2_config_to_zabbix.main()
            self.assertTrue(re.match(r"Failed to connect Zabbix server", self.io_stderr.getvalue()))

    @mock.patch('register_st2_config_to_zabbix.ZabbixAPI')
    def test_register_mediatype_with_invalid_authentication(self, mock_client):
        sys.argv += ['-z', 'http://invalid-zabbix-host', '-u', 'user', '-p', 'passwd']

        # make an exception that means failure to authenticate with Zabbix-server.
        mock_client.side_effect = ZabbixAPIException('auth error')

        with self.assertRaises(SystemExit):
            register_st2_config_to_zabbix.main()
            self.assertTrue(re.match(r"Failed to authenticate Zabbix", self.io_stderr.getvalue()))

    @mock.patch('register_st2_config_to_zabbix.ZabbixAPI')
    def test_register_duplicate_mediatype(self, mock_client):
        sys.argv += ['-z', 'http://zabbix-host']

        # make mock to get target mediatype
        mock_obj = mock.Mock()
        mock_obj.mediatype.get.return_value = [
            {'type': register_st2_config_to_zabbix.SCRIPT_MEDIA_TYPE,
             'exec_path': register_st2_config_to_zabbix.ST2_DISPATCHER_SCRIPT}
        ]
        mock_client.return_value = mock_obj

        with self.assertRaises(SystemExit):
            register_st2_config_to_zabbix.main()
            self.assertTrue(re.match(r"A MediaType for StackStorm has been already registered.",
                                     self.io_stderr.getvalue()))

    @mock.patch('register_st2_config_to_zabbix.ZabbixAPI')
    def test_register_mediatype_successfully(self, mock_client):
        sys.argv += ['-z', 'http://zabbix-host']
        self.is_registered_media = False
        self.is_registered_action = False

        def side_effect_media(*args, **kwargs):
            self.is_registered_media = True

        def side_effect_action(*args, **kwargs):
            self.is_registered_action = True

        mock_obj = mock.Mock()
        mock_obj.mediatype.get.return_value = [
            {'type': register_st2_config_to_zabbix.SCRIPT_MEDIA_TYPE,
             'exec_path': 'other-script.sh'},
            {'type': 0}
        ]
        mock_obj.mediatype.create.return_value = {'mediatypeids': ['1']}
        mock_obj.user.addmedia.side_effect = side_effect_media
        mock_obj.action.create.side_effect = side_effect_action
        mock_client.return_value = mock_obj

        register_st2_config_to_zabbix.main()

        self.assertTrue(re.match(r"Success to register the configurations",
                                 self.io_stdout.getvalue()))
        self.assertTrue(self.is_registered_media)
        self.assertTrue(self.is_registered_action)
