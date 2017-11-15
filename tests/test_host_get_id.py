import mock

from zabbix_base_action_test_case import ZabbixBaseActionTestCase
from host_get_id import HostGetID

from urllib2 import URLError
from pyzabbix.api import ZabbixAPIException


class HostGetIDTestCase(ZabbixBaseActionTestCase):
    __test__ = True
    action_cls = HostGetID

    @mock.patch('lib.actions.ZabbixBaseAction.find_host')
    @mock.patch('lib.actions.ZabbixBaseAction.connect')
    def test_run_connection_error(self, mock_connect, mock_find_host):
        action = self.get_action_instance(self.full_config)
        mock_connect.side_effect = URLError('connection error')
        test_dict = {'host': "test"}
        host_dict = {'name': "test", 'hostid': '1'}
        mock_find_host.return_vaue = host_dict

        with self.assertRaises(URLError):
            action.run(**test_dict)

    @mock.patch('lib.actions.ZabbixBaseAction.find_host')
    @mock.patch('lib.actions.ZabbixBaseAction.connect')
    def test_run_host_error(self, mock_connect, mock_find_host):
        action = self.get_action_instance(self.full_config)
        mock_connect.return_vaue = "connect return"
        test_dict = {'host': "test"}
        host_dict = {'name': "test", 'hostid': '1'}
        mock_find_host.side_effect = ZabbixAPIException('host error')
        mock_find_host.return_vaue = host_dict
        action.connect = mock_connect
        action.find_host = mock_find_host

        with self.assertRaises(ZabbixAPIException):
            action.run(**test_dict)

    @mock.patch('lib.actions.ZabbixBaseAction.find_host')
    @mock.patch('lib.actions.ZabbixBaseAction.connect')
    def test_run(self, mock_connect, mock_find_host):
        action = self.get_action_instance(self.full_config)
        mock_connect.return_vaue = "connect return"
        test_dict = {'host': "test"}
        host_dict = {'name': "test", 'hostid': '1'}
        mock_find_host.return_vaue = host_dict
        # action.connect = mock_connect
        # action.find_host = mock_find_host

        result = action.run(**test_dict)
        self.assertEqual(result, host_dict['hostid'])
