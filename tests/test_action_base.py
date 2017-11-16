import mock

from zabbix_base_action_test_case import ZabbixBaseActionTestCase
from event_action_runner import EventActionRunner

from urllib2 import URLError
from pyzabbix.api import ZabbixAPIException


class EventActionTestCase(ZabbixBaseActionTestCase):
    __test__ = True
    action_cls = EventActionRunner

    def test_run_action_without_configuration(self):
        self.assertRaises(ValueError, self.action_cls, self.blank_config)

    @mock.patch('lib.actions.ZabbixAPI')
    def test_run_action_with_invalid_config_of_endpoint(self, mock_client):
        # make an exception that means failure to connect server.
        mock_client.side_effect = URLError('connection error')

        action = self.get_action_instance(self.full_config)

        with self.assertRaises(URLError):
            action.run(action='something')

    @mock.patch('lib.actions.ZabbixAPI')
    def test_run_action_with_invalid_config_of_account(self, mock_client):
        # make an exception that means failure to authenticate with Zabbix-server.
        mock_client.side_effect = ZabbixAPIException('auth error')

        action = self.get_action_instance(self.full_config)

        with self.assertRaises(ZabbixAPIException):
            action.run(action='something')

    @mock.patch('lib.actions.ZabbixAPI')
    def test_run_action_with_invalid_config_of_action(self, mock_client):
        mock_obj = mock.Mock()
        mock_obj.invalid = []

        mock_client.return_value = mock_obj

        action = self.get_action_instance(self.full_config)
        result = action.run(action='invalid.action')

        self.assertFalse(result[0])
        self.assertEqual(result[1], "Specified action(invalid.action) is invalid")

    @mock.patch('lib.actions.ZabbixAPI')
    def test_run_action_with_valid_config(self, mock_client):
        def mock_double(param):
            return param * 2

        mock_handler = mock.Mock()
        mock_handler.double = mock.Mock(side_effect=mock_double)

        mock_obj = mock.Mock()
        mock_obj.action = mock_handler

        mock_client.return_value = mock_obj

        action = self.get_action_instance(self.full_config)
        result = action.run(action='action.double', param=4)

        self.assertTrue(result[0])
        self.assertEqual(result[1], 8)

    @mock.patch('lib.actions.ZabbixAPI')
    def test_find_host(self, mock_client):
        action = self.get_action_instance(self.full_config)
        test_dict = {'host_name': "test", 'hostid': "1"}
        mock_client.host.get.return_value = [test_dict]
        action.client = mock_client

        result = action.find_host(test_dict['host_name'])
        self.assertEqual(result, test_dict['hostid'])

    @mock.patch('lib.actions.ZabbixAPI')
    def test_find_host_no_host(self, mock_client):
        action = self.get_action_instance(self.full_config)
        test_dict = {'host_name': "test", 'host_id': "1"}
        mock_client.host.get.return_value = []
        action.client = mock_client

        with self.assertRaises(ValueError):
            action.find_host(test_dict['host_name'])

    @mock.patch('lib.actions.ZabbixAPI')
    def test_find_host_too_many_host(self, mock_client):
        action = self.get_action_instance(self.full_config)
        test_dict = [{'host_name': "test", 'hostid': "1"},
                    {'host_name': "test", 'hostid': "2"}]
        mock_client.host.get.return_value = test_dict
        action.client = mock_client

        with self.assertRaises(ValueError):
            action.find_host(test_dict[0]['host_name'])

    @mock.patch('lib.actions.ZabbixAPI')
    def test_find_host_fail(self, mock_client):
        action = self.get_action_instance(self.full_config)
        test_dict = {'host_name': "test", 'hostid': "1"}
        mock_client.host.get.side_effect = ZabbixAPIException('host error')
        mock_client.host.get.return_value = [test_dict]
        action.client = mock_client

        with self.assertRaises(ZabbixAPIException):
            action.find_host(test_dict['host_name'])

    @mock.patch('lib.actions.ZabbixAPI')
    def test_maintenance_get(self, mock_client):
        action = self.get_action_instance(self.full_config)
        test_dict = {'maintenance_name': "test", 'maintenanceid': "1"}
        mock_client.maintenance.get.return_value = [test_dict]
        action.client = mock_client

        result = action.maintenance_get(test_dict['maintenance_name'])
        self.assertEqual(result, [test_dict])

    @mock.patch('lib.actions.ZabbixAPI')
    def test_maintenance_get_fail(self, mock_client):
        action = self.get_action_instance(self.full_config)
        test_dict = {'maintenance_name': "test", 'maintenanceid': "1"}
        mock_client.maintenance.get.side_effect = ZabbixAPIException('maintenance error')
        mock_client.maintenance.get.return_value = [test_dict]
        action.client = mock_client

        with self.assertRaises(ZabbixAPIException):
            action.maintenance_get(test_dict['maintenance_name'])

    @mock.patch('lib.actions.ZabbixBaseAction.maintenance_get')
    @mock.patch('lib.actions.ZabbixAPI')
    def test_maintenance_create_or_update_update(self, mock_client, mock_maintenance_get):
        action = self.get_action_instance(self.full_config)
        test_dict = {'name': "test"}
        maintenance_dict = {'maintenance_name': "test", 'maintenanceid': "1"}
        mock_maintenance_get.return_value = [maintenance_dict]
        mock_client.maintenance.update.return_value = [maintenance_dict['maintenanceid']]
        action.client = mock_client

        result = action.maintenance_create_or_update(test_dict)
        self.assertEqual(result, [maintenance_dict['maintenanceid']])

    @mock.patch('lib.actions.ZabbixBaseAction.maintenance_get')
    @mock.patch('lib.actions.ZabbixAPI')
    def test_maintenance_create_or_update_update_fail(self, mock_client, mock_maintenance_get):
        action = self.get_action_instance(self.full_config)
        test_dict = {'name': "test"}
        maintenance_dict = {'maintenance_name': "test", 'maintenanceid': "1"}
        mock_maintenance_get.return_value = [maintenance_dict]
        mock_client.maintenance.update.return_value = [maintenance_dict['maintenanceid']]
        mock_client.maintenance.update.side_effect = ZabbixAPIException('maintenance error')
        action.client = mock_client

        with self.assertRaises(ZabbixAPIException):
            action.maintenance_create_or_update(test_dict)

    @mock.patch('lib.actions.ZabbixBaseAction.maintenance_get')
    @mock.patch('lib.actions.ZabbixAPI')
    def test_maintenance_create_or_update_create(self, mock_client, mock_maintenance_get):
        action = self.get_action_instance(self.full_config)
        test_dict = {'name': "test"}
        maintenance_dict = {'maintenance_name': "test", 'maintenanceid': "1"}
        mock_maintenance_get.return_value = []
        mock_client.maintenance.create.return_value = [maintenance_dict['maintenanceid']]
        action.client = mock_client

        result = action.maintenance_create_or_update(test_dict)
        self.assertEqual(result, [maintenance_dict['maintenanceid']])

    @mock.patch('lib.actions.ZabbixBaseAction.maintenance_get')
    @mock.patch('lib.actions.ZabbixAPI')
    def test_maintenance_create_or_update_create_fail(self, mock_client, mock_maintenance_get):
        action = self.get_action_instance(self.full_config)
        test_dict = {'name': "test"}
        maintenance_dict = {'maintenance_name': "test", 'maintenanceid': "1"}
        mock_maintenance_get.return_value = []
        mock_client.maintenance.create.return_value = [maintenance_dict['maintenanceid']]
        mock_client.maintenance.create.side_effect = ZabbixAPIException('maintenance error')
        action.client = mock_client

        with self.assertRaises(ZabbixAPIException):
            action.maintenance_create_or_update(test_dict)

    @mock.patch('lib.actions.ZabbixBaseAction.maintenance_get')
    @mock.patch('lib.actions.ZabbixAPI')
    def test_maintenance_create_or_update_too_many_maintenance_windows(self,
                                                                    mock_client,
                                                                    mock_maintenance_get):
        action = self.get_action_instance(self.full_config)
        test_dict = {'name': "test"}
        maintenance_dict = [{'maintenance_name': "test", 'maintenanceid': "1"},
                            {'maintenance_name': "test", 'maintenanceid': "2"}]
        mock_maintenance_get.return_value = maintenance_dict
        mock_client.maintenance.create.return_value = maintenance_dict[0]['maintenanceid']
        action.client = mock_client

        with self.assertRaises(ValueError):
            action.maintenance_create_or_update(test_dict)
