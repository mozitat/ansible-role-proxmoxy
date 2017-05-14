import pytest
import subprocess

API_GET = {
    '/cluster/resources': '''200 OK
    [
       {
          "cpu" : 0,
          "disk" : 0,
          "diskread" : 0,
          "diskwrite" : 0,
          "id" : "lxc/100",
          "maxcpu" : 2,
          "maxdisk" : 4294967296,
          "maxmem" : 1073741824,
          "mem" : 0,
          "name" : "testimi",
          "netin" : 0,
          "netout" : 0,
          "node" : "moximoz",
          "status" : "stopped",
          "template" : 0,
          "type" : "lxc",
          "uptime" : 0,
          "vmid" : 100
       },
       {
          "cpu" : 0,
          "disk" : 0,
          "diskread" : 0,
          "diskwrite" : 0,
          "id" : "lxc/201",
          "maxcpu" : 2,
          "maxdisk" : 6442450944,
          "maxmem" : 536870912,
          "mem" : 0,
          "name" : "VM201",
          "netin" : 0,
          "netout" : 0,
          "node" : "moximoz",
          "status" : "stopped",
          "template" : 0,
          "type" : "lxc",
          "uptime" : 0,
          "vmid" : 201
       },
       {
          "cpu" : 0,
          "disk" : 249036800,
          "diskread" : 53248,
          "diskwrite" : 0,
          "id" : "lxc/203",
          "maxcpu" : 2,
          "maxdisk" : 4294967296,
          "maxmem" : 536870912,
          "mem" : 3330048,
          "name" : "VM203",
          "netin" : 0,
          "netout" : 0,
          "node" : "moximoz",
          "status" : "running",
          "template" : 0,
          "type" : "lxc",
          "uptime" : 9474,
          "vmid" : 203
       },
       {
          "cpu" : 0,
          "disk" : 249036800,
          "diskread" : 53248,
          "diskwrite" : 0,
          "id" : "lxc/204",
          "maxcpu" : 2,
          "maxdisk" : 4294967296,
          "maxmem" : 536870912,
          "mem" : 3330048,
          "name" : "VM204",
          "netin" : 0,
          "netout" : 0,
          "node" : "moximoz",
          "status" : "running",
          "template" : 0,
          "type" : "lxc",
          "uptime" : 9474,
          "vmid" : 204
       },
       {
          "cpu" : 0.0231350590742604,
          "disk" : 1468399616,
          "id" : "node/moximoz",
          "level" : "",
          "maxcpu" : 2,
          "maxdisk" : 115041632256,
          "maxmem" : 8302227456,
          "mem" : 1191059456,
          "node" : "moximoz",
          "type" : "node",
          "uptime" : 10040
       },
       {
          "disk" : 196608,
          "id" : "storage/moximoz/tank_multimedia",
          "maxdisk" : 1930587111424,
          "node" : "moximoz",
          "storage" : "tank_multimedia",
          "type" : "storage"
       },
       {
          "disk" : 1468399616,
          "id" : "storage/moximoz/local",
          "maxdisk" : 115041632256,
          "node" : "moximoz",
          "storage" : "local",
          "type" : "storage"
       },
       {
          "disk" : 131072,
          "id" : "storage/moximoz/dir_tank_data",
          "maxdisk" : 1930587013120,
          "node" : "moximoz",
          "storage" : "dir_tank_data",
          "type" : "storage"
       },
       {
          "disk" : 747372544,
          "id" : "storage/moximoz/local-zfs",
          "maxdisk" : 114320650240,
          "node" : "moximoz",
          "storage" : "local-zfs",
          "type" : "storage"
       },
       {
          "disk" : 884736,
          "id" : "storage/moximoz/tank",
          "maxdisk" : 1930587799552,
          "node" : "moximoz",
          "storage" : "tank",
          "type" : "storage"
       }
    ]''',
    '/nodes/moximoz/lxc/100/config':
    '''
    200 OK
    {
       "arch" : "amd64",
       "description" : "My first LXC test container\n",
       "digest" : "fe5dcb51e3a024eff80b20916ec75eb68dc9f908",
       "hostname" : "testimi",
       "memory" : 1024,
       "ostype" : "centos",
       "rootfs" : "local-zfs:subvol-100-disk-1,size=4G",
       "swap" : 512
    }
    ''',
    '/nodes/moximoz/lxc/201/config':
    '''
    200 OK
    {
       "arch" : "amd64",
       "cores" : 1,
       "cpulimit" : "0.4",
       "digest" : "917c04cd2fb261a1e0d176249e6de9c6bf307d6e",
       "hostname" : "VM201",
       "memory" : 512,
       "mp0" : "tank_multimedia:subvol-201-disk-1,mp=/multimedia,acl=1,size=8G",
       "net0" : "name=eth0,bridge=vmbr0,gw=192.168.178.1,hwaddr=B6:75:39:CC:46:B1,ip=192.168.178.232/24,type=veth",
       "ostype" : "centos",
       "rootfs" : "local-zfs:subvol-201-disk-1,size=6G",
       "swap" : 512
    }
    ''',
    '/nodes/moximoz/lxc/203/config':
    '''
    200 OK
    {
        "arch" : "amd64",
        "digest" : "f4c17968e26eb5cde6d3a6e955d5efbb2120d02e",
        "hostname" : "VM203",
        "memory" : 512,
        "ostype" : "centos",
        "rootfs" : "local-zfs:subvol-203-disk-1,size=4G",
        "swap" : 512
    }
    ''',
    '/nodes/moximoz/storage/local-zfs/content':
    '''
    200 OK
    [
       {
          "content" : "images",
          "format" : "subvol",
          "name" : "subvol-100-disk-1",
          "parent" : null,
          "size" : 4294967296,
          "vmid" : "100",
          "volid" : "local-zfs:subvol-100-disk-1"
       },
       {
          "content" : "images",
          "format" : "subvol",
          "name" : "subvol-201-disk-1",
          "parent" : null,
          "size" : 6442450944,
          "vmid" : "201",
          "volid" : "local-zfs:subvol-201-disk-1"
       },
       {
          "content" : "images",
          "format" : "subvol",
          "name" : "subvol-203-disk-1",
          "parent" : null,
          "size" : 4294967296,
          "vmid" : "203",
          "volid" : "local-zfs:subvol-203-disk-1"
       },
       {
          "content" : "images",
          "format" : "subvol",
          "name" : "subvol-209-disk-1",
          "parent" : null,
          "size" : 4294967296,
          "vmid" : "209",
          "volid" : "local-zfs:subvol-209-disk-1"
       },
       {
          "content" : "images",
          "format" : "subvol",
          "name" : "subvol-211-disk-1",
          "parent" : null,
          "size" : 4294967296,
          "vmid" : "211",
          "volid" : "local-zfs:subvol-211-disk-1"
       },
       {
          "content" : "images",
          "format" : "subvol",
          "name" : "subvol-300-disk-1",
          "parent" : null,
          "size" : 4294967296,
          "vmid" : "300",
          "volid" : "local-zfs:subvol-300-disk-1"
       },
       {
          "content" : "images",
          "format" : "subvol",
          "name" : "subvol-300-man-2",
          "parent" : null,
          "size" : 4294967296,
          "vmid" : "300",
          "volid" : "local-zfs:subvol-300-man-2"
       }
    ]
    ''',
    '/nodes/moximoz/lxc/100/status/current':
    '''200 OK
    {
       "cpu" : 0,
       "cpus" : 2,
       "disk" : 0,
       "diskread" : 0,
       "diskwrite" : 0,
       "ha" : {
          "managed" : 0
       },
       "lock" : "",
       "maxdisk" : 4294967296,
       "maxmem" : 1073741824,
       "maxswap" : 536870912,
       "mem" : 0,
       "name" : "testimi",
       "netin" : 0,
       "netout" : 0,
       "status" : "stopped",
       "swap" : 0,
       "template" : "",
       "type" : "lxc",
       "uptime" : 0
    }
    ''',
    '/nodes/moximoz/lxc/203/status/current':
    '''200 OK
    {
        "cpu" : 0,
        "disk" : 249036800,
        "diskread" : 53248,
        "diskwrite" : 0,
        "maxcpu" : 2,
        "maxdisk" : 4294967296,
        "maxmem" : 536870912,
        "mem" : 3330048,
        "name" : "VM203",
        "netin" : 0,
        "netout" : 0,
        "node" : "moximoz",
        "status" : "running",
        "template" : "",
        "type" : "lxc",
        "uptime" : 9474
    }
    ''',
    '/nodes/moximoz/lxc/204/status/current':
    '''200 OK
    {
       "cpu" : 0,
       "cpus" : 2,
       "disk" : 0,
       "diskread" : 0,
       "diskwrite" : 0,
       "ha" : {
          "managed" : 0
       },
       "lock" : "",
       "maxdisk" : 4294967296,
       "maxmem" : 1073741824,
       "maxswap" : 536870912,
       "mem" : 0,
       "name" : "VM204",
       "netin" : 0,
       "netout" : 0,
       "status" : "suspended",
       "swap" : 0,
       "template" : "",
       "type" : "lxc",
       "uptime" : 0
    }
    ''',
    '/nodes/moximoz/lxc/999/status/current':
    {'error': True, 'rc': 2,
     'output': 'Configuration file \'nodes/moximoz/lxc/1001.conf\' does not exist'},
}

