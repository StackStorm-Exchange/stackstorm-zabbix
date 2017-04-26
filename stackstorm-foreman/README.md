# Foreman Integration Pack

## Configuration

```yaml
url: https://foreman.domain.tld
username: foo
password: bar
verify_ssl: False
```

## Actions

### Puppet

* `puppet.hosts` - List puppet hosts by environment

### Foreman

* `foreman.hosts` - List Hosts managed by Foreman
* `foreman.power_host` - Change a hosts powerstate
* `foreman.create_host` - Provision a new host

## Examples

### `foreman.create_host`

`st2 run foreman.create_host name=host-1.domain.tld provision_method=image hostconfig=<see below>

#### hostconfig

```
{
    "hostgroup_id": 18,
    "location_id": 4,
    "compute_resource_id": 1,
    "compute_profile_id": 14,
    "image_id": 3,
    "build": true,
    "compute_attributes": {
        "start": "1"
    }
}
```

Retrieve the ids by using `hammer-cli`.
#### payload

```
{
    "ip": "10.0.0.20",
    "ip6": null,
    "environment_id": 334344675,
    "environment_name": "production",
    "last_report": null,
    "mac": "00:11:22:33:44:00",
    "realm_id": null,
    "realm_name": null,
    "sp_mac": "00:11:22:33:44:01",
    "sp_ip": null,
    "sp_name": null,
    "domain_id": 22495316,
    "domain_name": "mydomain.net",
    "architecture_id": 501905019,
    "architecture_name": "x86_64",
    "operatingsystem_id": 1073012828,
    "operatingsystem_name": "RHEL 6.1",
    "subnet_id": null,
    "subnet_name": null,
    "subnet6_id": null,
    "subnet6_name": null,
    "sp_subnet_id": null,
    "ptable_id": 1007981702,
    "ptable_name": "ptable29",
    "medium_id": 980190962,
    "medium_name": "CentOS 5.4",
    "build": false,
    "comment": null,
    "disk": null,
    "installed_at": null,
    "model_id": null,
    "hostgroup_id": null,
    "owner_id": 886836129,
    "owner_type": "User",
    "enabled": true,
    "managed": true,
    "use_image": null,
    "image_file": "",
    "uuid": null,
    "compute_resource_id": 980190962,
    "compute_resource_name": "bigcompute",
    "compute_profile_id": 281110143,
    "compute_profile_name": "4-Networking",
    "capabilities": [
        "build",
        "image"
    ],
    "provision_method": "build",
    "certname": "testhost11.mydomain.net",
    "image_id": null,
    "image_name": null,
    "created_at": "2017-01-13 11:52:30 UTC",
    "updated_at": "2017-01-13 11:52:30 UTC",
    "last_compile": null,
    "global_status": 0,
    "global_status_label": "Warning",
    "organization_id": 447626438,
    "organization_name": "Organization 1",
    "location_id": 255093256,
    "location_name": "Location 1",
    "puppet_status": 0,
    "model_name": null,
    "configuration_status": 0,
    "configuration_status_label": "No reports",
    "build_status": 0,
    "build_status_label": "Installed",
    "name": "testhost11.mydomain.net",
    "id": 2,
    "puppet_proxy_id": 182953976,
    "puppet_proxy_name": "Puppetmaster Proxy",
    "puppet_ca_proxy_id": 182953976,
    "puppet_ca_proxy_name": "Puppetmaster Proxy",
    "puppet_proxy": {
        "name": "Puppetmaster Proxy",
        "id": 182953976,
        "url": "http://else.where:4567"
    },
    "puppet_ca_proxy": {
        "name": "Puppetmaster Proxy",
        "id": 182953976,
        "url": "http://else.where:4567"
    },
    "hostgroup_name": null,
    "hostgroup_title": null,
    "interfaces": [
        {
            "id": 2,
            "name": "testhost11.mydomain.net",
            "ip": "10.0.0.20",
            "mac": "00:11:22:33:44:00",
            "identifier": null,
            "primary": true,
            "provision": true,
            "type": "interface"
        },
        {
            "id": 3,
            "name": null,
            "ip": null,
            "mac": "00:11:22:33:44:01",
            "identifier": null,
            "primary": false,
            "provision": false,
            "type": "bmc"
        }
    ],
        "puppetclasses": [],
        "config_groups": [],
        "all_puppetclasses": [],
        "permissions": {
        "console_hosts": true,
        "build_hosts": true,
        "power_hosts": true,
        "edit_hosts": true,
        "destroy_hosts": true,
        "create_hosts": true,
        "ipmi_boot_hosts": true,
        "view_hosts": true,
        "puppetrun_hosts": true
    }
}
```
Documentation: https://theforeman.org/api/1.14/index.html