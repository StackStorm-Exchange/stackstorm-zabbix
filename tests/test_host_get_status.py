import mock

from zabbix_base_action_test_case import ZabbixBaseActionTestCase
from host_get_status import HostGetStatus

from urllib2 import URLError
from pyzabbix.api import ZabbixAPIException


class HostGetStatusTestCase(ZabbixBaseActionTestCase):
    __test__ = True
    action_cls = HostGetStatus

    @mock.patch('lib.actions.ZabbixBaseAction.connect')
    def test_run_connection_error(self, mock_connect):
        action = self.get_action_instance(self.full_config)
        mock_connect.side_effect = URLError('connection error')
        test_dict = {'host': "test"}
        host_dict = {'name': "test", 'hostid': '1'}
        action.find_host = mock.MagicMock(return_value=host_dict['hostid'])

        with self.assertRaises(URLError):
            action.run(**test_dict)

    @mock.patch('lib.actions.ZabbixBaseAction.connect')
    def test_run_host_error(self, mock_connect):
        action = self.get_action_instance(self.full_config)
        mock_connect.return_vaue = "connect return"
        test_dict = {'host': "test"}
        host_dict = {'name': "test", 'hostid': '1'}
        action.find_host = mock.MagicMock(return_value=host_dict['hostid'],
            side_effect=ZabbixAPIException('host error'))
        action.connect = mock_connect
        with self.assertRaises(ZabbixAPIException):
            action.run(**test_dict)

    @mock.patch('lib.actions.ZabbixBaseAction.connect')
    @mock.patch('lib.actions.ZabbixBaseAction.find_host')
    def test_run(self, mock_connect, mock_find_host):
        action = self.get_action_instance(self.full_config)
        mock_connect.return_vaue = "connect return"
        test_dict = {'host': "test"}
        host_dict = {'name': "test", 'hostid': '1', 'status': '0'}
        action.connect = mock_connect
        action.find_host = mock_find_host
        action.zabbix_host = host_dict

        result = action.run(**test_dict)
        self.assertEqual(result, host_dict['status'])
