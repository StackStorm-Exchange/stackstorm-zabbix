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

from zabbix_utils import ZabbixAPI
from zabbix_utils.exceptions import APIRequestError, ProcessingError
from st2common.runners.base_action import Action


class ZabbixBaseAction(Action):
    def __init__(self, config):
        super(ZabbixBaseAction, self).__init__(config)

        self.config = config
        self.client = None

        if not self.config:
            raise ValueError("Zabbix details not in the config.yaml")

        if "url" not in self.config:
            raise ValueError("Zabbix url details not in the config.yaml")
        # Require either api_token or username+password
        has_token = bool(self.config.get("api_token"))
        has_user = bool(self.config.get("username") and self.config.get("password"))
        if not has_token and not has_user:
            raise ValueError(
                "Zabbix api_token or username/password "
                "must be set in the config.yaml"
            )

    def connect(self):
        try:
            self.client = ZabbixAPI(
                url=self.config["url"],
                validate_certs=self.config["validate_certs"],
                timeout=self.config["timeout"],
                skip_version_check=self.config["skip_version_check"],
            )
            api_token = self.config.get("api_token")
            if api_token:
                self.client.login(token=api_token)
            else:
                self.client.login(
                    user=self.config["username"], password=self.config["password"]
                )
        except APIRequestError as e:
            raise APIRequestError("Failed to authenticate with Zabbix (%s)" % str(e))
        except ProcessingError as e:
            raise ProcessingError("Failed to connect to Zabbix Server (%s)" % str(e))
        except KeyError:
            raise KeyError("Configuration for Zabbix pack is not set yet")

    def reconstruct_args_for_ack_event(self, eventid, message, will_close):
        return {
            "eventids": eventid,
            "message": message,
            "action": 1 if will_close else 0,
        }

    def find_host(self, host_name):
        try:
            zabbix_host = self.client.host.get(filter={"host": host_name})
        except APIRequestError as e:
            raise APIRequestError(
                ("There was a problem searching for the host: " "{0}".format(e))
            )

        if len(zabbix_host) == 0:
            raise ValueError("Could not find any hosts named {0}".format(host_name))
        elif len(zabbix_host) >= 2:
            raise ValueError(
                "Multiple hosts found with the name: {0}".format(host_name)
            )

        self.zabbix_host = zabbix_host[0]

        return self.zabbix_host["hostid"]

    def host_get_extended(self, host_ids, select_field, output_fields):
        """Retrieve extended host data by IDs with a specified select parameter.

        Args:
            host_ids: Host ID or list of host IDs.
            select_field: The selectX parameter name (e.g. 'selectInterfaces').
            output_fields: List of output field names (e.g. ['hostid', 'interfaces']).

        Returns:
            List of host dicts with the requested extended data.
        """
        try:
            kwargs = {
                "hostids": host_ids,
                select_field: "extend",
                "output": output_fields,
            }
            return self.client.host.get(**kwargs)
        except APIRequestError as e:
            raise APIRequestError(
                "There was a problem searching for the host: {0}".format(e)
            )

    def maintenance_get(self, maintenance_name):
        try:
            result = self.client.maintenance.get(filter={"name": maintenance_name})
            return result
        except APIRequestError as e:
            raise APIRequestError(
                (
                    "There was a problem searching for the maintenance window: "
                    "{0}".format(e)
                )
            )

    def maintenance_create_or_update(self, maintenance_params):
        maintenance_result = self.maintenance_get(maintenance_params["name"])
        if len(maintenance_result) == 0:
            try:
                create_result = self.client.maintenance.create(**maintenance_params)
                return create_result
            except APIRequestError as e:
                raise APIRequestError(
                    (
                        "There was a problem creating the "
                        "maintenance window: {0}".format(e)
                    )
                )
        elif len(maintenance_result) == 1:
            try:
                maintenance_id = maintenance_result[0]["maintenanceid"]
                update_result = self.client.maintenance.update(
                    maintenanceid=maintenance_id, **maintenance_params
                )
                return update_result
            except APIRequestError as e:
                raise APIRequestError(
                    (
                        "There was a problem updating the "
                        "maintenance window: {0}".format(e)
                    )
                )
        elif len(maintenance_result) >= 2:
            raise ValueError(
                ("There are multiple maintenance windows with the " "name: {0}").format(
                    maintenance_params["name"]
                )
            )
