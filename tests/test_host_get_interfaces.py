import mock

from zabbix_base_action_test_case import ZabbixBaseActionTestCase
from host_get_interfaces import HostGetInterfaces

from six.moves.urllib.error import URLError


class HostGetInterfacesTestCase(ZabbixBaseActionTestCase):
    __test__ = True
    action_cls = HostGetInterfaces

    @mock.patch('lib.actions.ZabbixBaseAction.connect')
    def test_run_connection_error(self, mock_connect):
        action = self.get_action_instance(self.full_config)
        mock_connect.side_effect = URLError('connection error')
        test_dict = {'host_ids': ["12345"]}

        with self.assertRaises(URLError):
            action.run(**test_dict)

    @mock.patch('lib.actions.ZabbixAPI')
    @mock.patch('lib.actions.ZabbixBaseAction.connect')
    def test_run_host_error(self, mock_connect, mock_client):
        action = self.get_action_instance(self.full_config)
        mock_connect.return_vaue = "connect return"
        test_dict = {'host_ids': ["12345"]}
        interfaces_list = [{'hostid': "12345", 'interfaces': {
            'name': "test"}}]
        action.connect = mock_connect
        mock_client.host.get.return_value = interfaces_list
        action.client = mock_client

        result = action.run(**test_dict)
        mock_client.host.get.assert_called_with(
            hostids=test_dict['host_ids'],
            selectInterfaces='extend',
            output=['hostid', 'interfaces'])
        self.assertEqual(result, interfaces_list)

    @mock.patch('lib.actions.ZabbixAPI')
    @mock.patch('lib.actions.ZabbixBaseAction.connect')
    def test_run_none(self, mock_connect, mock_client):
        action = self.get_action_instance(self.full_config)
        mock_connect.return_vaue = "connect return"
        test_dict = {'host_ids': ["12345"]}
        interfaces_list = []
        action.connect = mock_connect
        mock_client.host.get.return_value = interfaces_list
        action.client = mock_client

        result = action.run(**test_dict)
        self.assertEqual(result, [])

    @mock.patch('lib.actions.ZabbixAPI')
    @mock.patch('lib.actions.ZabbixBaseAction.connect')
    def test_run_single(self, mock_connect, mock_client):
        action = self.get_action_instance(self.full_config)
        mock_connect.return_vaue = "connect return"
        test_dict = {'host_ids': ["12345"]}
        interfaces_list = [{'hostid': "12345", 'interfaces': {
            'name': "test"}}]
        action.connect = mock_connect
        mock_client.host.get.return_value = interfaces_list
        action.client = mock_client
        expected_return = [{'hostid': interfaces_list[0][
            'hostid'], 'interfaces': interfaces_list[0]['interfaces']}]

        result = action.run(**test_dict)
        mock_client.host.get.assert_called_with(
            hostids=test_dict['host_ids'],
            selectInterfaces='extend',
            output=['hostid', 'interfaces'])
        self.assertEqual(result, expected_return)

    @mock.patch('lib.actions.ZabbixAPI')
    @mock.patch('lib.actions.ZabbixBaseAction.connect')
    def test_run_multiple(self, mock_connect, mock_client):
        action = self.get_action_instance(self.full_config)
        mock_connect.return_vaue = "connect return"
        test_dict = {'host_ids': ["12345", "98765"]}
        interfaces_list = [{'hostid': "12345", 'interfaces':
                           {'name': "test"}},
                          {'hostid': "98765", 'interfaces':
                           {'name': "test2"}}]
        action.connect = mock_connect
        mock_client.host.get.return_value = interfaces_list
        action.client = mock_client
        expected_return = [{'hostid': interfaces_list[0]['hostid'],
                            'interfaces': interfaces_list[0]['interfaces']},
                           {'hostid': interfaces_list[1]['hostid'],
                            'interfaces': interfaces_list[1]['interfaces']}]

        result = action.run(**test_dict)
        mock_client.host.get.assert_called_with(
            hostids=test_dict['host_ids'],
            selectInterfaces='extend',
            output=['hostid', 'interfaces'])
        self.assertEqual(result, expected_return)
