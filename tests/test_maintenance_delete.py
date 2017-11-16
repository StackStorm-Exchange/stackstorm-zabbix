import mock

from zabbix_base_action_test_case import ZabbixBaseActionTestCase
from maintenance_delete import MaintenanceDelete

from urllib2 import URLError
from pyzabbix.api import ZabbixAPIException


class MaintenanceDeleteTestCase(ZabbixBaseActionTestCase):
    __test__ = True
    action_cls = MaintenanceDelete

    @mock.patch('lib.actions.ZabbixBaseAction.connect')
    def test_run_connection_error(self, mock_connect):
        action = self.get_action_instance(self.full_config)
        mock_connect.side_effect = URLError('connection error')
        test_dict = {'maintenance_window_name': None, 'maintenance_id': '1'}

        with self.assertRaises(URLError):
            action.run(**test_dict)

    @mock.patch('lib.actions.ZabbixAPI')
    @mock.patch('lib.actions.ZabbixBaseAction.connect')
    def test_run_by_id(self, mock_connect, mock_client):
        action = self.get_action_instance(self.full_config)
        mock_connect.return_vaue = "connect return"
        test_dict = {'maintenance_window_name': None, 'maintenance_id': '1'}
        action.connect = mock_connect
        mock_client.maintenance.delete.return_value = "delete return"
        action.client = mock_client

        result = action.run(**test_dict)
        mock_client.maintenance.delete.assert_called_with(test_dict['maintenance_id'])
        self.assertEqual(result, True)

    @mock.patch('lib.actions.ZabbixAPI')
    @mock.patch('lib.actions.ZabbixBaseAction.connect')
    def test_run_by_name(self, mock_connect, mock_client):
        action = self.get_action_instance(self.full_config)
        mock_connect.return_vaue = "connect return"
        test_dict = {'maintenance_window_name': "test", 'maintenance_id': None}
        maintenance_dict = {'name': "test", 'maintenanceid': 1}
        action.connect = mock_connect
        action.maintenance_get = mock.MagicMock(return_value=[maintenance_dict])
        mock_client.maintenance.delete.return_value = "delete return"
        action.client = mock_client

        result = action.run(**test_dict)
        mock_client.maintenance.delete.assert_called_with(maintenance_dict['maintenanceid'])
        self.assertEqual(result, True)

    @mock.patch('lib.actions.ZabbixAPI')
    @mock.patch('lib.actions.ZabbixBaseAction.connect')
    def test_run_by_name_no_return_error(self, mock_connect, mock_client):
        action = self.get_action_instance(self.full_config)
        mock_connect.return_vaue = "connect return"
        test_dict = {'maintenance_window_name': "test", 'maintenance_id': None}
        action.connect = mock_connect
        action.maintenance_get = mock.MagicMock(return_value=[])
        mock_client.maintenance.delete.return_value = "delete return"
        action.client = mock_client

        with self.assertRaises(ValueError):
            action.run(**test_dict)

    @mock.patch('lib.actions.ZabbixAPI')
    @mock.patch('lib.actions.ZabbixBaseAction.connect')
    def test_run_by_name_to_many_return_error(self, mock_connect, mock_client):
        action = self.get_action_instance(self.full_config)
        mock_connect.return_vaue = "connect return"
        test_dict = {'maintenance_window_name': "test", 'maintenance_id': None}
        maintenance_dict = [{'name': "test", 'maintenanceid': 1},
                            {'name': "test", 'maintenanceid': 2}]
        action.connect = mock_connect
        action.maintenance_get = mock.MagicMock(return_value=maintenance_dict)
        mock_client.maintenance.delete.return_value = "delete return"
        action.client = mock_client

        with self.assertRaises(ValueError):
            action.run(**test_dict)

    @mock.patch('lib.actions.ZabbixAPI')
    @mock.patch('lib.actions.ZabbixBaseAction.connect')
    def test_run_value_error(self, mock_connect, mock_client):
        action = self.get_action_instance(self.full_config)
        mock_connect.return_vaue = "connect return"
        test_dict = {'maintenance_window_name': None, 'maintenance_id': None}
        action.connect = mock_connect
        mock_client.maintenance.delete.return_value = "delete return"
        action.client = mock_client

        with self.assertRaises(ValueError):
            action.run(**test_dict)

    @mock.patch('lib.actions.ZabbixAPI')
    @mock.patch('lib.actions.ZabbixBaseAction.connect')
    def test_run_delete_error(self, mock_connect, mock_client):
        action = self.get_action_instance(self.full_config)
        mock_connect.return_vaue = "connect return"
        test_dict = {'maintenance_window_name': None, 'maintenance_id': '1'}
        action.connect = mock_connect
        mock_client.maintenance.delete.side_effect = ZabbixAPIException('maintenance error')
        mock_client.maintenance.delete.return_value = "delete return"
        action.client = mock_client

        with self.assertRaises(ZabbixAPIException):
            action.run(**test_dict)
