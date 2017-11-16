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


class HostUpdateStatus(ZabbixBaseAction):
    def run(self, host=None, status=None):
        """ Updates the status of a Zabbix Host. Status needs to be
        1 or 0 for the call to succeed.
        """
        self.connect()

        host_id = self.find_host(host)

        try:
            self.client.host.update(hostid=host_id, status=status)
            return True
        except ZabbixAPIException as e:
            raise ZabbixAPIException("There was a problem updating the host: {0}".format(e))
