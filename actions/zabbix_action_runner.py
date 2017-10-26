from pyzabbix.api import ZabbixAPIException
from st2actions.runners.pythonrunner import Action
from urllib2 import URLError
from zabbix.api import ZabbixAPI


class ZabbixActionRunner(Action):
    def __init__(self, config):
        super(ZabbixActionRunner, self).__init__(config)

        self.config = config

    def login(self):
        return ZabbixAPI(url=self.config['zabbix']['url'],
                         user=self.config['zabbix']['username'],
                         password=self.config['zabbix']['password'])

    def reconstruct_args_for_ack_event(self, eventid, message, will_close):
        return {
            'eventids': eventid,
            'message': message,
            'action': 1 if will_close else 0,
        }

    def run(self, action, *args, **kwargs):
        try:
            client = self.login()
        except ZabbixAPIException as e:
            return (False, "Failed to authenticate with Zabbix (%s)" % str(e))
        except URLError as e:
            return (False, "Failed to connect to Zabbix Server (%s)" % str(e))
        except KeyError:
            return (False, "Configuration for Zabbix pack is not set yet")

        if action == 'event.acknowledge':
            kwargs = self.reconstruct_args_for_ack_event(*args, **kwargs)

        try:
            api_handler = client
            for obj in action.split('.'):
                api_handler = getattr(api_handler, obj)

            return (True, api_handler(*args, **kwargs))
        except AttributeError:
            return (False, "Specified action(%s) is invalid" % action)
