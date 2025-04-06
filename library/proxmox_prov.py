#!/usr/bin/env python3

ANSIBLE_METADATA = {'status': ['preview'],
                    'supported_by': 'community',
                    'version': '0.8'}

DOCUMENTATION = '''
---
module: proxmox_prov
short_description: management of LXC instances on Proxmox VE
description:
  - has no dependencies and directly uses the local pvesh API interface on the host.
  - current status: "works for me"
  - allows you to create/delete/stop LXC instances in Proxmox VE cluster
  - automatically creates container rootfs/mpX volumes via API if inexistent.
  - can resize rootfs/mpX volumes.
  - currently supports only lxc containers.
  - other storage configurations other than ZFS are untested.
  - currently it is only tested on a single PVE host, not part of a cluster.
  - For options reference: https://pve.proxmox.com/wiki/Manual:_pct.conf
version_added: "2.1"
options:
  vmid:
    description:
      - the instance id
      - vm creation: if not set, the next available ID will be fetched from API.
      - if not set, will be fetched from PromoxAPI based on the hostname
    default: null
    required: false
  password:
    description:
      - the instance root password
      - required only for new CTs and C(state=present)
    default: null
    required: false
  hostname:
    description:
      - the instance hostname
      - required only for C(state=present)
      - must be unique if vmid is not passed
    default: null
    required: false
  ostemplate:
    description:
      - the template for VM creation
      - required only for C(state=present)
      - can be a absolute file path, or pvesm format 'local:vztmpl/template.tar.xz '
    default: null
    required: false
  arch:
    description:
      - OS architecture type (default=amd64)
    default: null
    required: false
    choices: ['amd64', 'i386']
  cmode:
    description:
      - Console mode (default=tty)
    default: null
    required: false
    choices: ['console', 'shell', 'tty']
  console:
    description:
      - Attach a console device (/dev/console) to the container. (default=1)
    type: bool
    default: null
    required: false
  cores:
    description:
      - numbers of allocated cores for instance (default=all)
    type: int
    default: null
    required: false
  cpulimit:
    description:
      - limit of cpu usage (default=0)
    type: int
    default: null
    required: false
  cpuunits:
    description:
      - CPU weight for a VM, relative to all other VMs. (default=1024)
      - larger value means more CPU time
    type: int
    default: null
    required: false
  delete:
    description:
      - A list of options that should be unset/deleted from the VM configuration.
    type: list
    default: null
    required: false
  description:
    description:
      - CT description as seen in web interface.
    type: string
    default: null
    required: false
  force:
    description:
      - forcing operations, untested, currently can be used only with C(present)
      - # TBD can be used only with states C(present), C(stopped), C(restarted)
      - # TBD with C(state=present) force option allow to overwrite existing container
      - # TBD with states C(stopped) , C(restarted) allow to force stop instance
    default: false
    required: false
    type: boolean
  lock:
    description:
      - Lock/Unlock the VM.
    type: enum
    default: null
    required: false
    choices: ['migrate', 'backup', 'snapshot', 'rollback']
  memory:
    description:
      - memory size in MB for instance
    default: 512
    required: false
  mp[X]:
    description:
      - X is one of 0...9
      - specifies additional mounts (separate disks) for the container
      - >
        mp[n]: [volume=]<volume> ,mp=<Path> [,acl=<1|0>] [,backup=<1|0>] [,quota=<1|0>]
           [,ro=<1|0>] [,shared=<1|0>] [,size=<DiskSize>(M|G|T)]
      - <1|0> means True/False boolean values
      - For a dir mount use {volume: /mnt/dir, mp: /mountinct, size: 0T}, size must be 0T.
      - For a bind mount use {volume: /mnt/bindmount, mp: /bindmount}.
      - Bind mount is not listed by df inside CT.
    default: null
    required: false
    type:  A hash/dictionary defining mount point properties
  nameserver:
    description:
      - sets nameserver(s) for VM, format: "10.0.0.1 10.0.0.2 10.0.0.3"
    type: string
    default: null
    required: false
  net[X]:
    description:
      - X is one of 0...9
      - specifies one network interface netX for the container
      - >
        net[X]: name=<string> [,bridge=<bridge>] [,firewall=<1|0>] [,gw=<GatewayIPv4>]
          [,gw6=<GatewayIPv6>] [,hwaddr=<XX:XX:XX:XX:XX:XX>] [,ip=<IPv4Format/CIDR>]
          [,ip6=<IPv6Format/CIDR>] [,mtu=<integer>] [,rate=<mbps>] [,tag=<integer>]
          [,trunks=<vlanid[;vlanid...]>] [,type=<veth>]
      - enclose integer values in quotes
      - <1|0> means True/False boolean values
    default: null
    required: false
    type:  A hash/dictionary defining interface properties
  node:
    description:
      - Proxmox VE node, when new VM will be created
      - if not set for C(state=present) uses local node hostname
      - for other states will be autodiscovered
    default: null
    required: false
  onboot:
    description:
      - specifies whether a VM will be started during system bootup (default=false)
    default: null
    required: false
    type: boolean
  ostype:
    description:
      - OS type. This is used to setup configuration inside the container...
    type: enum
    default: null
    required: false
    choices: ['alpine', 'archlinux', 'centos', 'debian', 'fedora', 'gentoo',
              'opensuse', 'ubuntu', 'unmanaged']
  pool:
    description:
      - add VM to Proxmox VE resource pool
      - Applies only to newly created VMs and is ignored for config runs.
    type: str
    default: null
    required: false
  protection:
    description:
      - Sets protection flag of container.
    type: bool
    default: null
    required: false
  rootfs:
    description:
      - the container root filesystem
      - for C(state=present): if not set, a volume will be automatically created.
      - >
        options: [storage=<storage>] [volume=]<volume> [acl=<1|0>] [,quota=<1|0>]
         [,ro=<1|0>] [,shared=<1|0>] [,size=<DiskSize>(M|G|T)]
      - <1|0> means True/False boolean values
      - default: (zfs) volume name= subvol-<vmid>-disk-1, size 4G
      - >
        volume can be defined as {'volume': 'local-zfs:subvol-101-disk-1'} or
         {'storage': '...', 'volume': '...'}
    default: null
    required: false
    type:  A hash/dictionary defining rootfs properties
  searchdomain:
    description:
      - The container DNS search domain (name).
    type: str
    default: null
    required: false
  ssh-public-keys:
    description:
      - On CT create setup ssh public key for root, supports only one key currently.
    type: str
    default: null
    required: false
  startup:
    description:
      - \[order=]\d+ [,up=\d+] [,down=\d+]
      - can also be just a number defining the startup order.
    type: str
    default: null
    required: false
  state:
    description:
     - Indicate desired state of the instance
    choices: ['present', 'absent', 'start', 'stop', 'restart']
    default: present
  storage:
    description:
      - only relevant for new VM creation with C(state=present)
      - target storage if not rootfs defined
    type: string
    default: 'local'
    required: false
  swap:
    description:
      - amount of swap in MB.
    type: int
    default: 512
    required: false
    # default: null  # tbd
  template:
    description:
      - Enable/disable template.
      - does not yet seem to be implemented.
    type: bool
    default: null
    required: false
  timeout:
    description:
      - timeout for shutdown operations, cannot be used in C(state=present).
    default: 60
    required: false
    type: integer
  tty:
    description:
      - The number of tty (0-6) available to the container.
    type: int
    default: null
    required: false
  unprivileged:
    description:
      - Makes the container run as unprivileged user. (Should not be modified manually.)
      - Can only be used on newly created CTs, 
    type: bool
    default: null
    required: false
notes:
  - >
    Uses pvesh command on the host node, meaning the executing (ansible) user
     needs sudo privileges.
  - Or the user has the appropriate permissions set in Proxmox VE. (untested)
requirements: [ "python >= 2.7" ]
author: "mozit.eu"
'''

