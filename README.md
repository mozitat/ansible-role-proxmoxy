# Ansible Role: proxmoxy

Configures proxmox 4.x hosts and provisions lxc vm containers. It does this by directly interfacing with the proxmox shell tools on the proxmox host. There is no direct dependency on the proxmox http API or libraries like proxmoxer.

For container management it ships with the proxmox_prov Ansible module. 

Proxmoxy can do:
* Host: configure Proxmox host system
* Templates: LXC Template management/downloading
* Permission: set Proxmox Users/Groups, Permissions and ACL
* Storage: management of storages (currently of type dir|zfspool|nfs)
* Provision: Create and configure LXC Containers with the proxmox_prov Module

## Requirements

None.

## Dependencies

None.

## Installation

### Ansible 2+

Using ansible galaxy:

```bash
ansible-galaxy install mozitat.proxmoxy
```

## Role Variables

All variables are defined in [`defaults/main.yml`](defaults/main.yml). See the Examples section for possible values.

### Host

| Name                                  | Default                    | Type    | Description                             |
| ------------------------------------- | -------------------------- | ------- | --------------------------------------- |
| `proxmoxy_host_modules`               | `{}`                         | dict    | Load extra kernel modules on boot       |
| `proxmoxy_host_tuntap`                | `true`                       | Boolean | Enable tun/tap for lxc ct               |
| `proxmoxy_host_remove_nosubnag`       | `true`                       | Boolean | Remove no-subscription message on login |
| `proxmoxy_host_repo_enterprise`       | `false`                      | Boolean | Disable/enable enterprise repo          |
| `proxmoxy_host_repo_nosubs`           | `true`                       | Boolean | Enable no-subscription repo             |

### Templates

| Name                                  | Default                        | Type    | Description                                                 |
| ------------------------------------- | ------------------------------ | ------- | ----------------------------------------------------------- |
| `proxmoxy_templates_storage`          | `"local"`                      | string  | Which storage to use for template storage                   |
| `proxmoxy_templates_dir`              | `"/var/lib/vz/template/cache"` | string  | The template files directory                                |
| `proxmoxy_templates_default`          | `"centos-7"`                   | string  | Default template used in provisioning                       |
| `proxmoxy_templates_update`           | `false`                        | Boolean | Always update template list with `pveam update`?            |
| `proxmoxy_templates`                  | `[]`                           | list    | Download these templates, can use python regex expressions. |

### Permission

*This module uses the pveum utility. `man pveum`*

| Name                                  | Default                     | Type          | Description                    |
| ------------------------------------- | --------------------------  | ------------- | ------------------------------ |
| `proxmoxy_permission_groups`          | `[{}]`                      | list of dicts | Create these groups            |
| `proxmoxy_permission_users`           | `[{}]`                      | list of dicts | Create users, the uid "user@pam" has to exist on the host |
| `proxmoxy_permission_roles`           | `[{}]`                      | list of dicts | Create roles           |
| `proxmoxy_permission_acls`            | `[{}]`                      | list of dicts | ACL values will be appended to the current value |

### Storage

*Currently cannot detect changes in single storage items, you can choose between set only on creation or always set.*

| Name                                  | Default                     | Type          | Description                    |
| ------------------------------------- | --------------------------  | ------------- | ------------------------------ |
| `proxmoxy_storage`                    | `[{}]`                      | list of dicts | PVE storages to create         |
| `proxmoxy_storage_content`            | `['images', 'rootdir']`     | list          | Default storage content        |
| `proxmoxy_storage_nodes`              | `[]`                        | list          | Default list of nodes for storages, leave empty for all. |
| `proxmoxy_storage_changes`            | `true`                      | Boolean       | Always set storage settings.   |
| `proxmoxy_storage_remove`             | `[]`                        | list          | List of storage items to remove. Items in this list normally should not appear in `proxmoxy_storage` |

### Provision

| Name                                  | Default                    | Type    | Description                    |
| ------------------------------------- | -------------------------- | ------- | ------------------------------ |
| `proxmoxy_provision_secret`           | `true`                     | Boolean | Read/save credentials from secret folder, [debops.secret](https://github.com/debops/ansible-secret) compatible |
| `proxmoxy_provision_containers`       | `[]`                       | list    | List of container configurations |
| `proxmoxy_provision_post_cmds`        | `[]`                       | list    | List of commands to run in new containers, may use double quotes. (but MUST not use single quotes) |


## Example Playbook

TODO Including an example of how to use your role (for instance, with variables passed in as parameters) is always nice for users too:

    - hosts: servers
      roles:
         - { role: username.rolename, x: 42 }

## License

MIT

## Author Information

mozit.eu

<!-- An optional section for the role authors to include contact information, or a website (HTML is not allowed). -->
