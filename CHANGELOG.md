# Change Log

## 0.1.5

- Added a new action `host_get_multiple_ids` that can retrieve 0, a single, or multiple zabbix hosts and
  return those as an array. This is for a race condition that exists when using several zabbix proxies.
- Added a new action `host_delete_by_id` that allows a host to be deleted give the Host's ID instead of the
  Host's Name
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
