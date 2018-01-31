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


class HostGetStatus(ZabbixBaseAction):
    def run(self, host=None, status=None):
        """ Gets the status of a Zabbix Host.
        """
        self.connect()

        # Find current host and populate self.zabbix_host
        self.find_host(host)

        # Get status from self.zabbix_host
        host_status = self.zabbix_host['status']

        return host_status