EXAMPLES = '''
# Create new container with minimal options
- proxmox_prov:
    vmid: 100
    password: 123456
    hostname: example.org
    ostemplate: 'local:vztmpl/centos-7-default_20161207_amd64.tar.xz'
# Create new container with some options and network interface with static ip.
- proxmox_prov:
    vmid: 100
    node: mo03
    password: 123456
    hostname: example.org
    ostemplate: 'local:vztmpl/ubuntu-14.04-x86_64.tar.gz'
    net0:
        name: eth0
        ip: 192.168.0.100/24
        gw: 192.168.0.1
        bridge: vmbr0
# Create new container with some options and network interface with dhcp.
- proxmox_prov:
    vmid: 100
    node: mo03
    password: 123456
    hostname: example.org
    ostemplate: 'local:vztmpl/ubuntu-14.04-x86_64.tar.gz'
    net0:
        name: eth0
        ip: dhcp
        ip6: dhcp
        bridge: vmbr0
# Create new container, defining rootfs and a mount, which will be created if inexistent
- proxmox_prov:
    vmid: 100
    node: mo03
    password: 123456
    hostname: example.org
    ostemplate: 'local:vztmpl/ubuntu-14.04-x86_64.tar.gz'
    mp0:
        # must be defined as proxmox storage pool
        storage: tank_media
        volume: subvol-100-disk-2
        mp: /mnt/media
        acl: True
        size: 5G
    rootfs:
        storage: local-zfs
        volume: subvol-201-disk-1
        size: 7G
# Start container
- proxmox_prov:
    vmid: 100
    state: start
# Shutdown/Stop container, with optional timeout
- proxmox_prov:
    vmid: 100
    state: shutdown
    timeout: 90
# Stop container with force
- proxmox_prov:
    vmid: 100
    state: stop
# Restart container
- proxmox_prov:
    vmid: 100
    state: restart
# Remove container
- proxmox_prov:
    vmid: 100
    state: absent
'''


