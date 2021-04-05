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


class HostGetInventory(ZabbixBaseAction):

    def run(self, host_ids=None):
        """ Gets the inventory of one or more Zabbix Hosts.
        """
        self.connect()

        # Find inventory by host ids
        try:
            inventory = self.client.host.get(
                hostids=host_ids, selectInventory='extend', output=['hostid', 'inventory'])
        except ZabbixAPIException as e:
            raise ZabbixAPIException(("There was a problem searching for the host: "
                                      "{0}".format(e)))

        return inventory
