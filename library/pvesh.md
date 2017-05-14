# pvesh example commands

    pvesh get /nodes/moximoz/storage/local-zfs/content
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
    ]

## Test API disk create on existing

    zfs create -o refquota=4G rpool/data/subvol-300-man-2
    pvesh create /nodes/moximoz/storage/local-zfs/content -format=subvol -filename=subvol-300-man-2 -size=6G -vmid=300

    # delete
    pvesh delete /nodes/moximoz/storage/local-zfs/content/subvol-300-man-2

## Create new VM on existing disk (subvol must exist)
pvesh create /nodes/moximoz/lxc -vmid=302 -ostemplate=/var/lib/vz/template/cache/centos-7-default_20161207_amd64.tar.xz -storage=local-zfs -rootfs=local-zfs:subvol-302-exists-1,acl=1,size=4G

## Diverse unsortierte commands

    pvesh get /cluster/nextid
    pvesh get /cluster/resources
200 OK
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
      "disk" : 249036800,
      "diskread" : 53248,
      "diskwrite" : 0,
      "id" : "lxc/203",
      "maxcpu" : 2,
      "maxdisk" : 4294967296,
      "maxmem" : 536870912,
      "mem" : 3330048,
      "name" : "XY2",
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
      "disk" : 0,
      "diskread" : 0,
      "diskwrite" : 0,
      "id" : "lxc/201",
      "maxcpu" : 2,
      "maxdisk" : 6442450944,
      "maxmem" : 536870912,
      "mem" : 0,
      "name" : "YYY",
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
]

    pvesh get /nodes/moximoz/lxc/209/config
200 OK
{
   "arch" : "amd64",
   "digest" : "cb9329f7b974fce17885d93598cfcae4ebdc6ddf",
   "hostname" : "YYY9",
   "memory" : 512,
   "onboot" : 0,
   "ostype" : "centos",
   "rootfs" : "local-zfs:subvol-209-disk-1,size=4G",
   "swap" : 0
}

    pvesh set /nodes/moximoz/lxc/209/config -onboot 0
200 OK

    pvesh set /nodes/moximoz/lxc/209/config -delete cores,swap
200 OK

    pvesh create /nodes/moximoz/storage/tank_multimedia/content -format=subvol -filename=subvol-300-test1 -vmid=300 -size=4G 
200 OK

    pvesh set /nodes/moximoz/lxc/300/config -cores 1 -cpulimit 0.4 -mp0=volume=tank_multimedia:subvol-300-test0,mp=/mountinvm0
200 OK


