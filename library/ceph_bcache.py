#!/usr/bin/python
#coding: utf-8 -*-

DOCUMENTATION = """
---
author: Michael Sambol
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
            disks=dict(required=True),
            ssd_device=dict(required=True),
        ),
    )
    disks = module.params.get('disks')
    ssd_device = module.params.get('ssd_device')
    changed = False

    for subdir, dirs, files in os.walk('/dev/disk/by-uuid/'):
      for file in files:
        disk = os.path.join(subdir, file)
      
        cmd = ['blkid', '-o', 'value', '-s', 'TYPE', disk]
        rc, out, err = module.run_command(cmd, check_rc=False)
        fs_type = out.rstrip()

        # sata drives will be xfs at this point; these are the ones we want
        if fs_type == 'xfs':

          # get the uuid from the current path
          cmd = ['basename', disk]
          rc, out, err = module.run_command(cmd, check_rc=False)
          uuid = out.rstrip() 

          # running this command with the uuid argument will return the same value each time
          cmd = ['ceph', 'osd', 'create', uuid]
          rc, out, err = module.run_command(cmd, check_rc=False) 
          osd_id = out.rstrip()

          # if first time running 'ceph osd create' against this uuid, create the osd dir
          # and handle rest of activation. if directory exists, the device has already
          # been activated
          if not os.path.exists('/var/lib/ceph/osd/ceph-' + osd_id): 
            os.makedirs('/var/lib/ceph/osd/ceph-' + osd_id)
            changed = True

            bcache_index = int(osd_id) % len(disks) 
            partition_index = bcache_index + 1

            cmd = ['mount', '/dev/bcache' + str(bcache_index), '/var/lib/ceph/osd/ceph-' + osd_id]
            rc, out, err = module.run_command(cmd, check_rc=False) 

            cmd = ['ceph-osd', '-i', osd_id, '--mkfs', '--mkkey', '--osd-uuid', uuid]
            rc, out, err = module.run_command(cmd, check_rc=False)

            os.remove('/var/lib/ceph/osd/ceph-' + osd_id + '/journal')

            cmd = ['ln', '-s', '/dev/' + ssd_device + str(partition_index), '/var/lib/ceph/osd/ceph-' + osd_id + '/journal']
            rc, out, err = module.run_command(cmd, check_rc=False)

            cmd = ['ceph-osd', '-i', osd_id, '--mkjournal']
            rc, out, err = module.run_command(cmd, check_rc=False)    
 
            cmd = ['umount', '/var/lib/ceph/osd/ceph-' + osd_id]
            rc, out, err = module.run_command(cmd, check_rc=False)

            cmd = ['ceph-disk', 'activate', '/dev/bcache' + str(bcache_index)]
            rc, out, err = module.run_command(cmd, check_rc=False)

    module.exit_json(changed=changed)
     
from ansible.module_utils.basic import *
main()
