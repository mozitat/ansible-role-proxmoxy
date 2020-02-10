from __future__ import absolute_import
from . import proxmox_prov as pv
from .conftest import CHANGE_DATA, mergedict, DIB, DCH, DEXP
import pytest

# run with watch
# ptw -c ./library/
# sound:
# ptw -c --onfail "echo -e '\a'" ./library/
# ptw -c --onfail "paplay /usr/share/sounds/freedesktop/stereo/suspend-error.oga" ./library/

Adict = {'state': 'present', 'vmid': 333, 'hostname': 'myhost', 'node': 'A',
         'onboot': False, 'ostemplate': None, 'delete': ['A', 'B']}


# This is much shorter!
@pytest.mark.parametrize('input', [
    ({'cores': 2}),
    ({'cores': 2, 'cpulimit': '0.5'}),
    ({'cores': 2, 'cpulimit': '0.5', 'delete': ['cores', 'cpulimit']}),
    # pytest.mark.xfail(({'cores': 99}))
])
def test_get_vm_changes(input):
    vm = pv.get_vm_by_id(201, pv.get_cluster_resources()['data'])
    result = pv.get_vm_config(vm)
    cfg = result['data']
    data = CHANGE_DATA['201 basic'].copy()
    data.update(input)
    changes = pv.get_vm_changes(data, cfg, True)
    assert changes == input


# @pytest.mark.skip()
@pytest.mark.parametrize('input, expect', [
    (DIB[0].copy(), {}),
    (mergedict(DIB[0], DCH[0]), DEXP[0]),
    (mergedict(DIB[0], DCH[1]), DEXP[1]),
    (mergedict(DIB[0], DCH[2]), DEXP[2]),
])
def test_get_vm_changes_disk(input, expect):
    vm = pv.get_vm_by_id(201, pv.get_cluster_resources()['data'])
    cfg = pv.get_vm_config(vm)['data']
    changes = pv.get_vm_changes(input, cfg, True)
    assert changes == expect


@pytest.mark.parametrize('input, expect', [
    # dict to command line
    ({'storage': 'tank_multimedia', 'volume': 'subvol-201-disk-1',
      'mp': '/multimedia', 'acl': True, 'size': '8G'},
     'tank_multimedia:subvol-201-disk-1,mp=/multimedia,acl=1,size=8G'),
    # command line to dict
    ('tank_multimedia:subvol-201-disk-1,mp=/multimedia,acl=0,size=8G',
     {'storage': 'tank_multimedia', 'volume': 'subvol-201-disk-1',
      'mp': '/multimedia', 'acl': False, 'size': '8G'}),
    # dict to command line with dir mount and reverse
    ({'volume': '/mnt/dirmount',
      'mp': '/dir_mount', 'size': '0G'},
     '/mnt/dirmount,mp=/dir_mount,size=0G'),
    ('/mnt/dirmount,mp=/dir_mount,size=0G',
     {'volume': '/mnt/dirmount',
      'mp': '/dir_mount', 'size': '0G'}),
    # simulate api returning 0T for 0 size
    ('/mnt/dirmount,mp=/dir_mount,size=0T',
     {'volume': '/mnt/dirmount',
      'mp': '/dir_mount', 'size': '0T'}),
    # netX both ways
    ({'name': 'eth0', 'bridge': 'vmbr0', 'hwaddr': 'as:04:23:ds:32', 'ip': '192.168.2.1/24',},
     'name=eth0,bridge=vmbr0,hwaddr=as:04:23:ds:32,ip=192.168.2.1/24'),
    ('name=eth0,bridge=vmbr0,firewall=0', {'name': 'eth0', 'bridge': 'vmbr0', 'firewall': False},),
    ('name=eth1,bridge=vmbr0,gw=192.168.178.1,hwaddr=B6:75:39:CC:46:B1,'
     'ip=192.168.178.207/24,mtu=1400,tag=3,type=veth',
     {'name': 'eth1', 'bridge': 'vmbr0', 'gw': '192.168.178.1', 'hwaddr':
      'B6:75:39:CC:46:B1', 'ip': '192.168.178.207/24', 'mtu': '1400', 'tag': '3',
      'type': 'veth'}),
    # (, ,),
])
def test_convert_params(input, expect):
    result = pv.convert_params(input)
    assert result == expect