import subprocess
import socket
import json
from ansible.module_utils.basic import AnsibleModule

# Constants
'''These Params are unknown to the API and will not be passed to the api by pvesh'''
API_PARAM_FILTER = ['node', 'state', 'ssh_public_keys']
'''Some (simple) params may need conversion from their YAML counterparts.'''
API_PARAM_CONV = {'onboot': int, 'delete': ','.join,
                  # disk/mp params
                  'acl': int, 'backup': int, 'quota': int, 'ro': int, 'shared': int,
                  # netX
                  'firewall': int,
                  # misc, the api always adds a final \n to description
                  'console': int, 'force': int, 'description': lambda x: x.rstrip(),
                  'template': int, 'unprivileged': int
                  }
'''These params are unknown to config API call, only used in creation.'''
API_PARAM_CREATE_ONLY = ['ostemplate', 'storage', 'vmid', 'password', 'pool',
                         'ssh-public-keys', 'unprivileged']
'''These are unknown to create, only used in config.'''
API_PARAM_CONFIG_ONLY = ['delete']

'''These are the valid network and mountpoint key names'''
NET_NAMES = ['net' + str(x) for x in range(0, 10)]
MP_NAMES = ['mp' + str(x) for x in range(0, 10)] + ['rootfs']


def pvesh(action='get', url='/', data=dict()):
    cmd = 'pvesh {0} {1} --output-format json'.format(action, url)
    if data:
        cmd = 'pvesh {0} {1} {2} --output-format json'.format(action, url,
                                         get_api_format(data))
    try:
        out = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT)
        dic = get_api_status_and_data(out, True, 0)
        dic.update({'rc': 0, 'cmd': cmd})
        return dic
        # return {'status': status, 'status_code': status_code, 'data': data}
    except subprocess.CalledProcessError as e:  # thrown if non-zero exit code
        err = e.output
        # print(err.decode('utf-8').strip() + ' : ' + cmd)
        dic = get_api_status_and_data(err, False, e.returncode)
        dic.update({'rc': e.returncode, 'cmd': cmd})
        return dic

# no first line like "200 OK" since 5.? 
def get_api_status_and_data(rawdata, json_fmt=True, exitcode=255):
    rawdata = rawdata.strip()
    status_code = exitcode
    if exitcode == 0:  # fake pre 5.x behaviour with http codes
      status_code = 200
    if(status_code == 200):
      status = 'OK'
    else:
      status = 'FAIL'
    if json_fmt:
        # catch case where pvesh does not return json data.
        try:
            data = json.loads(rawdata)
        except ValueError:
            data = rawdata
    else:
        data = rawdata
    return {'status_code': status_code, 'status': status, 'data': data}


def get_api_format(data, conv=API_PARAM_CONV, fmt='pvesh'):
    '''Get a string with the parameters in the format the api expects.
    '''
    arglist = []
    filtered = get_api_dict(data)
    for k, v in filtered.items():
        # data conversion, i.e. concat delete list
        v = conv[k](v) if k in conv else v
        # quote value if contains space
        arg = "'" + str(v) + "'" if ' ' in str(v) else str(v)
        arglist.append(k + '=' + arg)
    params = '-' + ' -'.join(arglist)
    return params


def get_api_dict(data, filter=API_PARAM_FILTER):
    '''Get a new dictionary without not-api keys,
     Also remove null values'''
    filtered_dict = dict()
    for k, v in data.items():
        if k not in filter:
            if v is not None:  # do not pass on unset (null) values
                filtered_dict[k] = v
    return filtered_dict


