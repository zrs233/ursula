#!/usr/bin/python
#coding: utf-8 -*-

DOCUMENTATION = '''
---
author: Jesse Keating and Dustin Lundquist
module: cinder_volume_group
short_description: Configure LVM volume groups
description:
  - This module creates a LVM VG for Cinder to use
options:
  dev:
    description:
      - The device to make a swift disk
    required: true
'''

EXAMPLES = '''
# create a volume group for cinder, named `cinder-volumes`,
# backed by a file mounted over loop device

- swift_disk: dev=sdb
'''

import os
import pwd
import grp

def main():
    module = AnsibleModule(
        argument_spec  = dict(
            dev       = dict(required=True),
        ),
    )

    dev = module.params.get('dev')
    dev_path = "/dev/%s" % dev
    part_path = "%s1" % dev_path

    if not os.path.exists(dev_path):
        module.fail_json(msg="no such device: %s" % dev)

    if os.path.exists(part_path):
        module.exit_json(changed=False)

    # setup the parted command
    cmd = ['parted', '--script', dev_path, 'mklabel', 'gpt', 'mkpart', 'primary', '1', '100%']
    rc, out, err = module.run_command(cmd, check_rc=True)

    # make an xfs
    cmd = ['mkfs.xfs', '-f', '-i', 'size=512', part_path]
    rc, out, err = module.run_command(cmd, check_rc=True)

    # discover uuid
    cmd = ['blkid', '-o', 'value', part_path]
    rc, out, err = module.run_command(cmd, check_rc=True)
    fsuuid = out.splitlines()[0]

    # write fstab
    try:
        with open('/etc/fstab', 'a') as f:
            f.write("UUID=%s /srv/node/%s1 xfs noatime,nodiratime,nobarrier,logbufs=8 0 0\n" % (fsuuid, dev))
    except Exception, e:
        module.fail_json(msg="failed to update fstab: %s" % e)

    # mount point
    os.makedirs('/srv/node/%s1' % dev)

    # mount it
    cmd = ['mount', '/srv/node/%s1' % dev]
    rc, out, err = module.run_command(cmd, check_rc=True)

    # chown it
    swuid = pwd.getpwnam('swift').pw_uid
    swgid = grp.getgrnam('swift').gr_gid
    os.chown('/srv/node/%s1' % dev, swuid, swgid)

    module.exit_json(changed=True)

# this is magic, see lib/ansible/module.params['common.py
#<<INCLUDE_ANSIBLE_MODULE_COMMON>>
main()
