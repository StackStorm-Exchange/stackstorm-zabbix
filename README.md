# Zabbix Integration Pack
This pack provides the capability to handle alerts from Zabbix and actions to it. This pack set configurations of Zabbix to dispatch event to the Trigger `zabbix.event_handler` along with the raises of Zabbix Alert. This describes the internal construction of this pack.

![Internal construction of this pack](./images/internal_construction.png)

# Requirements
The system requirement of this pack is
* Zabbix 3.0+ (We've confirmed to work with v3.0 and v3.2)

# Installation
First of all, you can install this pack as below
```
$ st2 pack install zabbix
```

After that you can set configurations for dispatching StackStorm's Trigger "zabbix.event_handler" to Zabbix by `/opt/stackstorm/packs/zabbix/tools/register_st2_config_to_zabbix.py` command. This is the usage of it.
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
$ /opt/stackstorm/packs/zabbix/tools/register_st2_config_to_zabbix.py -z http://zabbix-host/zabbix -u Admin -p zabbix
```

This will register a new MediaType (`StackStorm`) to dispatch events and add an action (`Dispatching to StackStorm`) which is associated with it.
When you created a new Zabbix-Trigger and link it to the Action, StackStorm would accept the message from Zabbix.

## Zabbix configuration

### MediaType for the StackStorm
After executing the `register_st2_config_to_zabbix.py` command, you can notice that new MediaType `StackStorm` is added on `Media types` page (you can move on by `Administration` > `MediaType`). And you also have to this configuration to send a request for dispatching trigger of StackStorm when Zabbix server detect an alert. Please click the `StackStorm` mediatype.
![](./images/configuration_for_mediatype1.png)

You see following page, and you have to fill out with parameters for your st2 environment (the endpoint URLs of st2-api and st2-auth, and authentication informations).
![](./images/configuration_for_mediatype2.png)

You can specify the additional parameters and you can handle them from the payload of the StackStorm's Trigger(`zabbix.event_handler`).

### Deploy the AlertScript
After installing the zabbix-pack, you have to deploy the script `st2_dispatcher.py` which send events of Zabbix to the StackStorm to the directory which Zabbix MediaType referrs. That's directory is specified by the parameter of `AlertScriptsPath` in the Zabbix configuration file on the node which zabbix was installed.
```
$ grep 'AlertScriptsPath' /etc/zabbix/zabbix_server.conf
### Option: AlertScriptsPath
# AlertScriptsPath=${datadir}/zabbix/alertscripts
AlertScriptsPath=/usr/lib/zabbix/alertscripts
```

This pack requires for you to deploy this `st2_dispatcher.py` in its directory (and setup executional environment if necessary) on the Zabbix installed node. Please set it up depending on your environment as below cases.

#### Case: single node
This is the case that both of StackStorm and Zabbix work on the same node.

<img src="./images/description_alertscript1.png" width="350">

This case is quite simple. All you have to do is copying `st2_dispatcher.py` to the directory which AlertScripts should be located.
```
$ sudo cp /opt/stackstorm/packs/zabbix/tools/scripts/st2_dispatch.py /usr/lib/zabbix/alertscripts/
```

#### Case: multiple nodes
This is the case that both processes work on separate (IP-reachable) nodes.

<img src="./images/description_alertscript2.png" width="350">

In this case, you have to do two things (deploying and making executional environment) to set it up. At first, it requires to copy `st2_dispatcher.py` file which is located in StackStorm's node to the directory of AlertScript in Zabbix node.

```
ubuntu@zabbix-node:~$ scp /opt/stackstorm/packs/zabbix/tools/scripts/st2_dispatch.py ./
ubuntu@zabbix-node:~$ sudo mv st2_dispatch.py /usr/lib/zabbix/alertscripts/
```

Then, you have to setup executional environment for this script. In an ubuntu environment, you can do it as below (If you use some other GNU/Linux distribution, please substitute the proper commands to install Python and PIP which is the package manager of Python).
```
ubuntu@zabbix-node:~$ sudo apt-get install python python-pip
```

After installing Python and PIP, you should install depending packages for this AlertScript by pip command.
```
ubuntu@zabbix-node:~$ sudo pip install st2client
```

It's over for setup. And you can verify whether this alertscript would work well manually as below. Please substibute described parameters with proper ones for your environment.
```
ubuntu@zabbix-node:~$ /usr/lib/zabbix/alertscripts/st2_dispatch.py \
> --st2-userid=st2admin \
> --st2-passwd=passwd \
> --st2-api-url=https://st2-node/api \
> --st2-auth-url=https://st2-node/auth
```

If it goes well, you can verify the Trigger `zabbix.event_handler` was dispatched on the st2-node.
```
ubuntu@st2-node:~$ st2 trigger-instance list -n1
+--------------------------+----------------------+-------------------------------+-----------+
| id                       | trigger              | occurrence_time               | status    |
+--------------------------+----------------------+-------------------------------+-----------+
| 5b8d1be547d0e404bffd99e3 | zabbix.event_handler | Mon, 03 Sep 2018 11:34:24 UTC | processed |
+--------------------------+----------------------+-------------------------------+-----------+
+---------------------------------------------------------------------------------------------+
| Note: Only one triggerinstance is displayed. Use -n/--last flag for more results.           |
+---------------------------------------------------------------------------------------------+
ubuntu@st2-node:~$ st2 trigger-instance get 5b8d1be547d0e404bffd99e3
+-----------------+-----------------------------+
| Property        | Value                       |
+-----------------+-----------------------------+
| id              | 5b8d1be547d0e404bffd99e3    |
| trigger         | zabbix.event_handler        |
| occurrence_time | 2018-09-03T11:32:53.943000Z |
| payload         | {                           |
|                 |     "alert_sendto": "",     |
|                 |     "extra_args": [],       |
|                 |     "alert_message": "",    |
|                 |     "alert_subject": ""     |
|                 | }                           |
| status          | processed                   |
+-----------------+-----------------------------+
```

### Action
You can link arbitrary Trigger (of Zabbix) to the action (`Dispatching to StackStorm`) which is registered by the setup command like this.
![](./images/configuration_for_action1.png)
![](./images/configuration_for_action2.png)

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
| Reference of the Action               | Description |
|:--------------------------------------|:------------|
| zabbix.ack_event                      | Send acknowledgement message for an event to Zabbix and may close it |
| zabbix.host_get_id                    | Get the ID of a Zabbix Host |
| zabbix.host_update_status             | Update the status of a Zabbix Host |
| zabbix.host_delete                    | Delete a Zabbix Host |
| zabbix.maintenance_create_or_update   | Create or update Zabbix Maintenance Window |
| zabbix.maintenance_delete             | Delete Zabbix Maintenance Window |
| zabbix.test_credentials               | Tests if it credentials in the config are valid |
