import mock

from zabbix_base_action_test_case import ZabbixBaseActionTestCase
from host_update_status import HostUpdateStatus

from urllib2 import URLError
from pyzabbix.api import ZabbixAPIException


class HostUpdateStatusTestCase(ZabbixBaseActionTestCase):
    __test__ = True
    action_cls = HostUpdateStatus

    @mock.patch('lib.actions.ZabbixBaseAction.connect')
    def test_run_connection_error(self, mock_connect):
        action = self.get_action_instance(self.full_config)
        mock_connect.side_effect = URLError('connection error')
        test_dict = {'host': "test", 'status': 1}
        host_dict = {'name': "test", 'hostid': '1'}
        mock.MagicMock(return_value=host_dict['hostid'])

        with self.assertRaises(URLError):
            action.run(**test_dict)

    @mock.patch('lib.actions.ZabbixBaseAction.connect')
    def test_run_host_error(self, mock_connect):
        action = self.get_action_instance(self.full_config)
        mock_connect.return_vaue = "connect return"
        test_dict = {'host': "test", 'status': 1}
        host_dict = {'name': "test", 'hostid': '1'}
        action.find_host = mock.MagicMock(return_value=host_dict['hostid'],
            side_effect=ZabbixAPIException('host error'))
        action.connect = mock_connect

        with self.assertRaises(ZabbixAPIException):
            action.run(**test_dict)

    @mock.patch('lib.actions.ZabbixAPI')
    @mock.patch('lib.actions.ZabbixBaseAction.connect')
    def test_run(self, mock_connect, mock_client):
        action = self.get_action_instance(self.full_config)
        mock_connect.return_vaue = "connect return"
        test_dict = {'host': "test", 'status': 1}
        host_dict = {'name': "test", 'hostid': '1'}
        action.connect = mock_connect
        action.find_host = mock.MagicMock(return_value=host_dict['hostid'])
        mock_client.host.update.return_value = "update return"
        action.client = mock_client

        result = action.run(**test_dict)
        mock_client.host.update.assert_called_with(hostid=host_dict['hostid'],
                                                status=test_dict['status'])
        self.assertEqual(result, True)

    @mock.patch('lib.actions.ZabbixAPI')
    @mock.patch('lib.actions.ZabbixBaseAction.connect')
    def test_run_update_error(self, mock_connect, mock_client):
        action = self.get_action_instance(self.full_config)
        mock_connect.return_vaue = "connect return"
        test_dict = {'host': "test", 'status': 1}
        host_dict = {'name': "test", 'hostid': '1'}
        action.connect = mock_connect
        action.find_host = mock.MagicMock(return_value=host_dict['hostid'])
        mock_client.host.update.side_effect = ZabbixAPIException('host error')
        mock_client.host.update.return_value = "update return"
        action.client = mock_client

        with self.assertRaises(ZabbixAPIException):
            action.run(**test_dict)
