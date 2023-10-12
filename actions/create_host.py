from lib.actions import ZabbixBaseAction
from zabbix.api import ZabbixAPI


class CreateHost(ZabbixBaseAction):
    def get_interface_config(self, ipaddr='', domain='', port="10050", is_main=False):
        return {
            "type": 1,
            "main": 1 if is_main else 0,
            "useip": 1 if ipaddr else 0,
            "dns": domain,
            "ip": ipaddr,
            "port": port,
        }

    def get_interface_config_with_domain(self, domains, main_if):
        return [self.get_interface_config(domain=x, is_main=(x == main_if)) for x in domains]

    def get_interface_config_with_ipaddr(self, ipaddrs, main_if):
        return [self.get_interface_config(ipaddrs)]

    def set_proxy_for_host(self, proxy_name, new_hosts):
        for proxy in self.client.proxy.get(filter={'host': proxy_name}):
            current_hosts = [x['hostid'] for x in self.client.host.get(proxyids=[proxy['proxyid']])]

            return self.client.proxy.update(**{
                'proxyid': proxy['proxyid'],
                'hosts': current_hosts + new_hosts,
            })

    def run(self, name, groups, ipaddrs, domains=[], proxy_host=None, token=None, main_if=''):
        # Initialize client object to connect Zabbix server
        if token:
            self.client = ZabbixAPI(url=self.config['zabbix']['url'])
            self.auth = token
        else:
            self.connect()

        # retrieve hostgroup-ids to be set to creating host object
        hostgroups = [x['groupid'] for x in self.client.hostgroup.get(filter={'name': groups})]

        # make interface configurations to be set to creating host object
        interfaces = (self.get_interface_config_with_ipaddr(ipaddrs, main_if) +
                      self.get_interface_config_with_domain(domains, main_if))

        # Zabbix server requires one interface value at least
        if not interfaces:
            return (False, "You have to IP address or domain value at least one.")

        # If there is no main interface, set it for the first one.
        if not any([x['main'] > 0 for x in interfaces]):
            interfaces[0]['main'] = 1

        # register a host object
        new_host = self.client.host.create(**{
            'host': name,
            'groups': [{'groupid': x} for x in hostgroups],
            'interfaces': interfaces,
        })

        # register ZabbixProxy if it is necessary
        if proxy_host:
            self.set_proxy_for_host(proxy_host, new_host['hostids'])

        return (True, new_host)