@pytest.mark.parametrize('input, pve_string, expect', [
    ({'acl': False, 'size': '10G'},
     'tank_multimedia:subvol-201-disk-1,mp=/multimedia,acl=1,size=8G',
     {'size': '10G', 'acl': False}),
    ({'storage': 'tank_multimedia', 'volume': 'subvol-201-disk-1', 'mp': '/change', 'acl': True, 'size': '10G'},
     'tank_multimedia:subvol-201-disk-1,mp=/multimedia,acl=1,size=8G',
     {'size': '10G', 'mp': '/change'}),
    # (, ,),
])
def test_dict_diff(input, pve_string, expect):
    changes = pv.get_dict_diff(input, pv.convert_params(pve_string))
    assert changes == expect


@pytest.mark.parametrize('inp, exp', [
                         ({'volume': 'local-zfs:subvol-101-disk-1', 'size': '4G'},
                          ('local-zfs', 'subvol', 'subvol-101-disk-1', '4G')),
                         ({'storage': 'local-zfs', 'volume': 'subvol-101-disk-1', 'size': '4G'},
                          ('local-zfs', 'subvol', 'subvol-101-disk-1', '4G')),
                         ({'volume': 'local-zfs:subvol-200-diskX'},
                          ('local-zfs', 'subvol', 'subvol-200-diskX', '4G')),
                         ({'volume': 'local:subvol-200-diskX', 'format': 'raw'},
                          ('local', 'raw', 'subvol-200-diskX', '4G')),
                         ({'storage': 'local-zfs', 'size': '6G'},
                          ('local-zfs', None, None, '6G')),
                         # case user uses 0 for size 0G
                         ({'volume': '/tank/directory', 'size': '0'},
                          (None, None, '/tank/directory', '0G')),
                         # ('bla', 'ba'),
                         ])
def test_get_volume_params(inp, exp):
    (sto, fmt, volname, sz) = pv.get_volume_params(inp)
    assert (sto, fmt, volname, sz) == exp


def test_get_vm_config():
    vm = pv.get_vm_by_id(201, pv.get_cluster_resources()['data'])
    result = pv.get_vm_config(vm)
    assert result['status_code'] == 200
    cfg = result['data']
    assert cfg['arch'] == 'amd64'
    assert cfg['hostname'] == 'VM201'


def test_get_vm_by_id_simple():
    vm = pv.get_vm_by_id(100, pv.get_cluster_resources()['data'])
    # this is still vm data from the resource list
    assert vm['vmid'] == 100
    assert vm['name'] == 'testimi'


def test_get_vm_by_id_onlyid():
    vm = pv.get_vm_by_id(201)
    assert vm['vmid'] == 201
    assert vm['name'] == 'VM201'
    assert vm['id'] == 'lxc/201'


def test_get_vm_by_hostname_only():
    vm2 = pv.get_vm_by_hostname('NotUnderThisName')
    assert vm2 is None
    vm = pv.get_vm_by_hostname('testimi')
    assert vm['vmid'] == 100
    assert vm['name'] == 'testimi'
    assert vm['id'] == 'lxc/100'


@pytest.mark.parametrize('inp, exp', [
                         (100, 'stopped'),
                         # expects int
                         pytest.mark.xfail(('testimi', 'stopped')),
                         ((100, 'moximoz'), 'stopped'),
                         (999, None),
                         (None, None),
                         # ('VMdoesnotexist', None),
                         ((999, 'moximoz'), None),
                         ])
def test_get_vm_status(inp, exp):
    try:
        st = pv.get_vm_status(*inp)
    except TypeError:
        st = pv.get_vm_status(inp)
    assert st == exp


@pytest.mark.parametrize('inp, exp', [
                         ((100, 'start'), ['UPID:moximoz', 'vzstart']),
                         ((100, 'stop'), ['UPID:moximoz', 'vzstop']),
                         ((999, 'stop'), ['vm does not exist']),
                         ])
def test_set_vm_status(inp, exp):
    try:
        st = pv.set_vm_status(*inp)
    except TypeError:
        st = pv.set_vm_status(inp)
    for e in exp:
        if 'does not exist' not in e:
            assert st.get('status_code') == 200
        assert e in st.get('data')