def get_dict_diff(A, B):
    '''Compare A to B and return all keys-value pairs in A that differ from B.'''
    diff = {}
    sa = set(A.items())
    sb = set(B.items())
    sdiff = sa ^ sb  # set symmetric_difference
    keys = set([x for x, y in sdiff])  # all keys different in A or B
    for k in keys:
        if k in A:
            diff[k] = A[k]
    return diff


def get_cluster_resources():
    result = pvesh(action='get', url='/cluster/resources')
    return result


def get_cluster_vms(resource_list):
    return [item for item in resource_list if item['type'] == 'lxc']


def get_storage_volumes(node, storage):
    '''Get all volumes on this storage on this node'''
    result = pvesh(action='get', url='/nodes/{0}/storage/{1}/content'
                   .format(node, storage))
    return result


def get_volume(node, storage, volid):
    '''Search list from get_storage_volumes for item with volid or name.'''
    result = get_storage_volumes(node, storage)
    if 'status' in result and result['status'] == 'FAIL':
      print("API call failed: " + str(result['data']))
      raise RuntimeError("API call failed: " + str(result['data']))

    volumes = result['data']
    for item in volumes:
        if 'volid' in item and volid == item['volid']:
            return item
        elif 'name' in item and volid == item['name']:
            return item
    return None


def get_volume_params(vol):
    '''From a dict (from ansible), get (splitted) volume parameters:
     storage, format, volumename(filename), size.
     vol["storage"] is optional if volume is "local:subvol-100-diskx". '''
    sto, fmt, volname, sz = (None, None, None, None)
    # TBD Could use a global DEFAULT_VOL_SIZE here
    sz = vol['size'] if 'size' in vol else '4G'
    # Problem: if user uses '0' for size, the API still saves it as '0T'.
    # HACK patch size 0 special case for API, always use 0G
    sz = '0G' if sz == '0' else sz
    sto = vol['storage'] if 'storage' in vol else None
    if 'volume' in vol:
        if vol['volume'].startswith('/'):  # plain directory case
            volname = vol['volume']
        else:
            # Could extract fmt from volume name too, TBD how are raw and qcow2 vols named?
            fmt = vol['format'] if 'format' in vol else 'subvol'
            if ':' in vol['volume']:
                sto, volname = vol['volume'].split(':')
            elif 'storage' in vol:  # case both storage and volume
                sto, volname = (vol['storage'], vol['volume'])
    return (sto, fmt, volname, sz)


def get_vm_by_id(id, resource_list=None):
    '''Get VM data from the cluster resource list, which can be provided
     as second parameter.'''
    vm = None
    if not resource_list:
        resource_list = get_cluster_vms(get_cluster_resources().get('data', None))
    for item in resource_list:
        if 'vmid' in item and int(item['vmid']) == int(id):
            vm = item
    return vm


def get_vm_by_hostname(name, resource_list=None):
    '''Get VM data from the cluster resource list by name'''
    vm = None
    if not resource_list:
        resource_list = get_cluster_vms(get_cluster_resources().get('data', None))
    for item in resource_list:
        # in the resource list the hostname is called 'name'
        if item.get('name') == name:
            vm = item
    return vm


def get_vm_config(vm):
    '''Get detailed vm config from the api, vm is a single item from the resource list.
     result.data contains the config.'''
    url = '/nodes/{0}/lxc/{1}/config'.format(vm['node'], vm['vmid'])
    result = pvesh('get', url)
    # Add node to vm config, not a true config item but needed later, by volume handling.
    if 'data' in result:
        result['data']['node'] = vm['node']
        # HACK patch data, the api always adds \n to the description string, remove.
        if 'description' in result['data']:
            result['data']['description'] = result['data']['description'].rstrip()
    return result


def set_vm_config(vm, changes):
    '''Set the vm configuration via API. converts disk/net dicts to api format.'''
    url = '/nodes/{0}/lxc/{1}/config'.format(vm['node'], vm['vmid'])
    # At last convert disks to correct format
    for k in list(changes.keys()):  # should be a safe way to iterate and change the dict.
        if k in MP_NAMES:
            changes[k] = convert_params(changes[k])
        if k in NET_NAMES:
            changes[k] = convert_params(changes[k])

    result = pvesh('set', url, changes)
    # api set config does not return anything useful.
    return result


def get_vm_disk_size(vm, disk='rootfs'):
    '''DEPRECATED Returns 0 if disk has no size property, and None if the disk does not exist'''
    if vm and disk in vm:
        items = vm[disk].split(',')
        for x in items:
            if x.startswith('size'):
                return x.split('=')[1]
        return 0
    else:
        return None