API_SET = {}
API_CREATE = {
    '/nodes/moximoz/lxc/100/status/start':
    '''200 OK
    UPID:moximoz:00000EA7:00003052:58AACFA3:vzstart:100:root@pam:
    ''',
    '/nodes/moximoz/lxc/100/status/stop':
    '''200 OK
    UPID:moximoz:0000164D:0000ED66:58AAD187:vzstop:100:root@pam:
    ''',
    '/nodes/moximoz/lxc/100/status/shutdown':
    '''200 OK
    UPID:moximoz:00002D4D:0014366D:58AEF68B:vzshutdown:100:root@pam:
    ''',
    '/nodes/moximoz/lxc/203/status/start':
    '''200 OK
    UPID:moximoz:00000EA7:00003052:58AACFA3:vzstart:203:root@pam:
    ''',
    '/nodes/moximoz/lxc/203/status/stop':
    '''200 OK
    UPID:moximoz:00000EA7:00003052:58AACFA3:vzstop:203:root@pam:
    ''',
    '/nodes/moximoz/lxc/203/status/shutdown':
    '''200 OK
    UPID:moximoz:00002D4D:0014366D:58AEF68B:vzshutdown:203:root@pam:
    ''',
    '/nodes/moximoz/lxc/204/status/start':
    '''200 OK
    UPID:moximoz:00000EA7:00003052:58AACFA3:vzstart:204:root@pam:
    ''',
    '/nodes/moximoz/lxc/204/status/stop':
    '''200 OK
    UPID:moximoz:00000EA7:00003052:58AACFA3:vzstop:204:root@pam:
    ''',
    '/nodes/moximoz/lxc/204/status/shutdown':
    '''200 OK
    UPID:moximoz:00002D4D:0014366D:58AEF68B:vzshutdown:204:root@pam:
    ''',
    }