@pytest.mark.parametrize('inp, exp', [
                         # doesn't exist
                         ({'vmid': 999}, (True, False, {'status': 'FAIL'})),
                         # is stopped
                         ({'vmid': 100}, (False, True, {'status': 'OK'})),
                         ({'hostname': 'testimi'}, (False, True, {'status': 'OK'})),
                         # is running
                         ({'vmid': 203}, (False, False, {'status': 'OK'})),
                         # is suspended
                         ({'vmid': 204}, (False, True, {'status': 'OK'})),
                         ])
def test_pve_ct_start(inp, exp):
        e, ch, meta = pv.pve_ct_start(inp)
        assert e == exp[0]
        assert ch == exp[1]
        assert list(exp[2].items())[0] in list(meta.items())


@pytest.mark.parametrize('inp, exp', [
                         # doesn't exist
                         ({'vmid': 999}, (True, False, {'status': 'FAIL'})),
                         # is stopped
                         ({'vmid': 100}, (False, False, {'status': 'OK'})),
                         ({'hostname': 'testimi'}, (False, False, {'status': 'OK'})),
                         # is running
                         ({'vmid': 203}, (False, True, {'status': 'OK'})),
                         # TBD status suspended, but suspending does not work here.
                         # ({'vmid': 204}, (False, True, {'status': 'OK'})),
                         ])
def test_pve_ct_stop(inp, exp):
        e, ch, meta = pv.pve_ct_stop(inp)
        assert e == exp[0]
        assert ch == exp[1]
        assert list(exp[2].items())[0] in list(meta.items())


@pytest.mark.parametrize('inp, exp', [
                         # doesn't exist
                         ({'vmid': 999}, (True, False, {'status': 'FAIL'})),
                         # is stopped
                         ({'vmid': 100}, (False, False, {'status': 'OK'})),
                         ({'hostname': 'testimi'}, (False, False, {'status': 'OK'})),
                         # is running
                         ({'vmid': 203}, (False, True, {'status': 'OK'})),
                         ({'vmid': 203, 'timeout': 40}, (False, True, {'status': 'OK'})),
                         ])
def test_pve_ct_shutdown(inp, exp):
        e, ch, meta = pv.pve_ct_shutdown(inp)
        assert e == exp[0]
        assert ch == exp[1]
        assert list(exp[2].items())[0] in list(meta.items())


@pytest.mark.parametrize('inp, exp', [
                         # if vmid it just returns it.
                         ({'vmid': 100}, 100),
                         ({'vmid': 999}, 999),
                         ({'vmid': 100, 'hostname': 'testimi'}, 100),
                         ({'hostname': 'testimi'}, 100),
                         ])
def test_get_vm_id(inp, exp):
        vmid = pv.get_vm_id(inp)
        assert vmid == exp


def test_get_cluster_resources():
    res = pv.get_cluster_resources()
    assert res['status_code'] == 200
    assert res['data'][0]['type'] == 'lxc'


def test_get_api_dict_simple():
    new = pv.get_api_dict(Adict)
    assert Adict != new
    assert new == {'hostname': 'myhost', 'vmid': 333, 'onboot': False,
                   'delete': ['A', 'B']}


def test_get_api_dict_remove_Nones():
    new = pv.get_api_dict(Adict)
    assert Adict != new
    assert 'ostemplate' not in new


def test_get_api_dict_keep_Falsy():
    new = pv.get_api_dict(Adict)
    assert Adict != new
    assert new['hostname'] == 'myhost'
    assert new['onboot'] is False


def test_get_api_format_simple():
    # new = pv.get_api_dict(Adict)
    new = pv.get_api_dict({'hostname': 'my', 'onboot': False})
    # line = pv.get_api_format(new, pv.API_PARAM_CONV)
    line = pv.get_api_format(new)
    assert line == "-hostname=my -onboot=0"


def test_get_api_format_with_delete():
    new = pv.get_api_dict({'hostname': 'my', 'onboot': False,
                           'delete': ['cores', 'cpulimit']})
    assert 'onboot' in new
    line = pv.get_api_format(new, pv.API_PARAM_CONV)
    assert line == "-hostname=my -onboot=0 -delete=cores,cpulimit"
