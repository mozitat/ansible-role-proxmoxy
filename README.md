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

All variables are defined in `defaults/main.yml`.

### Host

| Name                                  | Default                    | Type    | Description                    |
| ------------------------------------- | -------------------------- | ------- | ------------------------------ |
| `proxmoxy_host_modules`               | {}                         | dict    | load kernel modules on boot    |
| `proxmoxy_host_tuntap`                | true                       | Boolean | enable tun/tap for lxc ct      |
| `proxmoxy_host_remove_nosubnag`       | true                       | Boolean | remove no-subscription message |
| `proxmoxy_host_repo_enterprise`       | false                      | Boolean | dis-/enable enterprise repo    |
| `proxmoxy_host_repo_nosubs`           | true                       | Boolean | enable no-subscription repo    |

### Templates

| Name                                  | Default                     | Type    | Description                    |
| ------------------------------------- | --------------------------  | ------- | ------------------------------ |
| `proxmoxy_templates_storage`          | "local"                     | string  | which storage to use           |
| `proxmoxy_templates_dir`              | "/var/lib/vz/template/cache"| string  | template directory             |
| `proxmoxy_templates_default`          | "centos-7"                  | string  | default template used in provisioning |
| `proxmoxy_templates_update`           |  false                      | Boolean | always update template list?   |
| `proxmoxy_templates`                  | []                          | list    | download these templates, python regex possible |

### Permission

| Name                                  | Default                     | Type          | Description                    |
| ------------------------------------- | --------------------------  | ------------- | ------------------------------ |
| `proxmoxy_permission_groups`          | [{}]                        | list of dicts |            |
| `proxmoxy_permission_users`           | [{}]                        | list of dicts |            |
| `proxmoxy_permission_roles`           | [{}]                        | list of dicts |            |
| `proxmoxy_permission_acls`            | [{}]                        | list of dicts |            |

### Storage

| Name                                  | Default                     | Type          | Description                    |
| ------------------------------------- | --------------------------  | ------------- | ------------------------------ |
| `proxmoxy_storage`                    | [{}]                        | list of dicts |            |
| `proxmoxy_storage_content`            | ['images', 'rootdir']       | list          |            |
| `proxmoxy_storage_nodes`              | []                          | list          |            |
| `proxmoxy_storage_changes`            | True                        | Boolean       |            |
| `proxmoxy_storage_remove`             | []                          | list          |            |

## Example Playbook

Including an example of how to use your role (for instance, with variables passed in as parameters) is always nice for users too:

    - hosts: servers
      roles:
         - { role: username.rolename, x: 42 }

## License

MIT

## Author Information

mozit.eu

<!-- An optional section for the role authors to include contact information, or a website (HTML is not allowed). -->
