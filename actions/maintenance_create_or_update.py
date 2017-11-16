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

from datetime import datetime
from tzlocal import get_localzone
from lib.actions import ZabbixBaseAction


class MaintenanceCreateOrUpdate(ZabbixBaseAction):
    def run(self,
            host=None,
            time_type=None,
            maintenance_window_name=None,
            maintenance_type=None,
            start_date=None,
            end_date=None):
        """ Creates or updates a Zabbix maintenance window by looking
        for the supplied maintenance_window_name and creating the mainenance window if it
        does not exist or updating the mainenance window if it already exists.
        """
        self.connect()

        host_id = self.find_host(host)

        start_time = None
        end_time = None
        period = None
        if start_date is not None and end_date is not None:
            local_tz = get_localzone()

            start_local = datetime.strptime(start_date, "%Y-%m-%d %H:%M")
            start_local = start_local.replace(tzinfo=local_tz)
            start_time = int(start_local.strftime('%s'))

            end_local = datetime.strptime(end_date, "%Y-%m-%d %H:%M")
            end_local = end_local.replace(tzinfo=local_tz)
            end_time = int(end_local.strftime('%s'))

            period = end_time - start_time
        else:
            raise ValueError("Must supply a start_date and end_date")

        time_period = [{'start_date': start_time,
                        'timeperiod_type': time_type,
                        'period': period}]

        maintenance_params = {
            'hostids': [host_id],
            'name': maintenance_window_name,
            'active_since': start_time,
            'active_till': end_time,
            'maintenance_type': maintenance_type,
            'timeperiods': time_period
        }

        maintenance_result = self.maintenance_create_or_update(maintenance_params)

        return {'maintenance_id': maintenance_result['maintenanceids'][0]}
