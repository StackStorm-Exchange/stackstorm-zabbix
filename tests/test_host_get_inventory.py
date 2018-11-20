import mock

from zabbix_base_action_test_case import ZabbixBaseActionTestCase
from host_get_inventory import HostGetInventory

from urllib2 import URLError


class HostGetInventoryTestCase(ZabbixBaseActionTestCase):
    __test__ = True
    action_cls = HostGetInventory

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
        inventory_list = [{'hostid': "12345", 'inventory': {
            'serialno_a': "abcd1234", 'name': "test"}}]
        action.connect = mock_connect
        mock_client.host.get.return_value = inventory_list
        action.client = mock_client

        result = action.run(**test_dict)
        mock_client.host.get.assert_called_with(
            hostids=test_dict['host_ids'],
            selectInventory='extend',
            output=['hostid', 'inventory'])
        self.assertEqual(result, inventory_list)

    @mock.patch('lib.actions.ZabbixAPI')
    @mock.patch('lib.actions.ZabbixBaseAction.connect')
    def test_run_none(self, mock_connect, mock_client):
        action = self.get_action_instance(self.full_config)
        mock_connect.return_vaue = "connect return"
        test_dict = {'host_ids': ["12345"]}
        inventory_list = []
        action.connect = mock_connect
        mock_client.host.get.return_value = inventory_list
        action.client = mock_client

        result = action.run(**test_dict)
        self.assertEqual(result, [])

    @mock.patch('lib.actions.ZabbixAPI')
    @mock.patch('lib.actions.ZabbixBaseAction.connect')
    def test_run_single(self, mock_connect, mock_client):
        action = self.get_action_instance(self.full_config)
        mock_connect.return_vaue = "connect return"
        test_dict = {'host_ids': ["12345"]}
        inventory_list = [{'hostid': "12345", 'inventory': {
            'serialno_a': "abcd1234", 'name': "test"}}]
        action.connect = mock_connect
        mock_client.host.get.return_value = inventory_list
        action.client = mock_client
        expected_return = [{'hostid': inventory_list[0][
            'hostid'], 'inventory': inventory_list[0]['inventory']}]

        result = action.run(**test_dict)
        mock_client.host.get.assert_called_with(
            hostids=test_dict['host_ids'],
            selectInventory='extend',
            output=['hostid', 'inventory'])
        self.assertEqual(result, expected_return)

    @mock.patch('lib.actions.ZabbixAPI')
    @mock.patch('lib.actions.ZabbixBaseAction.connect')
    def test_run_multiple(self, mock_connect, mock_client):
        action = self.get_action_instance(self.full_config)
        mock_connect.return_vaue = "connect return"
        test_dict = {'host_ids': ["12345", "98765"]}
        inventory_list = [{'hostid': "12345", 'inventory':
                           {'serialno_a': "abcd1234", 'name': "test"}},
                          {'hostid': "98765", 'inventory':
                           {'serialno_a': "efgh5678", 'name': "test2"}}]
        action.connect = mock_connect
        mock_client.host.get.return_value = inventory_list
        action.client = mock_client
        expected_return = [{'hostid': inventory_list[0]['hostid'],
                            'inventory': inventory_list[0]['inventory']},
                           {'hostid': inventory_list[1]['hostid'],
                            'inventory': inventory_list[1]['inventory']}]

        result = action.run(**test_dict)
        mock_client.host.get.assert_called_with(
            hostids=test_dict['host_ids'],
            selectInventory='extend',
            output=['hostid', 'inventory'])
        self.assertEqual(result, expected_return)
