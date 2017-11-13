import mock
import yaml

from st2tests.base import BaseActionTestCase
from event_action_runner import EventActionRunner

from urllib2 import URLError
from pyzabbix.api import ZabbixAPIException


class EventActionTestCase(BaseActionTestCase):
    __test__ = True
    action_cls = EventActionRunner

    def setUp(self):
        super(EventActionTestCase, self).setUp()

        self.full_config = yaml.safe_load(self.get_fixture_content('full.yaml'))

    def test_run_action_without_configuration(self):
        action = self.get_action_instance({})

        self.assertRaises(ValueError, action.run(action='something'))

    @mock.patch('lib.actions.ZabbixAPI')
    def test_run_action_with_invalid_config_of_endpoint(self, mock_client):
        # make an exception that means failure to connect server.
        mock_client.side_effect = URLError('connection error')

        action = self.get_action_instance(self.full_config)

        self.assertRaises(URLError, action.run(action='something'))

    @mock.patch('lib.actions.ZabbixAPI')
    def test_run_action_with_invalid_config_of_account(self, mock_client):
        # make an exception that means failure to authenticate with Zabbix-server.
        mock_client.side_effect = ZabbixAPIException('auth error')

        action = self.get_action_instance(self.full_config)

        self.assertRaises(ZabbixAPIException, action.run(action='something'))

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