def convert_params(thing):
    '''Depending on input convert to PVE disk/net string or ansible disk/net dict'''
    # We need the list of params for an ordered, predictable (testable) output string.
    disk_params = ['mp', 'acl', 'backup', 'quota', 'ro', 'shared', 'size']
    # skip name, see elif below
    net_params = ['bridge', 'firewall', 'gw', 'gw6', 'hwaddr', 'ip',
                  'ip6', 'mtu', 'rate', 'tag', 'trunks', 'type']
    params = disk_params + net_params
    # Ask forgiveness not permission
    try:  # Dict case: convert dict to pve string
        r = ''
        if 'volume' in thing and thing['volume'].startswith('/'):  # disk directory
            r += thing['volume']
        elif 'storage' in thing and 'volume' in thing:  # disk volume case
            r += thing['storage'] + ':' + thing['volume']
        elif 'name' in thing:  # Network interface case
            r += 'name=' + thing['name']

        for p in params:
            if p in thing and p not in ('storage', 'volume'):
                v = API_PARAM_CONV[p](thing[p]) if p in API_PARAM_CONV else thing[p]
                r += ',{0}={1}'.format(p, str(v))
        return r
    except TypeError:  # String case: convert pve string to dict
        r = {}
        lstart = 0
        lines = thing.split(',')
        if not thing.startswith('name='):  # netX starts with name param
            if thing.startswith('/'):  # disk is directory
                r['volume'] = lines[lstart]
            else:
                r['storage'], r['volume'] = lines[lstart].split(':')
            lstart += 1
        for p in lines[lstart:]:
            k, v = p.split('=')
            # # HACK api patch, a size of 0 could be returned as 0T by API.
            # if k == "size" and v in ['0M', '0G', '0T']:
            #     v = '0'
            # currently all this params are int, so simply applying int is ok.
            v = bool(int(v)) if k in API_PARAM_CONV.keys() else v
            r[k] = v
        return r
    # should not happen
    return None


def get_vm_changes(api_data, vm_config, apply_filter=False):
    data = api_data
    changes = dict()

    for k, v in data.items():
        if k == 'delete' and v:
            for item in v:  # Only add delete item if exists in config
                if item in vm_config:
                    if 'delete' not in changes:
                        changes['delete'] = list()
                    changes['delete'].append(item)
        elif k in MP_NAMES and v:
            if k not in vm_config:  # the disk is new, create
                (sto, fmt, volname, sz) = get_volume_params(v)
                if get_volume(vm_config['node'], sto, volname) is None and not volname.startswith('/'):
                    create = {k: {
                                  'node': vm_config['node'],
                                  'storage': sto, 'vmid': data['vmid'], 'format': fmt,
                                  'filename': volname, 'size': sz}}
                    if '__disk_create' not in changes:
                        changes['__disk_create'] = dict()
                    changes['__disk_create'].update(create)
                    # changes.update(create)
                changes.update({k: v})
            else:
                diff = get_dict_diff(v, convert_params(vm_config[k]))
                # do not resize to 0, dir mounts have 0 size
                if 'size' in diff and diff['size'] not in [0, '0', '0M', '0G', '0T']:
                    resize = {k: {
                        'node': vm_config['node'],
                        'vmid': data['vmid'],
                        'size': diff['size'],
                    }}
                    if '__disk_resize' not in changes:
                        changes['__disk_resize'] = dict()
                    changes['__disk_resize'].update(resize)
                if diff:
                    # make sure existing disk params are not deleted by changes
                    newdiff = convert_params(vm_config[k])
                    newdiff.update(diff)
                    changes.update({k: newdiff})
            # get the params from v
        elif k in NET_NAMES and v:
            if k in vm_config:
                net_cfg = convert_params(vm_config[k])
            else:
                net_cfg = dict()
            diff = get_dict_diff(v, net_cfg)
            if diff:
                # include already set values
                net_cfg.update(diff)
                changes.update({k: net_cfg})
        elif k in vm_config:
            if v != vm_config[k]:  # existing option value mismatch, change
                changes[k] = v

        else:  # set new config option
            changes[k] = v

    if apply_filter:
        # should be ok to use this default here, because only vm_config uses changes.
        filter = list(set(API_PARAM_FILTER + API_PARAM_CREATE_ONLY))
        changes = get_api_dict(changes, filter)
    return changes


