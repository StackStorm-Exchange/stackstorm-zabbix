import mock

from zabbix_base_action_test_case import ZabbixBaseActionTestCase
from call_api import CallAPI


class CallAPITest(ZabbixBaseActionTestCase):
    __test__ = True
    action_cls = CallAPI

    @mock.patch('lib.actions.ZabbixBaseAction.connect')
    def test_run_action_without_token(self, mock_conn):
        action = self.get_action_instance(self.full_config)

        # This is a mock of calling API 'hoge'
        action.client = mock.Mock()
        action.client.hoge.return_value = 'result'

        # This checks that a method which is specified in the api_method parameter would be called
        self.assertEqual(action.run(api_method='hoge', token=None, param='foo'), 'result')

    @mock.patch('call_api.ZabbixAPI')
    def test_run_action_with_token(self, mock_client):
        action = self.get_action_instance(self.full_config)

        # This is a mock of calling API 'hoge' to confirm that
        # specified parameters would be passed correctly.
        def side_effect(*args, **kwargs):
            return (args, kwargs)

        _mock_client = mock.Mock()
        _mock_client.hoge.side_effect = side_effect
        mock_client.return_value = _mock_client

        # This checks that specified parameter and access token would be set expectedly
        result = action.run(api_method='hoge', token='test_token', param='foo')
        self.assertEqual(result, ((), {'param': 'foo'}))
        self.assertEqual(action.auth, 'test_token')

    @mock.patch('lib.actions.ZabbixBaseAction.connect')
    def test_call_hierarchized_method(self, mock_conn):
        action = self.get_action_instance(self.full_config)

        # Initialize client object that only accepts request to 'foo.bar' method.
        action.client = mock.Mock(spec=['foo'])
        action.client.foo = mock.Mock(spec=['bar'])
        action.client.foo.bar.return_value = 'result'

        # Send request with proper parameter
        self.assertEqual(action.run(api_method='foo.bar', token=None, param='hoge'), 'result')

        # Send request with invalid api_method
        with self.assertRaises(RuntimeError):
            action.run(api_method='foo.hoge', token=None, param='hoge')

    @mock.patch('call_api.ZabbixAPI')
    def test_run_action_with_empty_parameters(self, mock_client):
        action = self.get_action_instance(self.full_config)

        # This is a mock of calling API 'hoge' to confirm that
        # params with a value of None (p0) are removed prior to execution
        # Should not remove [ '123', False, {}, [], 0 ]
        def side_effect(*args, **kwargs):
            return (args, kwargs)

        _mock_client = mock.Mock()
        _mock_client.hoge.side_effect = side_effect
        mock_client.return_value = _mock_client

        result = action.run(api_method='hoge', token='test_token',
            **{'p0': None, 'p1': '123', 'p2': False, 'p3': {}, 'p4': [], 'p5': 0})
        self.assertEqual(result, ((),
            {'p1': '123', 'p2': False, 'p3': {}, 'p4': [], 'p5': 0}))
        _mock_client.hoge.assert_called_with(
            **{'p1': '123', 'p2': False, 'p3': {}, 'p4': [], 'p5': 0})
