#!/usr/bin/python
#coding: utf-8 -*-

DOCUMENTATION = """
---
author: Michael Sambol, Siva Nandyala
module: ceph_bcache
short_description: Activates OSDs in a Bcache Ceph cluster
description: Because of the nature of a Bcache Ceph cluster,
             a "stateless" approach was taken. This module was
             largely based on: http://redpill-linpro.com/sysadvent/2015/12/18/stateless-osd-servers.html
options:
  disks:
    description:
      - List of disks. Defined as ceph.disks in the env.
    required: True
  ssd_device:
    description:
      - The SSD device. Defined as ceph.bcache_ssd_device in the env.
    required: True
"""

EXAMPLES = """
- name: activate osds
  ceph_bcache:
    disks: "{{ ceph.disks }}"
    ssd_device: "{{ ceph.bcache_ssd_device }}"
"""

import os


def main():
    module = AnsibleModule(
        argument_spec=dict(
            disks=dict(type='list',required=True),
            ssd_device=dict(required=True),
        ),
    )
    disks = module.params.get('disks')
    ssd_device = module.params.get('ssd_device')
    changed = False
    uuids_in_order = [None] * len(disks)

    # the disks have symlinks to /dev/bcacheX. we need the disks
    # in increasing order by X.
    for subdir, dirs, files in os.walk('/dev/disk/by-uuid/'):
      for uuid in files:
        disk = os.path.join(subdir, uuid)
        path = os.path.realpath(disk)

        if 'bcache' in path:
          bcache_index = int(path[len(path)-1:])
          uuids_in_order.pop(bcache_index)
          uuids_in_order.insert(bcache_index,uuid)

    for i in range(0, len(uuids_in_order)):

      # running this command with the uuid argument will return the same value each time
      cmd = ['ceph', 'osd', 'create', uuids_in_order[i]]
      rc, out, err = module.run_command(cmd, check_rc=True)
      osd_id = out.rstrip()

      # if first time running 'ceph osd create' against this uuid, create the osd dir
      # and handle rest of activation. if directory exists, the device has already
      # been activated.
      if not os.path.exists('/var/lib/ceph/osd/ceph-' + osd_id):
        os.makedirs('/var/lib/ceph/osd/ceph-' + osd_id)
        changed = True

        bcache_index = int(osd_id) % len(disks)
        partition_index = bcache_index + 1

        cmd = ['mount', '/dev/bcache' + str(bcache_index), '/var/lib/ceph/osd/ceph-' + osd_id]
        rc, out, err = module.run_command(cmd, check_rc=True)

        cmd = ['ceph-osd', '-i', osd_id, '--mkfs', '--mkkey', '--osd-uuid', uuids_in_order[i]]
        rc, out, err = module.run_command(cmd, check_rc=True)

        os.remove('/var/lib/ceph/osd/ceph-' + osd_id + '/journal')

        cmd = ['ln', '-s', '/dev/' + ssd_device + str(partition_index), '/var/lib/ceph/osd/ceph-' + osd_id + '/journal']
        rc, out, err = module.run_command(cmd, check_rc=True)

        cmd = ['ceph-osd', '-i', osd_id, '--mkjournal']
        rc, out, err = module.run_command(cmd, check_rc=True)

        cmd = ['umount', '/var/lib/ceph/osd/ceph-' + osd_id]
        rc, out, err = module.run_command(cmd, check_rc=True)

        cmd = ['ceph-disk', 'activate', '/dev/bcache' + str(bcache_index)]
        rc, out, err = module.run_command(cmd, check_rc=True)

        with open("/etc/fstab", "a") as fstab:
          fstab.write('UUID=' + uuids_in_order[i] + ' /var/lib/ceph/osd/ceph-' + osd_id + ' xfs defaults,noatime,largeio,inode64,swalloc 0 0\n')

    module.exit_json(changed=changed)

from ansible.module_utils.basic import *
main()