def create_volume(node, storage, vmid, format='subvol', volname=None, size='4G'):
    if volname is None:
        volname = '{0}-{1}-disk-1'.format(format, vmid)
    data = {'vmid': vmid, 'format': format, 'size': size, 'filename': volname}
    query = '/nodes/{0}/storage/{1}/content'.format(node, storage)
    result = pvesh('create', query, data)
    return result


def resize_volume(node, vmid, disk, size):
    data = {'disk': disk, 'size': size}
    query = '/nodes/{0}/lxc/{1}/resize'.format(node, vmid)
    result = pvesh('set', query, data)
    return result


def create_vm(data):
    '''Create a simple VM with a rootfs, to fully configure the created VM
    one has to use config_vm on the newly created VM.'''
    # no ID specified, get new id from cluster
    # in this case the json data is simply a string like "102"
    if 'vmid' not in data or not data['vmid']:
        result = pvesh('get', url='/cluster/nextid')
        if result.get('status_code', None) == 200:
            data['vmid'] = int(result['data'])
        else:
            return result
    vmid = data['vmid']
    # get node from ansible or data
    if not data.get('node', None):
        data['node'] = socket.gethostname()
    filtered_data = get_api_dict(data, filter=API_PARAM_CONFIG_ONLY)

    # If rootfs is fully specd, we create or own disk. If not we let proxmox do it
    # with default params (size), the other params are set by config later.
    # create rootfs disk. disk create failures not handled yet
    fs = filtered_data.get('rootfs', None)
    if fs:
        storage, fmt, volname, sz = get_volume_params(fs)
        if storage and volname:
            filtered_data.pop('storage', None)  # remove now unnecessary param from data
            if get_volume(data['node'], storage, volname) is None:
                result = create_volume(data['node'], storage, data['vmid'],
                                       fmt, volname, sz)
                # An error occured
                if result.get('status_code', None) != 200:
                    result.update({'status': 'FAIL'})
                    return result
            # finally convert rootfs dict to PVE format
            filtered_data['rootfs'] = convert_params(fs)
        else:
            # if only rootfs.storage defined, move it to main param list.
            if storage:
                filtered_data.update({'storage': storage})
            filtered_data.pop('rootfs', None)  # remove incomplete rootfs for create

    # parameters like netX and mpX are handled by config_vm, remove for create.
    for x in NET_NAMES + MP_NAMES:
        if x != 'rootfs':
            filtered_data.pop(x, None)

    result = pvesh('create', '/nodes/{0}/lxc'.format(data['node']), filtered_data)
    if result.get('status_code', None) == 200:
        result.update({'vmid': vmid})
        # more items are not really necessary
        # result.update({'action': 'create', 'create': 'success', 'vmid': vmid})
    return result


def config_vm(data, vm):
    '''Configure a vm if the config params do not match the ones in data'''
    # get vm current config
    result = get_vm_config(vm)
    # Error check
    if result['status_code'] != 200:
        result.update(changed=False)
        return result
    vm_config = result['data']
    change_items = get_vm_changes(data, vm_config, True)
    api_items = get_api_dict(change_items,
                             filter=list(set(API_PARAM_FILTER + API_PARAM_CREATE_ONLY)))
    if api_items:
        # Handle disk resize and create
        if '__disk_create' in api_items:
            items = api_items.pop('__disk_create')
            for disk, cfg in items.items():
                result = create_volume(cfg['node'], cfg['storage'],
                                       cfg['vmid'], cfg['format'], cfg['filename'],
                                       cfg['size'])
                if result['status_code'] != 200:
                    return result
        if '__disk_resize' in api_items:
            items = api_items.pop('__disk_resize')
            for disk, cfg in items.items():
                result = resize_volume(cfg['node'], cfg['vmid'], disk, cfg['size'])
                if result['status_code'] != 200:
                    return result

        # Set VM config options
        ret = set_vm_config(vm, api_items)
        # Always return a status_code
        if 'status_code' not in ret:
            # TODO if meta in ret, rc == 0
            ret.update(status_code=200)
        ret.update(changed=True, changes=change_items)
        return ret
    else:
        result.update(changed=False)
        return result


