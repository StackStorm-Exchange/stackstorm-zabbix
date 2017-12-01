import mock

from zabbix_base_action_test_case import ZabbixBaseActionTestCase
from test_credentials import TestCredentials

from pyzabbix.api import ZabbixAPIException


class TestCredentialsTestCase(ZabbixBaseActionTestCase):
    __test__ = True
    action_cls = TestCredentials

    @mock.patch('lib.actions.ZabbixBaseAction.connect')
    def test_run(self, mock_connect):
        action = self.get_action_instance(self.full_config)
        result = action.run()
        self.assertEqual(result, True)

    @mock.patch('lib.actions.ZabbixBaseAction.connect')
    def test_run_connection_error(self, mock_connect):
        action = self.get_action_instance(self.full_config)
        mock_connect.side_effect = ZabbixAPIException('login error')
        with self.assertRaises(ZabbixAPIException):
            action.run()
