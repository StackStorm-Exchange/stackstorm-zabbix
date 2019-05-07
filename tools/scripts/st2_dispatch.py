#!/usr/bin/env python

from st2client.base import BaseCLIApp

from optparse import OptionParser

import json


class ZabbixDispatcher(BaseCLIApp):

    def __init__(self, options):
        self.options = options

        # make a client object to connect st2api
        self.client = self.get_client(args=options)

        # If no API key was passed, get a token using user/pass
        if not self.options.api_key:
            self.client.token = self._get_auth_token(client=self.client,
                                                     username=options.st2_userid,
                                                     password=options.st2_passwd,
                                                     cache_token=False)

    def dispatch_trigger(self, args):

        # Validate if the Alert message is a valid JSON List or Dict and replace
        # alert_message (string)with an object so that its correctly formatted.
        try:
            json_alert = json.loads(self.options.alert_message)
        except:
            pass
        else:
            setattr(self.options, 'alert_message', json_alert)

        body = {
            'trigger': self.options.trigger,
            'payload': {
                'alert_sendto': self.options.alert_sendto,
                'alert_subject': self.options.alert_subject,
                'alert_message': self.options.alert_message,
                'extra_args': args,
            },
        }

        # API Key is preferred over User/Pass when both are present.
        if self.options.api_key:
            print('ST2 Auth Method: API Key')
            auth_method = 'St2-Api-Key'
            auth_value = self.options.api_key
        else:
            print('ST2 Auth Method: Auth Token')
            auth_method = 'X-Auth-Token'
            auth_value = self.client.token

        # send request to st2api to dispatch trigger of Zabbix
        return self.client.managers['Webhook'].client.post('/webhooks/st2', body, headers={
            'Content-Type': 'application/json', auth_method: auth_value})


def get_options():
    parser = OptionParser()

    # Default values will be overridden by JSON Dict or poitional args.
    # If a default is defined but its not a required opt (API key Vs User/Pass)
    # it can cause issues.
    parser.add_option('--st2-userid', dest="st2_userid", default="st2admin",
                      help="Login username of StackStorm")
    parser.add_option('--st2-passwd', dest="st2_passwd", default="",
                      help="Login password associated with the user")
    parser.add_option('--st2-api-url', dest="api_url",
                      help="Endpoint URL for API")
    parser.add_option('--st2-auth-url', dest="auth_url",
                      help="Endpoint URL for auth")
    parser.add_option('--api-key', dest="api_key",
                      help="ST2 API Key to be used when no user/pass defined")
    parser.add_option('--alert-sendto', dest="alert_sendto", default="",
                      help="'Send to' value from user media configuration of Zabbix")
    parser.add_option('--alert-subject', dest="alert_subject", default="",
                      help="'Default subject' value from action configuration of Zabbix")
    parser.add_option('--alert-message', dest="alert_message", default="",
                      help="'Default message' value from action configuration of Zabbix")
    parser.add_option('--trigger', dest="trigger", default="zabbix.event_handler",
                      help='Set the trigger name that dispatch should send to on St2')
    parser.add_option('--skip-config', dest="skip_config", default=False, action='store_true',
                      help='Do NOT parse and use the CLI config file')
    parser.add_option('--config-file', dest="config_file",
                      help='Path to the CLI config file')

    # Zabbix send argument as one string even though it includes whitespace
    # (like $ st2_dispatch.py "foo bar" "hoge fuga" ...).
    # And we can't specify keyward argument, we can only specify args.
    #
    # So it's hard for us to parse the argument of zabbix mediatype using optparse.
    # Then, I decided to fix the order of the CLI arguemnts.
    #
    # See am_prepare_mediatype_exec_command in alert_manager.c in Zabbix src

    (options, args) = parser.parse_args()

    # Check if the very first positional argument is a valid JSON Dict.
    try:
        param_object = json.loads(args[0])
    except:
        # First arg is not a JSON dict, assuming user/pass configuration
        arg_list = ['api_url', 'auth_url', 'st2_userid', 'st2_passwd',
                    'alert_sendto', 'alert_subject', 'alert_message']
        # Parse remaining positional args based on arg_list
        for index, param in enumerate(arg_list):
            if len(args) > index and args[index]:
                setattr(options, param, args[index])

        return (options, args[len(arg_list):])

    else:
        # First arg is a JSON dict, assuming apikey only
        arg_list = ['alert_sendto', 'alert_subject', 'alert_message']
        # Since arg[0] is a JSON dict and we are handling it specifically,
        #   remove it from the list
        args.pop(0)
        # Assign all key/val in param_object to options
        for k, v in param_object.items():
            setattr(options, k, v)
        # Parse remaining positional args based on arg_list
        for index, param in enumerate(arg_list):
            if len(args) > index and args[index]:
                setattr(options, param, args[index])

        return (options, args[len(arg_list):])


def main():
    # Parse and get arguments
    print('Parsing Options')
    (options, args) = get_options()

    # Instantiate st2 client and prepare data for dispatch to st2
    print('Preparing Dispatcher')
    dispatcher = ZabbixDispatcher(options)

    # Dispatch data to trigger on st2 (default zabbix.event_handler)
    print('Dispatching to ST2')
    dispatcher.dispatch_trigger(args)


if __name__ == '__main__':
    main()
