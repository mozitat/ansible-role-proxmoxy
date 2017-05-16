# Ansible Role: proxmoxy

Configures proxmox 4.x hosts and provisions lxc vm containers. It does this by directly interfacing with the proxmox shell tools on the proxmox host. There is no direct dependency on the proxmox http API or libraries like proxmoxer.

For container management it ships with the [proxmox_prov](library/proxmox_prov.py) Ansible module. 

Proxmoxy is able to:
* Host: configure Proxmox host system
* Templates: LXC Template management/downloading
* Permission: set Proxmox Users/Groups, Permissions and ACL
* Storage: management of storages *(type dir|zfspool|nfs)*
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
| `proxmoxy__host_modules`               | `{}`                         | dict    | Load extra kernel modules on boot       |
| `proxmoxy__host_tuntap`                | `true`                       | Boolean | Enable tun/tap for lxc ct               |
| `proxmoxy__host_remove_nosubnag`       | `true`                       | Boolean | Remove no-subscription message on login |
| `proxmoxy__host_repo_enterprise`       | `false`                      | Boolean | Disable/enable enterprise repo          |
| `proxmoxy__host_repo_nosubs`           | `true`                       | Boolean | Enable no-subscription repo             |

### Templates

*For a list of all templates: `pveam available`*

| Name                                  | Default                        | Type    | Description                                                 |
| ------------------------------------- | ------------------------------ | ------- | ----------------------------------------------------------- |
| `proxmoxy__templates_storage`          | `"local"`                      | string  | Which storage to use for template storage                   |
| `proxmoxy__templates_dir`              | `"/var/lib/vz/template/cache"` | string  | The template files directory                                |
| `proxmoxy__templates_default`          | `"centos-7"`                   | string  | Default template used in provisioning                       |
| `proxmoxy__templates_update`           | `false`                        | Boolean | Always update template list with `pveam update`?            |
| `proxmoxy__templates`                  | `[]`                           | list    | Download these templates, can use python regex expressions. |

### Permission

*This module uses the pveum utility. `man pveum`*

| Name                                  | Default                     | Type          | Description                    |
| ------------------------------------- | --------------------------  | ------------- | ------------------------------ |
| `proxmoxy__permission_groups`          | `[{}]`                      | list of dicts | Create these groups            |
| `proxmoxy__permission_users`           | `[{}]`                      | list of dicts | Create users, the uid "user@pam" has to exist on the host |
| `proxmoxy__permission_roles`           | `[{}]`                      | list of dicts | Create roles           |
| `proxmoxy__permission_acls`            | `[{}]`                      | list of dicts | ACL values will be appended to the current value |

### Storage

*Currently cannot detect changes in single storage items, you can choose between set only on creation or always set.*

| Name                                  | Default                     | Type          | Description                    |
| ------------------------------------- | --------------------------  | ------------- | ------------------------------ |
| `proxmoxy__storage`                    | `[{}]`                      | list of dicts | PVE storages to create         |
| `proxmoxy__storage_content`            | `['images', 'rootdir']`     | list          | Default storage content        |
| `proxmoxy__storage_nodes`              | `[]`                        | list          | Default list of nodes for storages, leave empty for all. |
| `proxmoxy__storage_changes`            | `true`                      | Boolean       | Always set storage settings.   |
| `proxmoxy__storage_remove`             | `[]`                        | list          | List of storage items to remove. Items in this list normally should not appear in `proxmoxy__storage` |

### Provision

| Name                                  | Default                    | Type    | Description                    |
| ------------------------------------- | -------------------------- | ------- | ------------------------------ |
| `proxmoxy__provision_secret`           | `true`                     | Boolean | Read/save credentials from secret folder, [debops.secret](https://github.com/debops/ansible-secret) compatible |
| `proxmoxy__provision_bridge`           | `"vmbr0"`                  | string  | Default bridge definition for netX networks |
| `proxmoxy__provision_containers`       | `[]`                       | list    | List of container configurations |
| `proxmoxy__provision_post_cmds`        | `[]`                       | list    | List of simple commands to run in new containers, may use quotes, but no pipes or redirection. |


## Example Playbook

```yaml
- hosts: all
  vars:
    proxmoxy__host_modules:
      lm-sensors: w83627ehf

    proxmoxy__templates:
    - 'centos-[67]{1}-.*'
    - 'debian-8..-standard'
    - 'ubuntu-16.[0-9]+-standard']

    proxmoxy__permission_groups:
      - name: admins
        comment: 'Admins Group'
      - name: group1
        comment: 'another group'

    proxmoxy__permission_users:
      - name: myuser@pam
        comment: 'Dis my user'
        email: 'myuser@bla.at'
        enable: True,
        expire: 0
        firstname: 'Max'
        groups: 'admins,group1'
        key: ''
        lastname: 'Muster'
        password: Null

    proxmoxy__permission_roles:
      - name: Sys_Power
        privs:
          - 'Sys.PowerMgmt'
          - 'Sys.Console'

    proxmoxy__permission_acls:
      - path: '/'
        roles:
          - 'PVEAuditor'
          - 'PVEDatastoreUser'
          - 'PVEVMAdmin'
          - 'Sys_Power'
        propagate: 1
        groups:
          - 'group1'

    proxmoxy__storage:
      - type: zfspool  # mandatory 'type, id, pool'
        id: storage-zfs
        pool: tank/data
        blocksize: Null
        sparse: 1
        content: ['images', 'rootdir']
        disable: 0
        nodes: ['mynode1']
      - type: dir  # mandatory 'type id path'
        id: storage-dir
        path: /tank/somedir
        maxfiles: 3
        shared: 0
      - type: nfs  # mandatory 'type id server export path'
        id: storage-nfs
        server: 192.168.1.2
        export: /myexport
        path: /mnt/nfs_myexport
        options: 'vers=3,soft'
        maxfiles: 7
        content: ['images', 'rootdir', 'vztmpl', 'backup', 'iso']

    proxmoxy__storage_remove:
    - 'tank-remove'
    - 'andremoveme'

    proxmoxy__provision_containers:
      - vmid: 210
        state: present
        ostemplate: "centos-7.*"
        password: abc1234  # ignored if secret is used
        storage: local-zfs
        hostname: ct210
        memory: 512
        onboot: True
        net0:
          name: eth0
          bridge: vmbr0
          ip: 192.168.1.210/24
          gw: 192.168.1.1

  roles:
    - role: mozitat.proxmoxy
```

## License

MIT

## Author Information

mozit.eu

<!-- An optional section for the role authors to include contact information, or a website (HTML is not allowed). -->
