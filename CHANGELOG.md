# Change Log

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
