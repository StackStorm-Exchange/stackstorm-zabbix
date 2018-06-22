# Licensed to the StackStorm, Inc ('StackStorm') under one or more
# contributor license agreements.  See the NOTICE file distributed with
# this work for additional information regarding copyright ownership.
# The ASF licenses this file to You under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with
# the License.  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from lib.actions import ZabbixBaseAction
from pyzabbix.api import ZabbixAPIException


class ZabbixGetMultipleHostID(ZabbixBaseAction):
    def find_hosts(self, host_name):
        """ Queries the zabbix api for a host and returns just the
        ids of the hosts as a list. If a host could not be found it
        returns an empty list.
        """
        try:
            zabbix_hosts = self.client.host.get(filter={"host": host_name})
        except ZabbixAPIException as e:
            raise ZabbixAPIException(("There was a problem searching for the host: "
                                    "{0}".format(e)))

        zabbix_hosts_return = []
        if len(zabbix_hosts) > 0:
            for host in zabbix_hosts:
                zabbix_hosts_return.append(host['hostid'])

        return zabbix_hosts_return

    def run(self, host=None):
        """ Gets the IDs of the Zabbix host given the Hostname or FQDN
        of the Zabbix host.
        """
        self.connect()

        zabbix_hosts = self.find_hosts(host)

        return {'host_ids': zabbix_hosts}
