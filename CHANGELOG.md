# Change Log

## 1.2.2
### Added
- `actions/host_get_hostgroups` - Gets/Checks the hostgroups that a given Zabbix host is in

## 1.2.1
### Added
- `actions/workflows/host_get_active_triggers` - Added parameter, 'priority', which allows active triggers to be filtered by severity (priority) level

## 1.2.0
### Added
- `actions/workflows/host_get_active_triggers` - Gets active triggers for a given Zabbix host

## 1.1.0

### Added
- `actions/host_get_alerts` - Gets alerts for a given Zabbix host
- `actions/host_get_events` - Gets events for a given Zabbix host
- `actions/host_get_triggers` - Gets triggers for a given Zabbix host

## 1.0.0

- Drop python 2.7 support.

## 0.4.0

### Added
- `actions/host_get_interfaces.yaml` - Gets the interfaces of one or more Zabbix Hosts

### Updated
- `actions/update_host.yaml` - Added some of the default host properties from the following link to allow them to be changed as well
  https://www.zabbix.com/documentation/5.0/manual/api/reference/host/object

## 0.3.2

- Extend `list_hosts` action to allow specifying a list of groupids (not possible in `filter`), as well as `output` to allow trimming of returned data.

## 0.3.1

### Added

- Explicitly specify supported Python versions

### Changed

- Fixups for Python 3

## 0.3.0

### Added

- `actions/call_api.py` - A primitive pimplemenetation of `python-script` to send a request to specified API endpoint with other specified parameters.
- `actions/list_host_groups.yaml` - List all host_groups objects which are registered in Zabbix
- `actions/list_host_interfaces.yaml` - List all hostinterfaces objects which are registered in Zabbix
- `actions/list_hosts.yaml` - List all host objects which are registered in Zabbix
- `actions/list_templates.yaml` - List all templates objects which are registered in Zabbix
- `actions/update_host.yaml` - A primitive action to update host information

## 0.2.0

### Added

- `actions/create_host.yaml` - register a new host object to zabbix server.

## 0.1.11

### Changes

- `triggers/event_handler.yaml` - `alert_message` type updated to include `array`, `object`
  with logic in `st2_dispatch.py` to handle the difference.
- `st2_dispatch.py` flags: `--st2-api-url` and `--st2-auth-url` no longer have default values.
  See code comments for details.

### Additions

- API Keys can now be used to authenticate to the ST2 API. Please see the 'Advanced Usage'
  section in the readme for more details.
- `--api-key` flag can be passed to `st2_dispatch.py` to test usage with an API Key for authentication
- `st2_dispatch.py` can now send to a user defined trigger, but defaults to `zabbix.event_handler`
- The value of `alert_message` passed in from the Zabbix macro `{ALERT.MESSAGE}` will now be evaluated
  to determine if its a JSON valid List or Dict, or a string, and passed accordingly.
- When using a JSON Dict to pass auth parameters, keys and values passed are parsed as is into options
  that can then be used in later logic.
  This means you can pass any valid option as a key:val pair (`st2_userid`, `st2_passwd`, `trigger`, etc)
  - This excludes `alert_sendto`, `alert_subject`, `alert_message` as they are parsed after the JSON Dict

### Fixes

- Corrected a bug in `ack_event.yaml` where `enum:` was applied with `type: boolean`. Fixes #32
- `host_get_multiple_ids` - `type:` is now `array` (was `string`). Fixes #22

## 0.1.10

- The script that registers st2's configuration to Zabbix would be compatible with Zabbix v4.0.
- An integration test for `register_st2_config_to_zabbix.py` with different version of Zabbix was added.
- A configuration file of docker-compose was added for running integration test in local machine.

## 0.1.9

- Version bump to fix tagging issue. No code change

## 0.1.8

### Added

- New Action: `host_get_inventory` - Get the inventory of one or more Zabbix Hosts

## 0.1.7

### Changed

- Changed MediaType parameter of StackStorm to access through the API endpoints instead of accessing
  directly to each service processes.
- Changed `st2_dispatch.py` to conform to be able to communicate with up to date st2api (v2.8).

  **Note:** This change is backward incompatible -- the interface of `st2_dispatch.py` is changed from
  `--st2-host` to `--st2-api-url` and `--st2-auth-url` to be able to dispach trigger through proxy.
  To update from previous version to this, you should execute `register_st2_config_to_zabbix.py` command.
  This resets configuration of Zabbix for conforming to the interface of current `st2_dispatch.py`
  to dispatch `zabbix.event_handler`.

### Fixed

- Fixed typos in README and ported images from persoanl repository of a contributor
- Fixed to be able to overwrite Zabbix configuration for StackStorm by `register_st2_config_to_zabbix.py`


## 0.1.6

- Fixed typo in `tools/scripts/st2_dispatch.py`.
  Contributed by Nick Maludy (Encore Technologies)

## 0.1.5

- Added a new action `host_get_multiple_ids` that can retrieve 0, a single, or multiple zabbix hosts and
  return those as an array. This is for a race condition that exists when using several zabbix proxies.
- Added a new action `host_delete_by_id` that allows a host to be deleted given the Host's ID instead of
  the Host's Name
  Contributed by Brad Bishop (Encore Technologies)

## 0.1.4

- Added a new action `host_get_status` that retrieves the status of a host in Zabbix.
  Contributed by Brad Bishop (Encore Technologies)

## 0.1.3

- Added a new action `test_credentials` that tests if the credentials in the config are valid.
  Contributed by Nick Maludy (Encore Technologies)

## 0.1.2

- Added base action class with common code. Removed duplicate code from other actions
- Added host_get_id action action to return the id of a Zabbix Host
- Added host_update_status action to change the status of a Zabbix Host
- Added host_delete action to delete a Zabbix Host
- Added maintenance_create_or_update action to create a maintenance window or update one if it already exists
- Added maintenance_delete action to delete a maintenance window

Contributed by Brad Bishop (Encore Technologies)

## 0.1.1

- Set a secret option to the password property in the config.schema.yaml

## 0.1.0

- Initial release
