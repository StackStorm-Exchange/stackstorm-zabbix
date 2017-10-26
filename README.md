# Zabbix Integration Pack
This pack provides the capability to handle alerts from Zabbix and actions to it. This pack set configurations of Zabbix to dispatch event to the Trigger `zabbix.event_handler` along with the raises of Zabbix Alert. This describes the internal construction of this pack.

![Internal construction of this pack](https://raw.githubusercontent.com/userlocalhost/st2-zabbix/images_for_README/images/internal_construction.png)

# Requirements
The system requirement of this pack is
* Zabbix 3.0+ (We've confirmed to work with v3.0 and v3.2)

# Installation
First of all, you can install this pack as below
```
$ st2 pack install zabbix
```

After that you can set configurations for dispatching StackStorm's Trigger "zabbix.event_handler" to Zabbix by `/opt/stackstorm/pack/zabbix/tools/register_st2_config_to_zabbix.py` command. This is the usage of it.
```
Usage: register_st2_config_to_zabbix.py [options]

Options:
  -h, --help            show this help message and exit
  -z Z_URL, --zabbix-url=Z_URL
                        The URL of Zabbix Server
  -u Z_USERID, --username=Z_USERID
                        Login username to login Zabbix Server
  -p Z_PASSWD, --password=Z_PASSWD
                        Password which is associated with the username
  -s Z_SENDTO, --sendto=Z_SENDTO
                        Address, user name or other identifier of the
                        recipient
```

And here is an example to execute it.
```
$ source /opt/stackstorm/virtualenvs/zabbix/bin/activate
$ /opt/stackstorm/pack/zabbix/tools/register_st2_config_to_zabbix.py -z http://zabbix-host/zabbix -u Admin -p zabbix
```

This will register a new MediaType (`StackStorm`) to dispatch events and add an action (`Dispatching to StackStorm`) which is associated with it.
When you created a new Zabbix-Trigger and link it to the Action, StackStorm would accept the message from Zabbix.

## Zabbix configuration

### MediaType for the StackStorm
After adding the configurations to the Zabbix, you need to modify the parameters that specify the Hostname (or IP address) of StackStorm node and username and password to auehtnticate with StackStorm from the Zabbix-portal. You can do it by accessing the page of `Administration` > `MediaType`.
![](https://raw.githubusercontent.com/userlocalhost/st2-zabbix/images_for_README/images/configuration_for_mediatype1.png)
![](https://raw.githubusercontent.com/userlocalhost/st2-zabbix/images_for_README/images/configuration_fro_mediatype2.png)

You can specify the additional parameters and you can handle them from the payload of the StackStorm's Trigger(`zabbix.event_handler`).

## Deploy the AlertScript
After installing the zabbix-pack, you have to deploy the script `st2_dispatcher.py` which send events of Zabbix to the StackStorm to the directory which Zabbix MediaType referrs. That's directory is specified by the parameter of `AlertScriptsPath` in the Zabbix configuration file as below.
```
$ grep 'AlertScriptsPath' /etc/zabbix/zabbix_server.conf
### Option: AlertScriptsPath
# AlertScriptsPath=${datadir}/zabbix/alertscripts
AlertScriptsPath=/usr/lib/zabbix/alertscripts
```
Please copy the dispatcher script (`st2_dispatch.py`) to it.
```
$ sudo cp /opt/stackstorm/pack/zabbix/tools/scripts/st2_dispatch.py /usr/lib/zabbix/alertscripts/
```

### Action
You can link arbitrary Trigger (of Zabbix) to the action (`Dispatching to StackStorm`) which is registered by the setup command like this.
![](https://raw.githubusercontent.com/userlocalhost/st2-zabbix/images_for_README/images/configuration_for_action1.png)
![](https://raw.githubusercontent.com/userlocalhost/st2-zabbix/images_for_README/images/configuration_for_action2.png)

By this setting, Zabbix will dispatch event to StackStorm when the registered trigger makes an alert.

# Triggers

## zabbix.event_handler
This trigger is defined to have following parameters.

| Parameter     | Description of context |
|:--------------|:-----------------------|
| alert_sendto  | describe value from user media configuration of Zabbix |
| alert_subject | describe status and name of Zabbix Trigger which raises an alert |
| alert_message | describe detail of alert (see following) |
| extra_args    | describe optional user-defined values (default is `[]`) |

In the `alert_message` parameter, these context is contained as the json format (but the parameter value is string because of the functional restriction of Zabbix). You can parse it in an action to be passed these parameter.

| Parameter of `alert_message` | Description of context |
|:-----------------------------|:-----------------------|
| ['event']['id']              | Numeric ID of the event that triggered an action of Zabbix |
| ['event']['time']            | Time of the event that triggered an action of Zabbix |
| ['trigger']['id']            | Numeric trigger ID which triggered this action of Zabbix |
| ['trigger']['name']          | Name of the trigger of Zabbix |
| ['trigger']['status']        | Current trigger value of Zabbix. Can be either PROBLEM or OK |
| ['items'][0~9]               | `Array` type value to have following `Dict` type informations, and the length of it is fixed to 10 by Zabbix |
| ['items'][0~9]['name']       | Name of trigger setting which alert raises |
| ['items'][0~9]['host']       | Hstname which alert raises |
| ['items'][0~9]['key']        | Key name to retrieve value |
| ['items'][0~9]['value']      | Value which make alert raises |

(These configuration values are corresponding to [the Macros of Zabbix](https://www.zabbix.com/documentation/3.2/manual/appendix/macros/supported_by_location))

# Configuration of StackStorm
You need to set configuration when you run following Action. These are the configuration parameters.

| Configuration Param | Description | Default |
|:--------------------|:------------|:--------|
| url                 | Zabbix login URL | http://localhost/zabbix |
| username            | Login usernmae | Admin |
| password            | Password of `username` | zabbix |

# Action
| Reference of the Action | Description |
|:------------------------|:------------|
| zabbix.ack_event        | Send acknowledgement message for an event to Zabbix and may close it |
