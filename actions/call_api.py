from lib.actions import ZabbixBaseAction
from zabbix.api import ZabbixAPI

import six


class CallAPI(ZabbixBaseAction):
    def run(self, api_method, token, **params):
        # Initialize client object to connect Zabbix server

        # Python doesn't let you modify the length of a dict or list while iterating
        iterate_params = params.copy()

        # Look for Empty strings and None values, but allow False
        # If None or '', remove it from params.
        for key, value in six.iteritems(iterate_params):
            if key in params and not params[key] and not params[key] is False:
                del params[key]

        if token:
            self.client = ZabbixAPI(url=self.config['zabbix']['url'])
            self.auth = token
        else:
            self.connect()

        return self._call_api_method(self.client, api_method, params)

    def _call_api_method(self, client, api_method, params):
        """
        Most of method of Zabbix API consist of a couple of attributes (e.g. "host.get").
        This method unties each attribute and validate it.
        """
        if '.' in api_method:
            return self._call_api_method(self._get_client_attr(client, api_method.split('.')[0]),
                                         '.'.join(api_method.split('.')[1:]), params)

        # This sends a request to Zabbix server
        return self._get_client_attr(client, api_method)(**params)

    def _get_client_attr(self, parent_object, attribute):
        if not hasattr(parent_object, attribute):
            raise RuntimeError("Zabbix client does not have a '%s' method", attribute)

        return getattr(parent_object, attribute)
