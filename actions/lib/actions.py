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

        if "zabbix" in self.config:
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
