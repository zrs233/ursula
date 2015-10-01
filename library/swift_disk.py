#!/usr/bin/python
# coding: utf-8 -*-

DOCUMENTATION = '''
---
author: Jesse Keating and Dustin Lundquist
module: swift_disk
short_description: Functions to streamline swift disk management
'''

EXAMPLES = '''
# unmount, format to xfs, and mount sdb
# irrelevant of the drive's current state
# (not mounted, not XFS, etc.)

- swift_disk: dev=sdb
'''
from ansible.module_utils.basic import *
import os
import pwd
import grp


def main():
    module = AnsibleModule(
        argument_spec=dict(
            dev=dict(required=True),
        ),
    )

    was_changed = False

    dev = module.params.get('dev')
    dev_path = "/dev/%s" % dev
    part_path = "%s1" % dev_path

    if not os.path.exists(dev_path):
        module.fail_json(msg="no such device: %s" % dev)

    #Algorithm to cover all use cases for formatting a disk to XFS
    #1) If FS Type is not XFS
        #1.1) If device is mounted, unmount it
        #1.2) Format disk and mount it (done)
    #2) If FS Type is XFS
        #2.1) If device is not mounted or on wrong mount point
            #2.2.1) Unmount (if needed)
            #2.2.2) Format disk and mount it (done)

    if get_fs_type(dev, module) != 'xfs\n':
        was_changed = True
        if is_mounted(dev, module):
            unmount_dev(dev, module)
        format_dev(dev_path, part_path, module)
        mount_dev(dev, part_path, module)
    else:
        if get_mount_point(dev, module) != get_expected_mount(dev):
            unmount_dev(dev, module)
            was_changed = True
            format_dev(dev_path, part_path, module)
            mount_dev(dev, part_path, module)

    module.exit_json(changed=was_changed)

# Check if the specified device is mounted
def is_mounted(dev, module):
    return get_mount_point(dev, module) != ''


# Get the mount point of specified device
def get_mount_point(dev, module):
    cmd = "mount | grep %s | awk '{print $3}'" % dev
    rc, output, err = module.run_command(cmd, use_unsafe_shell=True)
    
    output = output.rstrip('\n') 
    return output


# Format the specified device with xfs file system
def format_dev(dev_path, part_path, module):
    # setup the parted command
    cmd = ['parted', '--script', dev_path, 'mklabel', 'gpt', 'mkpart', 'primary', '1', '100%']
    module.run_command(cmd, check_rc=True)

    cmd = ['mkfs.xfs', '-f', '-i', 'size=512', part_path]
    module.run_command(cmd, check_rc=True)


# Clean the fstab
def clean_fstab(dev, mnt_point, module):
    cmd = ['sed', '-i', '\#%s#d' % mnt_point, '/etc/fstab']
    module.run_command(cmd, check_rc=True)


# Unmount a specified device
def unmount_dev(dev, module):
    if is_mounted(dev, module):
        mnt_path = get_mount_point(dev, module)
        cmd = ['umount', mnt_path]
        module.run_command(cmd, check_rc=True)

        clean_fstab(dev, mnt_path, module)


# Mount a specific device and write info to fstab
def mount_dev(dev, part_path, module):
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
    module.run_command(cmd, check_rc=True)

    # chown it
    swuid = pwd.getpwnam('swift').pw_uid
    swgid = grp.getgrnam('swift').gr_gid
    os.chown('/srv/node/%s1' % dev, swuid, swgid)


# Return the expected mount
def get_expected_mount(dev):
    return '/srv/node/%s1' % dev


# Check if the file system of a device is xfs
def is_xfs_fs(dev, module):
    return get_fs_type(dev, module) == "xfs\n"


# Return the expected UUID for a device
def get_expected_uuid(dev, module):
    return get_blkid("UUID", dev, module)


# Get blkid of device
def get_blkid(key, dev, module):
    cmd = ['blkid', '-c', '/dev/null', '-s', key, '-o', 'value', "/dev/%s1" % dev]
    rc, output, err = module.run_command(cmd)

    if output and output != '':
        return output
    else:
        return None


# Get file type of device
def get_fs_type(dev, module):
    return get_blkid("TYPE", dev, module)


# this is magic, see lib/ansible/module.params['common.py
# <<INCLUDE_ANSIBLE_MODULE_COMMON>>
main()
