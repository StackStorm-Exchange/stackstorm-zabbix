from lib.actions import ZabbixBaseAction
from zabbix.api import ZabbixAPI


class CallAPI(ZabbixBaseAction):
    def run(self, api_method, token, **params):
        # Initialize client object to connect Zabbix server
        if token:
            self.client = ZabbixAPI(url=self.config['zabbix']['url'])
            self.auth = token
        else:
            self.connect()

        return eval('self.client.%s' % api_method)(**params)