def pve_ct_present(data):

    all_results = get_cluster_resources()
    vms = get_cluster_vms(all_results['data'])
    # get vm by ID or hostname
    if data['vmid']:
        vm = get_vm_by_id(data['vmid'], vms)
    else:
        vm = get_vm_by_hostname(data['hostname'], vms)
    # If vm is null goto create
    if vm:
        result = config_vm(data, vm)
        error = False if result['status_code'] == 200 else True
        # The changed key should always be set, but to be sure check that.
        changed = result['changed'] if 'changed' in result else True
        return error, changed, result
    else:
        result = create_vm(data)
        error = False if result['status_code'] == 200 else True
        if not error:
            vmid = result.get('vmid', None)
            if vmid:
                vm = get_vm_by_id(vmid)
                cfg_result = config_vm(data, vm)
                cfg_result.update({'create': result})
                return error, True, cfg_result

        return error, True, result

    # default: something went wrong
    meta = {'present': 'ERROR', "status": all_results['status'], 'response': all_results}
    return True, False, meta


def pve_ct_absent(data):
    all_results = get_cluster_resources()
    vms = get_cluster_vms(all_results['data'])
    # get vm by ID or hostname
    if data['vmid']:
        vm = get_vm_by_id(data['vmid'], vms)
    else:
        vm = get_vm_by_hostname(data['hostname'], vms)
    # If vm == null, do nothing
    # double check id match, of none given check hostname too
    if vm and (vm['vmid'] == data['vmid']
               or (not data['vmid'] and vm['name'] == data['hostname'])):
        # node should really be in vm['node'], but if node use local node
        node = None
        if 'node' in vm and vm['node']:
            node = vm['node']
        else:
            node = socket.gethostname()
        result = pvesh('delete', '/nodes/{0}/lxc/{1}'
                       .format(node, vm['vmid']))
        error = False if result['status_code'] == 200 else True
        return error, True, result
    else:
        meta = {"absent": "VM does not exist."}
        return False, False, meta

    meta = {"absent": "ERROR", "status": all_results['status'],
            'response': all_results}
    return True, False, meta


def get_vm_id(data):
    '''Get the int vmid of a vm. data can be a dict or just a hostname.'''
    try:  # its a dict
        id = data.get('vmid')
        if id:
            return id
        name = data.get('hostname')
    except AttributeError:  # its a hostname string
        name = data
    vm = get_vm_by_hostname(name)
    if vm:
        return vm.get('vmid')
    return None


def get_vm_status(id, node=None):
    '''id is the int id or None.'''
    # vmid = int(id)
    vmid = id
    # try:
    #     vmid = int(id)
    # except ValueError:
    #     try:
    #         vmid = get_vm_by_hostname(id).get('vmid')
    #     except AttributeError:
    #         vmid = None
    if vmid and not node:
        vm = get_vm_by_id(vmid)
        node = vm.get('node') if vm else None
    if vmid and node:
        result = pvesh('get', '/nodes/{0}/lxc/{1}/status/current'
                       .format(node, vmid))
        if result.get('rc') == 0:
            state = 'unknown'
            try:
                state = result.get('data').get('status')
            except AttributeError:
                pass
            return state
    return None


def set_vm_status(id, status, node=None, timeo=None):
    cmds = ['start', 'shutdown', 'stop', 'suspend', 'resume']
    data = None
    if timeo:
        data = {'timeout': timeo}
    if status not in cmds:
        return {'status': 'FAIL', 'status_code': 400, 'data':
                'unknown status: {0}'.format(status)}
    if not node:
        vm = get_vm_by_id(id)
        node = vm.get('node') if vm else None
    if id and node:
        result = pvesh('create', '/nodes/{0}/lxc/{1}/status/{2}'
                       .format(node, id, status), data)
        return result
    return {'status': 'FAIL', 'status_code': 400, 'data': 'vm does not exist.'}


def pve_ct_start(data):
    id = get_vm_id(data)
    status = get_vm_status(id, data.get('node'))

    if not status:
        meta = {'status': 'FAIL', 'data': 'VM {0} does not exist.'.format(id)}
        return True, False, meta

    if(status != 'running'):
        meta = set_vm_status(id, 'start', data.get('node'))
        return False, True, meta
    else:
        meta = {'status': 'OK', 'data': 'VM {0} is already running.'.format(id)}
        return False, False, meta

    # unknown error
    meta = {"status": "ERROR", "data": 'Unknown error.'}
    return True, False, meta


def pve_ct_stop(data):
    id = get_vm_id(data)
    status = get_vm_status(id, data.get('node'))

    if not status:
        meta = {'status': 'FAIL', 'data': 'VM {0} does not exist.'.format(id)}
        return True, False, meta

    if(status != 'stopped'):
        meta = set_vm_status(id, 'stop', data.get('node'))
        return False, True, meta
    else:  # TBD status suspended, but suspending does not work here.
        meta = {'status': 'OK', 'data': 'VM {0} is already stopped.'.format(id)}
        return False, False, meta


