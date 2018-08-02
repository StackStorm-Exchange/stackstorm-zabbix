#!/usr/bin/env python
import json
import sys

from optparse import OptionParser
from zabbix.api import ZabbixAPI
from pyzabbix.api import ZabbixAPIException
from urllib2 import URLError

# This constant describes 'script' value of 'type' property in the MediaType,
# which is specified in the Zabbix API specification.
SCRIPT_MEDIA_TYPE = '1'

# This is a constant for the metadata of MediaType to be registered
ST2_DISPATCHER_SCRIPT = 'st2_dispatch.py'
ST2_ACTION_NAME = 'Dispatching to StackStorm'


def get_options():
    parser = OptionParser()

    parser.add_option('-z', '--zabbix-url', dest="z_url",
                      help="The URL of Zabbix Server")
    parser.add_option('-u', '--username', dest="z_userid", default='Admin',
                      help="Login username to login Zabbix Server")
    parser.add_option('-p', '--password', dest="z_passwd", default='zabbix',
                      help="Password which is associated with the username")
    parser.add_option('-s', '--sendto', dest="z_sendto", default='Admin',
                      help="Address, user name or other identifier of the recipient")

    (options, args) = parser.parse_args()

    if not options.z_url:
        parser.error('Zabbix Server URL is not given')

    return (options, args)


def is_already_registered_mediatype(client, options):
    """
    This method checks target MediaType has already been registered, or not.
    """
    for mtype in client.mediatype.get():
        if mtype['type'] == SCRIPT_MEDIA_TYPE and mtype['exec_path'] == ST2_DISPATCHER_SCRIPT:
            return mtype['mediatypeid']


def is_already_registered_action(client, options):
    """
    This method checks target Action has already been registered, or not.
    """
    for action in client.action.get():
        if action['name'] == ST2_ACTION_NAME:
            return action['actionid']


def register_media_type(client, options, mediatype_id=None):
    """
    This method registers a MediaType which dispatches alert to the StackStorm.
    """
    mediatype_args = [
        '-- CHANGE ME : api_url  (e.g. https://st2-node/api/v1)',
        '-- CHANGE ME : auth_url (e.g. https://st2-node/auth/v1)',
        '-- CHANGE ME : login uername of StackStorm --',
        '-- CHANGE ME : login password of StackStorm --',
        '{ALERT.SENDTO}',
        '{ALERT.SUBJECT}',
        '{ALERT.MESSAGE}',
    ]

    # send request to register a new MediaType for StackStorm
    params = {
        'description': 'StackStorm',
        'type': SCRIPT_MEDIA_TYPE,
        'exec_path': ST2_DISPATCHER_SCRIPT,
        'exec_params': "\n".join(mediatype_args) + "\n",
    }
    if mediatype_id:
        params['mediatypeid'] = mediatype_id

        ret = client.mediatype.update(**params)
    else:
        ret = client.mediatype.create(**params)

    return ret['mediatypeids'][0]


def register_action(client, mediatype_id, options, action_id=None):

    if action_id:
        client.action.delete(action_id)

    return client.action.create(**{
        'name': ST2_ACTION_NAME,
        'esc_period': 360,
        'eventsource': 0,  # means event created by a trigger
        'def_shortdata': '{TRIGGER.STATUS}: {TRIGGER.NAME}',
        'def_longdata': json.dumps({
            'event': {
                'id': '{EVENT.ID}',
                'time': '{EVENT.TIME}',
            },
            'trigger': {
                'id': '{TRIGGER.ID}',
                'name': '{TRIGGER.NAME}',
                'status': '{TRIGGER.STATUS}',
            },
            'items': [{
                'name': '{ITEM.NAME%s}' % index,
                'host': '{HOST.NAME%s}' % index,
                'key': '{ITEM.KEY%s}' % index,
                'value': '{ITEM.VALUE%s}' % index
            } for index in range(1, 9)],
        }),
        'operations': [{
            "operationtype": 0,
            "esc_period": 0,
            "esc_step_from": 1,
            "esc_step_to": 1,
            "evaltype": 0,
            "opmessage_usr": [{"userid": "1"}],
            "opmessage": {
                "default_msg": 1,
                "mediatypeid": mediatype_id,
            }
        }]
    })


def register_media_to_admin(client, mediatype_id, options):
    return client.user.addmedia(**{
        "users": [
            {"userid": "1"},
        ],
        "medias": {
            "mediatypeid": mediatype_id,
            "sendto": options.z_sendto,
            "active": "0",
            "severity": "63",
            "period": "1-7,00:00-24:00",
        }
    })


def main():
    (options, _) = get_options()

    try:
        client = ZabbixAPI(url=options.z_url,
                           user=options.z_userid,
                           password=options.z_passwd)
    except URLError as e:
        sys.exit('Failed to connect Zabbix server (%s)' % e)
    except ZabbixAPIException as e:
        sys.exit('Failed to authenticate Zabbix (%s)' % e)

    # get ID of MediaType for StackStorm if it exists, or None.
    mediatype_id = is_already_registered_mediatype(client, options)

    # register a new MediaType or update one which is already registered to dispatch events
    # to the StackStorm
    mediatype_id = register_media_type(client, options, mediatype_id)

    # get ID of Action for StackStorm if it exists, or None.
    action_id = is_already_registered_action(client, options)

    # register a Action which is associated with the registered MediaType
    register_action(client, mediatype_id, options, action_id)

    # register a Media to the Admin user
    register_media_to_admin(client, mediatype_id, options)

    print('Success to register the configurations for StackStorm to the Zabbix Server.')


if __name__ == '__main__':
    main()
