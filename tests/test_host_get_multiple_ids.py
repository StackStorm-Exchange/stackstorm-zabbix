import mock

from zabbix_base_action_test_case import ZabbixBaseActionTestCase
from host_get_multiple_ids import ZabbixGetMultipleHostID

from urllib2 import URLError
from pyzabbix.api import ZabbixAPIException


class GetMultipleHostIDTestCase(ZabbixBaseActionTestCase):
    __test__ = True
    action_cls = ZabbixGetMultipleHostID

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
        action.find_hosts = mock.MagicMock(return_value=host_dict['hostid'],
            side_effect=ZabbixAPIException('host error'))
        action.connect = mock_connect
        with self.assertRaises(ZabbixAPIException):
            action.run(**test_dict)

    @mock.patch('lib.actions.ZabbixBaseAction.connect')
    def test_run_none(self, mock_connect):
        action = self.get_action_instance(self.full_config)
        mock_connect.return_vaue = "connect return"
        test_dict = {'host': "test"}
        action.connect = mock_connect
        action.find_hosts = mock.MagicMock(return_value=[])
        expected_return = {'host_ids': []}

        result = action.run(**test_dict)
        self.assertEqual(result, expected_return)

    @mock.patch('lib.actions.ZabbixBaseAction.connect')
    def test_run_single(self, mock_connect):
        action = self.get_action_instance(self.full_config)
        mock_connect.return_vaue = "connect return"
        test_dict = {'host': "test"}
        host_dict = {'name': "test", 'hostid': '1'}
        action.connect = mock_connect
        action.find_hosts = mock.MagicMock(return_value=[host_dict['hostid']])
        expected_return = {'host_ids': [host_dict['hostid']]}

        result = action.run(**test_dict)
        self.assertEqual(result, expected_return)

    @mock.patch('lib.actions.ZabbixBaseAction.connect')
    def test_run_multiple(self, mock_connect):
        action = self.get_action_instance(self.full_config)
        mock_connect.return_vaue = "connect return"
        test_dict = {'host': "test"}
        host_dict = [{'name': "test", 'hostid': '1'}, {'name': "test", 'hostid': '2'}]
        action.connect = mock_connect
        action.find_hosts = mock.MagicMock(return_value=[host_dict[0]['hostid'],
                                                        host_dict[1]['hostid']])
        expected_return = {'host_ids': [host_dict[0]['hostid'], host_dict[1]['hostid']]}

        result = action.run(**test_dict)
        self.assertEqual(result, expected_return)