def pve_ct_shutdown(data):
    id = get_vm_id(data)
    status = get_vm_status(id, data.get('node'))
    timeout = data.get('timeout')

    if not status:
        meta = {'status': 'FAIL', 'data': 'VM {0} does not exist.'.format(id)}
        return True, False, meta

    if(status != 'stopped'):
        meta = set_vm_status(id, 'shutdown', data.get('node'), timeo=timeout)
        return False, True, meta
    else:
        meta = {'status': 'OK', 'data': 'VM {0} is already stopped.'.format(id)}
        return False, False, meta


def pve_ct_restart(data):
    id = get_vm_id(data)
    status = get_vm_status(id, data.get('node'))
    timeout = data.get('timeout')

    if not status:
        meta = {'status': 'FAIL', 'data': 'VM {0} does not exist.'.format(id)}
        return True, False, meta

    if(status == 'running'):
        meta = set_vm_status(id, 'shutdown', data.get('node'), timeo=timeout)
    meta = set_vm_status(id, 'start', data.get('node'), timeo=timeout)

    return False, True, meta


def pve_ct_suspend(data):
    # suspending TBD
    meta = {"status": "ERROR", "data": 'Not implemented'}
    return True, False, meta


def pve_ct_resume(data):
    # suspending TBD
    meta = {"status": "ERROR", "data": 'Not implemented'}
    return True, False, meta


def main():

    # Proxmox API defaults are not set here, let the API deal with it.
    module = AnsibleModule(
        argument_spec=dict(
            # unsorted: state, vmid, password, hostname, ostemplate
            state=dict(default='present', type='str',
                       choices=['present', 'absent', 'start', 'shutdown', 'stop',
                                'restart', 'suspend', 'resume']),
            vmid=dict(type='int', required=False),
            password=dict(type='str', no_log=True),
            hostname=dict(type='str', required=False),
            ostemplate=dict(type='str'),
            arch=dict(type='str'),
            cmode=dict(type='str'),
            console=dict(type='bool'),
            cores=dict(type='int'),
            cpuunits=dict(type='int'),
            delete=dict(type='list'),
            description=dict(type='str'),
            force=dict(type='bool'),
            lock=dict(type='str'),
            memory=dict(type='int'),
            mp0=dict(type='dict'),
            mp1=dict(type='dict'),
            mp2=dict(type='dict'),
            mp3=dict(type='dict'),
            mp4=dict(type='dict'),
            mp5=dict(type='dict'),
            mp6=dict(type='dict'),
            mp7=dict(type='dict'),
            mp8=dict(type='dict'),
            mp9=dict(type='dict'),
            nameserver=dict(type='str'),
            net0=dict(type='dict'),
            net1=dict(type='dict'),
            net2=dict(type='dict'),
            net3=dict(type='dict'),
            net4=dict(type='dict'),
            net5=dict(type='dict'),
            net6=dict(type='dict'),
            net7=dict(type='dict'),
            net8=dict(type='dict'),
            net9=dict(type='dict'),
            node=dict(type='str'),
            onboot=dict(type='bool'),
            # could be an enum according to docs, this is freeer.
            ostype=dict(type='str'),
            pool=dict(type='str'),
            protection=dict(type='bool'),
            rootfs=dict(type='dict'),
            searchdomain=dict(type='str'),
            # hyphen in var name not allowed, workaround and exclude _var_
            ssh_public_keys=dict(type='str', aliases=['ssh-public-keys']),
            startup=dict(type='str'),
            storage=dict(type='str'),
            swap=dict(type='int', default=512),  # enforce value as in API docs.
            template=dict(type='bool'),
            # timeout is only valid for start/stop operations
            timeout=dict(type='int'),
            tty=dict(type='int'),
            unprivileged=dict(type='bool'),
        )
    )
    choice_map = {
        "present": pve_ct_present,
        "absent": pve_ct_absent,
        "start": pve_ct_start,
        "shutdown": pve_ct_shutdown,
        "stop": pve_ct_stop,
        "restart": pve_ct_restart,
        "suspend": pve_ct_suspend,
        "resume": pve_ct_resume,
    }
    is_error, has_changed, result = choice_map.get(module.params['state'])(module.params)

    if not is_error:
        module.exit_json(changed=has_changed, meta=result)
    else:
        module.fail_json(msg="Error in proxmox_prov module", meta=result)


if __name__ == '__main__':
    main()
