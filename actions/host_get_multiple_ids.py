from pyzabbix.api import ZabbixAPIException
from urllib2 import URLError
from zabbix.api import ZabbixAPI
from st2common.runners.base_action import Action


class ZabbixGetMultipleHostID(Action):
    def __init__(self, config):
        super(ZabbixGetMultipleHostID, self).__init__(config)
        self.config = config

        if self.config is not None and "zabbix" in self.config:
            if "url" not in self.config['zabbix']:
                raise ValueError("Zabbix url details not in the config.yaml")
            elif "username" not in self.config['zabbix']:
                raise ValueError("Zabbix user details not in the config.yaml")
            elif "password" not in self.config['zabbix']:
                raise ValueError("Zabbix password details not in the config.yaml")
        else:
            raise ValueError("Zabbix details not in the config.yaml")

    def connect(self):
        client = None
        try:
            client = ZabbixAPI(url=self.config['zabbix']['url'],
                               user=self.config['zabbix']['username'],
                               password=self.config['zabbix']['password'])
        except ZabbixAPIException as e:
            raise ZabbixAPIException("Failed to authenticate with Zabbix (%s)" % str(e))
        except URLError as e:
            raise URLError("Failed to connect to Zabbix Server (%s)" % str(e))
        except KeyError:
            raise KeyError("Configuration for Zabbix pack is not set yet")

        return client

    def find_hosts(self, client, host_name):
        try:
            zabbix_hosts = client.host.get(filter={"host": host_name})
        except ZabbixAPIException as e:
            raise ZabbixAPIException(("There was a problem searching for the host: "
                                    "{0}".format(e)))

        zabbit_hosts_return = []
        if len(zabbix_hosts) > 0:
            for host in zabbix_hosts:
                zabbit_hosts_return.append(host['hostid'])

        return zabbit_hosts_return

    def run(self, host=None):
        client = self.connect()

        zabbix_hosts = self.find_hosts(client, host)

        return (True, {'host_ids': zabbix_hosts})