API_DELETE = {}

# # # Test data for disk/net difference tests, List indices approach.
# Everything will be matched against config from API get /nodes/moximoz/lxc/201/config.
# DIffBase Test data basis
DIB = [
    {
        'state': 'present',
        'vmid': 201,
        'hostname': 'VM201',
        'memory': 512,
        'cores': 1,
        'cpulimit': '0.4',
    },
]

# DiffCHanges, What will be changed
DCH = [
    {
        'rootfs': {'storage': 'local-zfs',
                   'volume': 'subvol-201-disk-1', 'size': '7G'},
    },
    {
        'rootfs': {'size': '9G'},
    },
    {
        'mp0': {
                'storage': 'tank_multimedia',
                'volume': 'subvol-201-disk-1',
                'mp': '/multimedia',
                'acl': True,
                'shared': True,
                'size': '10G',
            },
    },
]

# DiffEXPect Expect Data
DEXP = [
    {
        'rootfs': {'storage': 'local-zfs',
                   'volume': 'subvol-201-disk-1', 'size': '7G'},
        '__disk_resize': {'rootfs': {'node': 'moximoz',
                                     'size': '7G',
                                     'vmid': 201}
                          },
    },
    {
        'rootfs': {'storage': 'local-zfs',
                   'volume': 'subvol-201-disk-1', 'size': '9G'},
        '__disk_resize': {'rootfs': {'node': 'moximoz',
                                     'size': '9G',
                                     'vmid': 201}
                          },
    },
    {
        'mp0': {
                'storage': 'tank_multimedia',
                'volume': 'subvol-201-disk-1',
                'mp': '/multimedia',
                'acl': True,
                'shared': True,
                'size': '10G',
            },
        '__disk_resize': {
            'mp0': {'node': 'moximoz', 'size': '10G', 'vmid': 201, }
        }
    },
]

