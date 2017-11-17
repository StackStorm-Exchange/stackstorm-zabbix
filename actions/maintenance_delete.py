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


class MaintenanceDelete(ZabbixBaseAction):
    def run(self, maintenance_id=None, maintenance_window_name=None):
        """ Delete a maintenance window base on the given maintenance_window_name
        or a maintenance_id
        """
        self.connect()

        if maintenance_window_name is not None:
            maintenance_result = self.maintenance_get(maintenance_window_name)

            if len(maintenance_result) == 0:
                raise ValueError(("Could not find maintenance windows with name: "
                                "{0}").format(maintenance_window_name))
            elif len(maintenance_result) == 1:
                maintenance_id = maintenance_result[0]['maintenanceid']
            elif len(maintenance_result) >= 2:
                raise ValueError(("There are multiple maintenance windows with the "
                                "name: {0}").format(maintenance_window_name))
        elif maintenance_window_name is None and maintenance_id is None:
            raise ValueError("Must provide either a maintenance_window_name or a maintenance_id")

        try:
            self.client.maintenance.delete(maintenance_id)
        except ZabbixAPIException as e:
            raise ZabbixAPIException(("There was a problem deleting the "
                "maintenance window: {0}").format(e))

        return True
