import os
import sys
import mock
import json
import requests
from optparse import OptionParser

from unittest import TestCase

sys.path.append(os.path.dirname(os.path.realpath(__file__)) + '/../tools/scripts')

import st2_dispatch


class FakeResponse(object):

    def __init__(self, text, status_code, reason, *args):
        self.text = text
        self.status_code = status_code
        self.reason = reason
        if args:
            self.headers = args[0]

    def json(self):
        return json.loads(self.text)

    def raise_for_status(self):
        raise Exception(self.reason)


class TestZabbixDispatcher(TestCase):
    TOKEN = {
        'user': 'st2admin',
        'token': '44583f15945b4095afbf57058535ca64',
        'expiry': '2017-02-12T00:53:09.632783Z',
        'id': '589e607532ed3535707f10eb',
        'metadata': {}
    }

    def setUp(self):
        self.parser = OptionParser()

        self.parser.add_option('--userid', dest='st2_userid')
        self.parser.add_option('--passwd', dest='st2_passwd')
        self.parser.add_option('--api-url', dest='api_url')
        self.parser.add_option('--auth-url', dest='auth_url')
        self.parser.add_option('--alert-sendto', dest="alert_sendto", default="")
        self.parser.add_option('--alert-subject', dest="alert_subject", default="")
        self.parser.add_option('--alert-message', dest="alert_message", default="")
        self.parser.add_option('--skip-config', dest='skip_config', default=True)
        self.parser.add_option('--config-file', dest='config_file')

    @mock.patch.object(
        requests, 'post',
        mock.MagicMock(return_value=FakeResponse(json.dumps(TOKEN), 200, 'OK')))
    def test_dispatch_trigger(self):
        (options, _) = self.parser.parse_args([
            '--userid', 'foo',
            '--passwd', 'bar',
            '--api-url', 'https://localhost/api/v1',
            '--auth-url', 'https://localhost/auth/v1',
        ])

        dispatcher = st2_dispatch.ZabbixDispatcher(options)
        self.assertEqual(dispatcher.client.token, self.TOKEN['token'])

        resp = dispatcher.dispatch_trigger(args=[
            options.api_url,
            options.auth_url,
            options.st2_userid,
            options.st2_passwd,
            'foo', 'bar', 'baz'
        ])
        self.assertEqual(resp.status_code, 200)
