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

from pyzabbix.api import ZabbixAPIException
from st2common.runners.base_action import Action
from urllib2 import URLError
from zabbix.api import ZabbixAPI


class ZabbixBaseAction(Action):
    def __init__(self, config):
        super(ZabbixBaseAction, self).__init__(config)

        self.config = config
        self.client = None

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
        try:
            self.client = ZabbixAPI(url=self.config['zabbix']['url'],
                                    user=self.config['zabbix']['username'],
                                    password=self.config['zabbix']['password'])
        except ZabbixAPIException as e:
            raise ZabbixAPIException("Failed to authenticate with Zabbix (%s)" % str(e))
        except URLError as e:
            raise URLError("Failed to connect to Zabbix Server (%s)" % str(e))
        except KeyError:
            raise KeyError("Configuration for Zabbix pack is not set yet")

    def reconstruct_args_for_ack_event(self, eventid, message, will_close):
        return {
            'eventids': eventid,
            'message': message,
            'action': 1 if will_close else 0,
        }

    def find_host(self, host_name):
        try:
            zabbix_host = self.client.host.get(filter={"host": host_name})
        except ZabbixAPIException as e:
            raise ZabbixAPIException(("There was a problem searching for the host: "
                                    "{0}".format(e)))

        if len(zabbix_host) == 0:
            raise ValueError("Could not find any hosts named {0}".format(host_name))
        elif len(zabbix_host) >= 2:
            raise ValueError("Multiple hosts found with the name: {0}".format(host_name))

        self.zabbix_host = zabbix_host[0]

        return self.zabbix_host['hostid']

    def maintenance_get(self, maintenance_name):
        try:
            result = self.client.maintenance.get(filter={"name": maintenance_name})
            return result
        except ZabbixAPIException as e:
            raise ZabbixAPIException(("There was a problem searching for the maintenance window: "
                                    "{0}".format(e)))

    def maintenance_create_or_update(self, maintenance_params):
        maintenance_result = self.maintenance_get(maintenance_params['name'])
        if len(maintenance_result) == 0:
            try:
                create_result = self.client.maintenance.create(**maintenance_params)
                return create_result
            except ZabbixAPIException as e:
                raise ZabbixAPIException(("There was a problem creating the "
                                        "maintenance window: {0}".format(e)))
        elif len(maintenance_result) == 1:
            try:
                maintenance_id = maintenance_result[0]['maintenanceid']
                update_result = self.client.maintenance.update(maintenanceid=maintenance_id,
                                                            **maintenance_params)
                return update_result
            except ZabbixAPIException as e:
                raise ZabbixAPIException(("There was a problem updating the "
                                        "maintenance window: {0}".format(e)))
        elif len(maintenance_result) >= 2:
            raise ValueError(("There are multiple maintenance windows with the "
                            "name: {0}").format(maintenance_params['name']))
