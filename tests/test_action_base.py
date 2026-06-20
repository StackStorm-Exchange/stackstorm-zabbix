import mock

from zabbix_base_action_test_case import ZabbixBaseActionTestCase
from verify_credentials import VerifyCredentials

from zabbix_utils.exceptions import ProcessingError
from zabbix_utils.exceptions import APIRequestError


class BaseActionTestCase(ZabbixBaseActionTestCase):
    __test__ = True
    action_cls = VerifyCredentials

    def test_run_action_without_configuration(self):
        self.assertRaises(ValueError, self.action_cls, self.blank_config)

    def test_init_with_token_only_config(self):
        action = self.get_action_instance(self.token_config)
        self.assertIsNotNone(action)

    def test_init_missing_auth(self):
        config = {"url": "http://localhost:8080"}
        with self.assertRaises(ValueError):
            self.action_cls(config)

    def test_init_empty_username(self):
        config = {"url": "http://localhost:8080", "username": "", "password": "zabbix"}
        with self.assertRaises(ValueError):
            self.action_cls(config)

    def test_init_empty_password(self):
        config = {"url": "http://localhost:8080", "username": "Admin", "password": ""}
        with self.assertRaises(ValueError):
            self.action_cls(config)

    def test_init_none_credentials(self):
        config = {"url": "http://localhost:8080", "username": None, "password": None}
        with self.assertRaises(ValueError):
            self.action_cls(config)

    @mock.patch("lib.actions.ZabbixAPI")
    def test_connect_with_token(self, mock_zabbix_cls):
        mock_client = mock.Mock()
        mock_zabbix_cls.return_value = mock_client

        action = self.get_action_instance(self.token_config)
        action.connect()

        mock_zabbix_cls.assert_called_with(
            url="http://localhost:8080",
            validate_certs=True,
            timeout=30,
            skip_version_check=False,
        )
        mock_client.login.assert_called_once_with(token="my-test-token-12345")

    @mock.patch("lib.actions.ZabbixAPI")
    def test_connect_with_username_password(self, mock_zabbix_cls):
        mock_client = mock.Mock()
        mock_zabbix_cls.return_value = mock_client

        action = self.get_action_instance(self.full_config)
        action.connect()

        mock_client.login.assert_called_once_with(user="Admin", password="zabbix")

    @mock.patch("lib.actions.ZabbixAPI")
    def test_run_action_with_invalid_config_of_endpoint(self, mock_client):
        mock_client.side_effect = ProcessingError("connection error")

        action = self.get_action_instance(self.full_config)

        with self.assertRaises(ProcessingError):
            action.run()

    @mock.patch("lib.actions.ZabbixAPI")
    def test_run_action_with_invalid_config_of_account(self, mock_client):
        mock_client.side_effect = APIRequestError("auth error")

        action = self.get_action_instance(self.full_config)

        with self.assertRaises(APIRequestError):
            action.run()

    @mock.patch("lib.actions.ZabbixAPI")
    def test_find_host(self, mock_client):
        action = self.get_action_instance(self.full_config)
        test_dict = {"host_name": "test", "hostid": "1"}
        mock_client.host.get.return_value = [test_dict]
        action.client = mock_client

        result = action.find_host(test_dict["host_name"])
        self.assertEqual(result, test_dict["hostid"])

    @mock.patch("lib.actions.ZabbixAPI")
    def test_find_host_no_host(self, mock_client):
        action = self.get_action_instance(self.full_config)
        test_dict = {"host_name": "test", "host_id": "1"}
        mock_client.host.get.return_value = []
        action.client = mock_client

        with self.assertRaises(ValueError):
            action.find_host(test_dict["host_name"])

    @mock.patch("lib.actions.ZabbixAPI")
    def test_find_host_too_many_host(self, mock_client):
        action = self.get_action_instance(self.full_config)
        test_dict = [
            {"host_name": "test", "hostid": "1"},
            {"host_name": "test", "hostid": "2"},
        ]
        mock_client.host.get.return_value = test_dict
        action.client = mock_client

        with self.assertRaises(ValueError):
            action.find_host(test_dict[0]["host_name"])

    @mock.patch("lib.actions.ZabbixAPI")
    def test_find_host_fail(self, mock_client):
        action = self.get_action_instance(self.full_config)
        test_dict = {"host_name": "test", "hostid": "1"}
        mock_client.host.get.side_effect = APIRequestError("host error")
        mock_client.host.get.return_value = [test_dict]
        action.client = mock_client

        with self.assertRaises(APIRequestError):
            action.find_host(test_dict["host_name"])

    @mock.patch("lib.actions.ZabbixAPI")
    def test_maintenance_get(self, mock_client):
        action = self.get_action_instance(self.full_config)
        test_dict = {"maintenance_name": "test", "maintenanceid": "1"}
        mock_client.maintenance.get.return_value = [test_dict]
        action.client = mock_client

        result = action.maintenance_get(test_dict["maintenance_name"])
        self.assertEqual(result, [test_dict])

    @mock.patch("lib.actions.ZabbixAPI")
    def test_maintenance_get_fail(self, mock_client):
        action = self.get_action_instance(self.full_config)
        test_dict = {"maintenance_name": "test", "maintenanceid": "1"}
        mock_client.maintenance.get.side_effect = APIRequestError("maintenance error")
        mock_client.maintenance.get.return_value = [test_dict]
        action.client = mock_client

        with self.assertRaises(APIRequestError):
            action.maintenance_get(test_dict["maintenance_name"])

    @mock.patch("lib.actions.ZabbixBaseAction.maintenance_get")
    @mock.patch("lib.actions.ZabbixAPI")
    def test_maintenance_create_or_update_update(
        self, mock_client, mock_maintenance_get
    ):
        action = self.get_action_instance(self.full_config)
        test_dict = {"name": "test"}
        maintenance_dict = {"maintenance_name": "test", "maintenanceid": "1"}
        mock_maintenance_get.return_value = [maintenance_dict]
        mock_client.maintenance.update.return_value = [
            maintenance_dict["maintenanceid"]
        ]
        action.client = mock_client

        result = action.maintenance_create_or_update(test_dict)
        self.assertEqual(result, [maintenance_dict["maintenanceid"]])

    @mock.patch("lib.actions.ZabbixBaseAction.maintenance_get")
    @mock.patch("lib.actions.ZabbixAPI")
    def test_maintenance_create_or_update_update_fail(
        self, mock_client, mock_maintenance_get
    ):
        action = self.get_action_instance(self.full_config)
        test_dict = {"name": "test"}
        maintenance_dict = {"maintenance_name": "test", "maintenanceid": "1"}
        mock_maintenance_get.return_value = [maintenance_dict]
        mock_client.maintenance.update.return_value = [
            maintenance_dict["maintenanceid"]
        ]
        mock_client.maintenance.update.side_effect = APIRequestError(
            "maintenance error"
        )
        action.client = mock_client

        with self.assertRaises(APIRequestError):
            action.maintenance_create_or_update(test_dict)

    @mock.patch("lib.actions.ZabbixBaseAction.maintenance_get")
    @mock.patch("lib.actions.ZabbixAPI")
    def test_maintenance_create_or_update_create(
        self, mock_client, mock_maintenance_get
    ):
        action = self.get_action_instance(self.full_config)
        test_dict = {"name": "test"}
        maintenance_dict = {"maintenance_name": "test", "maintenanceid": "1"}
        mock_maintenance_get.return_value = []
        mock_client.maintenance.create.return_value = [
            maintenance_dict["maintenanceid"]
        ]
        action.client = mock_client

        result = action.maintenance_create_or_update(test_dict)
        self.assertEqual(result, [maintenance_dict["maintenanceid"]])

    @mock.patch("lib.actions.ZabbixBaseAction.maintenance_get")
    @mock.patch("lib.actions.ZabbixAPI")
    def test_maintenance_create_or_update_create_fail(
        self, mock_client, mock_maintenance_get
    ):
        action = self.get_action_instance(self.full_config)
        test_dict = {"name": "test"}
        maintenance_dict = {"maintenance_name": "test", "maintenanceid": "1"}
        mock_maintenance_get.return_value = []
        mock_client.maintenance.create.return_value = [
            maintenance_dict["maintenanceid"]
        ]
        mock_client.maintenance.create.side_effect = APIRequestError(
            "maintenance error"
        )
        action.client = mock_client

        with self.assertRaises(APIRequestError):
            action.maintenance_create_or_update(test_dict)

    @mock.patch("lib.actions.ZabbixBaseAction.maintenance_get")
    @mock.patch("lib.actions.ZabbixAPI")
    def test_maintenance_create_or_update_too_many_maintenance_windows(
        self, mock_client, mock_maintenance_get
    ):
        action = self.get_action_instance(self.full_config)
        test_dict = {"name": "test"}
        maintenance_dict = [
            {"maintenance_name": "test", "maintenanceid": "1"},
            {"maintenance_name": "test", "maintenanceid": "2"},
        ]
        mock_maintenance_get.return_value = maintenance_dict
        mock_client.maintenance.create.return_value = maintenance_dict[0][
            "maintenanceid"
        ]
        action.client = mock_client

        with self.assertRaises(ValueError):
            action.maintenance_create_or_update(test_dict)

    @mock.patch("lib.actions.ZabbixAPI")
    def test_host_get_extended(self, mock_client):
        action = self.get_action_instance(self.full_config)
        mock_client.host.get.return_value = [
            {"hostid": "1", "interfaces": [{"interfaceid": "10"}]}
        ]
        action.client = mock_client

        result = action.host_get_extended(
            "1", "selectInterfaces", ["hostid", "interfaces"]
        )
        self.assertEqual(
            result, [{"hostid": "1", "interfaces": [{"interfaceid": "10"}]}]
        )
        mock_client.host.get.assert_called_with(
            hostids="1", selectInterfaces="extend", output=["hostid", "interfaces"]
        )

    @mock.patch("lib.actions.ZabbixAPI")
    def test_host_get_extended_api_error(self, mock_client):
        action = self.get_action_instance(self.full_config)
        mock_client.host.get.side_effect = APIRequestError("host error")
        action.client = mock_client

        with self.assertRaises(APIRequestError):
            action.host_get_extended("1", "selectInterfaces", ["hostid", "interfaces"])