CHANGE_DATA = {
    '201 basic': {
        'state': 'present',
        'vmid': 201,
        'hostname': 'VM201',
        'memory': 512,
        'cores': 1,
        'cpulimit': '0.4',
        # 'disk': '4G',
        # 'swap': 512,
        # 'storage': 'local-zfs',
        # 'ostemplate': '/var/lib/vz/template/cache/centos-7-default_20161207_amd64.tar.xz',
        # "mp0": "tank_multimedia:subvol-201-disk-1,mp=/multimedia,acl=1,size=8G",
        # TBD type=veth
        # "net0": "name=eth0,bridge=vmbr0,gw=192.168.178.1,ip=192.168.178.232/24,type=veth",
        # 'onboot': False,
        # 'delete': [cores, cpulimit],
        # '': '',
    },
    '201 rootfs': {
        'state': 'present',
        'vmid': 201,
        'hostname': 'VM201',
        'memory': 512,
        'rootfs': {'storage': 'local-zfs',
                    'volume': 'subvol-201-disk-1', 'size': '7G'},
        # 'ostemplate': '/var/lib/vz/template/cache/centos-7-default_20161207_amd64.tar.xz',
        # 'storage': 'local-zfs',
    },
    '201 net0': {
        "net0": {'name': 'eth0', 'bridge': 'vmbr0', 'gw': '192.168.178.1',
                 'ip': '192.168.111.111/24'},
    },
    '201 root resize': {
        'rootfs': {'size': '9G'},
    },
    '201 mp0 resize': {
        'mp0': {
            'storage': 'tank_multimedia',
            'volume': 'subvol-201-disk-1',
            'mp': '/multimedia',
            'acl': True,
            'shared': True,
            'size': '10G',
        },
    },
    '201 mp1 create': {
        'mp1': {
            'storage': 'tank_multimedia',
            'volume': 'subvol-201-disk-2',
            'mp': '/muhmuh',
            'acl': True,
            # 'size': '10G',
        },
    },
    '201 multi resize': {
        'rootfs': {'size': '9G'},
        'mp0': {
            'storage': 'tank_multimedia',
            'volume': 'subvol-201-disk-1',
            'mp': '/multimedia',
            'acl': True,
            'size': '10G',
        },
    },
    '201 multi create': {
        'mp0': {
            'storage': 'tank_multimedia',
            'volume': 'subvol-201-disk-1',
            'mp': '/multimedia',
            'acl': True,
            'size': '10G',
        },
        'mp1': {
            'storage': 'tank_multimedia',
            'volume': 'subvol-201-disk-2',
            'mp': '/muhmuh',
            'acl': True,
            # 'size': '10G',
        },
    },
}


def mergedict(x, y):
    """Given two dicts, merge them into a new dict as a shallow copy."""
    z = x.copy()
    z.update(y)
    return z


@pytest.fixture(autouse=True)
def patch_functions(monkeypatch):
    monkeypatch.setattr('subprocess.check_output', subprocess_mock)


def subprocess_mock(cmd, shell=True, stderr=''):
    cmd_lines = cmd.split()
    action = cmd_lines[1]
    url = cmd_lines[2]
    all_params = cmd_lines[3:]
    # assume action is always ok.
    API = API_GET
    if action == 'set':
        API = API_SET
    if action == 'create':
        API = API_CREATE
    if action == 'delete':
        API = API_DELETE

    err_output = 'no \'{0}\' handler for {1} '.format(action, url)
    rc = 1
    if url in API:
        try:
            API[url].get('error')
            err_output = API[url].get('output', err_output)
            rc = API[url].get('rc', rc)
            raise subprocess.CalledProcessError(rc, cmd, err_output)
        except AttributeError:
            return API[url]
    else:
        raise KeyError('No url in fake API: ' + action + ' ' + url)

    return err_output
