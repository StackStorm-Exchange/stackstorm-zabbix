import mock

from zabbix_base_action_test_case import ZabbixBaseActionTestCase
from maintenance_create_or_update import MaintenanceCreateOrUpdate

from urllib2 import URLError
from pyzabbix.api import ZabbixAPIException


class MaintenanceCreateOrUpdateTestCase(ZabbixBaseActionTestCase):
    __test__ = True
    action_cls = MaintenanceCreateOrUpdate

    @mock.patch('lib.actions.ZabbixBaseAction.connect')
    def test_run_connection_error(self, mock_connect):
        action = self.get_action_instance(self.full_config)
        mock_connect.side_effect = URLError('connection error')
        test_dict = {'host': "test",
                    'time_type': 0,
                    'maintenance_window_name': "test",
                    'maintenance_type': 0,
                    'start_date': "2017-11-14 10:40",
                    'end_date': "2017-11-14 10:45"}
        host_dict = {'name': "test", 'hostid': '1'}
        mock.MagicMock(return_value=host_dict['hostid'])

        with self.assertRaises(URLError):
            action.run(**test_dict)

    @mock.patch('lib.actions.ZabbixBaseAction.connect')
    def test_run_host_error(self, mock_connect):
        action = self.get_action_instance(self.full_config)
        mock_connect.return_vaue = "connect return"
        test_dict = {'host': "test",
                    'time_type': 0,
                    'maintenance_window_name': "test",
                    'maintenance_type': 0,
                    'start_date': "2017-11-14 10:40",
                    'end_date': "2017-11-14 10:45"}
        host_dict = {'name': "test", 'hostid': '1'}
        action.find_host = mock.MagicMock(return_value=host_dict['hostid'],
            side_effect=ZabbixAPIException('host error'))
        action.connect = mock_connect

        with self.assertRaises(ZabbixAPIException):
            action.run(**test_dict)

    @mock.patch('lib.actions.ZabbixBaseAction.connect')
    def test_run_maintenance_error(self, mock_connect):
        action = self.get_action_instance(self.full_config)
        mock_connect.return_vaue = "connect return"
        test_dict = {'host': "test",
                    'time_type': 0,
                    'maintenance_window_name': "test",
                    'maintenance_type': 0,
                    'start_date': "2017-11-14 10:40",
                    'end_date': "2017-11-14 10:45"}
        host_dict = {'name': "test", 'hostid': '1'}
        maintenance_dict = {'maintenanceids': ['1']}
        action.connect = mock_connect
        action.find_host = mock.MagicMock(return_value=host_dict['hostid'])
        action.maintenance_create_or_update = mock.MagicMock(return_value=maintenance_dict,
            side_effect=ZabbixAPIException('maintenance error'))

        with self.assertRaises(ZabbixAPIException):
            action.run(**test_dict)

    @mock.patch('lib.actions.ZabbixBaseAction.connect')
    def test_run(self, mock_connect):
        action = self.get_action_instance(self.full_config)
        mock_connect.return_vaue = "connect return"
        test_dict = {'host': "test",
                    'time_type': 0,
                    'maintenance_window_name': "test",
                    'maintenance_type': 0,
                    'start_date': "2017-11-14 10:40",
                    'end_date': "2017-11-14 10:45"}
        host_dict = {'name': "test", 'hostid': '1'}
        maintenance_dict = {'maintenanceids': ['1']}
        expected_return = {'maintenance_id': maintenance_dict['maintenanceids'][0]}
        action.connect = mock_connect
        action.find_host = mock.MagicMock(return_value=host_dict['hostid'])
        action.maintenance_create_or_update = mock.MagicMock(return_value=maintenance_dict)

        result = action.run(**test_dict)
        self.assertEqual(result, expected_return)
