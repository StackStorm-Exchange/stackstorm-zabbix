import os
import re
import sys
import mock

from six import StringIO
from unittest import TestCase

from six.moves.urllib.error import URLError
from pyzabbix.api import ZabbixAPIException

sys.path.append(os.path.dirname(os.path.realpath(__file__)) + '/../tools/')
import register_st2_config_to_zabbix


class TestRegisterMediaType(TestCase):
    def setUp(self):
        sys.argv = ['register_st2_config_to_zabbix.py']
        self.io_stdout = StringIO()
        self.io_stderr = StringIO()
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
        self.is_registered_media = False
        self.is_registered_action = False
        self.is_called_delete = False

        def side_effect_media(*args, **kwargs):
            self.is_registered_media = True

        def side_effect_action(*args, **kwargs):
            self.is_registered_action = True

        def side_effect_delete(*args, **kwargs):
            self.is_called_delete = True

        # make mock to get target mediatype
        mock_obj = mock.Mock()
        mock_obj.apiinfo.version.return_value = '3.x'
        mock_obj.mediatype.get.return_value = [{
            'type': register_st2_config_to_zabbix.SCRIPT_MEDIA_TYPE,
            'exec_path': register_st2_config_to_zabbix.ST2_DISPATCHER_SCRIPT,
            'mediatypeid': '1',
        }]

        # make mock to return no action
        mock_obj.action.get.return_value = []
        mock_obj.mediatype.update.return_value = {'mediatypeids': ['1']}
        mock_client.return_value = mock_obj

        mock_obj.user.addmedia.side_effect = side_effect_media
        mock_obj.action.create.side_effect = side_effect_action
        mock_obj.action.delete.side_effect = side_effect_delete

        register_st2_config_to_zabbix.main()
        self.assertTrue(re.match(r"Success to register the configurations",
                                 self.io_stdout.getvalue()))
        self.assertTrue(self.is_registered_media)
        self.assertTrue(self.is_registered_action)
        self.assertFalse(self.is_called_delete)

        # make mock to return action which is alredy registered
        mock_obj.action.get.return_value = [{
            'name': register_st2_config_to_zabbix.ST2_ACTION_NAME,
            'actionid': 1,
        }]

        register_st2_config_to_zabbix.main()
        self.assertTrue(re.match(r"Success to register the configurations",
                                 self.io_stdout.getvalue()))
        self.assertTrue(self.is_registered_media)
        self.assertTrue(self.is_registered_action)
        self.assertTrue(self.is_called_delete)

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
        mock_obj.apiinfo.version.return_value = '3.x'
        mock_obj.mediatype.get.return_value = [
            {'type': register_st2_config_to_zabbix.SCRIPT_MEDIA_TYPE,
             'exec_path': 'other-script.sh'},
            {'type': 0}
        ]
        mock_obj.mediatype.create.return_value = {'mediatypeids': ['1']}
        mock_obj.action.get.return_value = []
        mock_obj.user.addmedia.side_effect = side_effect_media
        mock_obj.action.create.side_effect = side_effect_action
        mock_client.return_value = mock_obj

        register_st2_config_to_zabbix.main()

        self.assertTrue(re.match(r"Success to register the configurations",
                                 self.io_stdout.getvalue()))
        self.assertTrue(self.is_registered_media)
        self.assertTrue(self.is_registered_action)

    def test_register_mediatype_with_different_zabbix_version(self):
        mock_client = mock.Mock()

        def side_effect_addmedia(*args, **kwargs):
            return 'user.addmedia is called'

        def side_effect_userupdate(*args, **kwargs):
            return 'user.update is called'

        # set side_effect of caling user.update and user.addmedia API
        mock_client.user.addmedia.side_effect = side_effect_addmedia
        mock_client.user.update.side_effect = side_effect_userupdate

        # When sending request that changes MediaType to Zabbix3.x, this calls user.addmedia API
        mock_client.apiinfo.version.return_value = '3.x.y'
        ret = register_st2_config_to_zabbix.register_media_to_admin(mock_client, 1, mock.Mock())
        self.assertEqual(ret, 'user.addmedia is called')

        # When sending request that changes MediaType to Zabbix3.x, this calls user.update API
        mock_client.apiinfo.version.return_value = '4.x.y'
        ret = register_st2_config_to_zabbix.register_media_to_admin(mock_client, 1, mock.Mock())
        self.assertEqual(ret, 'user.update is called')
