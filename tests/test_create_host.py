import mock

from zabbix_base_action_test_case import ZabbixBaseActionTestCase
from create_host import CreateHost


class CreateHostTest(ZabbixBaseActionTestCase):
    __test__ = True
    action_cls = CreateHost

    def setUp(self):
        self._check_data = {}

        def side_effect_update_proxy(*args, **kwargs):
            self._check_data['is_set_proxy'] = True

        def side_effect_create_host(host, groups, interfaces):
            self._check_data['interfaces'] = interfaces

            return {'hostids': ['1234']}

        # initialize mock client
        self._mock_client = mock.Mock()
        self._mock_client.hostgroup.get.return_value = []
        self._mock_client.host.create.side_effect = side_effect_create_host
        self._mock_client.host.get.return_value = []
        self._mock_client.proxy.update.side_effect = side_effect_update_proxy
        self._mock_client.proxy.get.return_value = [{'proxyid': 1234}]

        super(CreateHostTest, self).setUp()

    @mock.patch('lib.actions.ZabbixBaseAction.connect')
    def test_create_host(self, mock_connect):
        def side_effect_connect():
            self._check_data['password_authentication'] = True
        mock_connect.side_effect = side_effect_connect

        # set mock client to AirOne
        action = self.get_action_instance(self.full_config)
        action.client = self._mock_client

        (result, data) = action.run(name='test-host', groups=[], domains=['example.com'])
        self.assertTrue(result)
        self.assertEqual(data, {'hostids': ['1234']})
        self.assertTrue(self._check_data['password_authentication'])
        self.assertFalse('is_set_proxy' in self._check_data)
        self.assertEqual(self._check_data['interfaces'], [{
            'type': 1,
            'main': 1,
            'useip': 0,
            'dns': 'example.com',
            'ip': '',
            'port': '10050'
        }])

        # This tests a case when main_if parameter is set
        action.run(name='test', groups=[], main_if='bar.test', domains=['foo.test', 'bar.test'])

        ifdata = self._check_data['interfaces']
        self.assertEqual(len(ifdata), 2)
        self.assertEqual([x['main'] for x in ifdata if x['dns'] == 'foo.test'], [0])
        self.assertEqual([x['main'] for x in ifdata if x['dns'] == 'bar.test'], [1])

    @mock.patch('create_host.ZabbixAPI')
    @mock.patch('lib.actions.ZabbixBaseAction.connect')
    def test_create_host_with_token_and_proxy(self, mock_connect, mock_client):
        def side_effect():
            self._check_data['password_authentication'] = True
        mock_connect.side_effect = side_effect

        # set mock client to AirOne
        mock_client.return_value = self._mock_client
        action = self.get_action_instance(self.full_config)

        (result, data) = action.run(name='test-host', groups=[], domains=['example.com'],
                                    token='token', proxy_host='proxy')
        self.assertTrue(result)
        self.assertEqual(data, {'hostids': ['1234']})
        self.assertFalse('password_authentication' in self._check_data)
        self.assertTrue(self._check_data['is_set_proxy'])

    @mock.patch('lib.actions.ZabbixBaseAction.connect')
    def test_create_host_without_interface_information(self, mock_connect):
        action = self.get_action_instance(self.full_config)
        action.client = self._mock_client
        (result, data) = action.run(name='test-host', groups=[])

        self.assertFalse(result)
        self.assertEqual(data, 'You have to IP address or domain value at least one.')
