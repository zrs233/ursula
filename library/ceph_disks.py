#!/usr/bin/python
#coding: utf-8 -*-

DOCUMENTATION = '''
---
author: Siva Mullapudi
module: ceph_disks
short_description: Returns a list of valid devices
description:
    - Returns a list of ssd devices based on the osd type as facts.
options: none
'''

EXAMPLES = '''
# Assuming a journal_collocation osd type.
- ceph_disks:
'''

import os
import re
import subprocess
import json

def search_output(output, token):
    matches = ""
    for line in output.splitlines():
        if token in line:
            matches = matches + line + "\n"
    return matches.rstrip("\n")

def search_output_nearby_lines(output, token, direction, line_count):
    matches = ""
    match_line_num = 0

    for line in output.splitlines():
        if token in line:
            break
        match_line_num += 1

    if direction == "after":
        matches = "\n".join(output.splitlines()[match_line_num: match_line_num + line_count + 1])
    else:
        matches = "\n".join(output.splitlines()[match_line_num - line_count: match_line_num + 1])

    return matches.rstrip("\n")

def has_valid_mountpoint(device_name, lsblk_devices):
    partition_pattern = re.compile(device_name + "[0-9]")

    for device in lsblk_devices.splitlines():
        if partition_pattern.match(device.split()[0]):
            if len(device.split()) >= 7:
                mountPoint = device.split()[6]
                if mountPoint == "/boot" or mountPoint == "/" or mountPoint == "[SWAP]":
                    return False

    return True

def disk_type(module, device_name, device_size, adaptecTest, lsiTest, path, diskProps, adapterInfo):
    #ADAPTEC CONTROLLER
    if adaptecTest:
        cmd = ['/lib/udev/scsi_id', '--whitelist', '-p', '0x80', '--device=/dev/%s' % device_name, '--export']
        rc, out, err = module.run_command(cmd, check_rc=False)
        temp = search_output(out, "ID_SERIAL_SHORT")
        serial = temp.split('=')[1]

        if serial:
            cmd = ['%s/arcconf' % path, 'getconfig', '1', 'LD']
            rc, out, err = module.run_command(cmd, check_rc=False)

            temp = search_output_nearby_lines(out, serial, "after", 20)
            temp = search_output(temp, "Segment 0")
            longSerial = temp[-15:].strip()

            cmd = ['%s/arcconf' % path, 'getconfig', '1', 'PD']
            rc, out, err = module.run_command(cmd, check_rc=False)

            isSSD = search_output_nearby_lines(out, longSerial, "after", 13)
            isSSD = search_output(search_output(isSSD, "SSD"), "Yes")

            if isSSD:
                return "SSD"
        else:
            module.fail_json(msg="The disk may be corrupted. Please check the disk.")
            return "Error"

    #LSI CONTROLLER
    elif lsiTest:
        targetIdFromLSHW = search_output_nearby_lines(diskProps, device_name, "before", 1)
        targetIdFromLSHW = search_output(targetIdFromLSHW, "scsi")
        targetIdFromLSHW = targetIdFromLSHW.split(":")[2].split(".")[1]

        diskTypes = search_output_nearby_lines(adapterInfo, "(Target Id: " + targetIdFromLSHW + ")", "after", 75)
        diskTypes = search_output(diskTypes, "Media Type:")
        ssdDiskCount = 0

        for line in diskTypes.splitlines():
            diskType = line.split(":")[1].strip()
            if diskType == "Solid State Device":
                ssdDiskCount += 1

        if ssdDiskCount > 0:
            return "SSD"

    #NO CONTROLLERS (DEFAULT CHECK) - Assuming that an ssd is less than 2TB
    else:
        if device_size <= 2e12:
            return "SSD"

    return "HDD"

def find_available_devices(module, adaptecTest, lsiTest, path, diskProps, adapterInfo):
    ssd_devices = []
    cmd = ['lsblk', '-b', '-l', '-n']
    rc, lsblk_devices, err = module.run_command(cmd, check_rc=False)

    if not lsblk_devices:
        module.fail_json(msg="No devices detected")
        return

    for device in lsblk_devices.splitlines():
        device_name = device.split()[0]
        device_size = device.split()[3]
        device_type = device.split()[5]

        # Only consider device if the type is a disk and not a partition or lvm.
        # needs to have a valid mountpoint as well
        if device_type != "disk" or not has_valid_mountpoint(device_name, lsblk_devices):
            continue

        device_disk_type = disk_type(module, device_name, float(device_size), adaptecTest, lsiTest, path, diskProps, adapterInfo)

        if device_disk_type == "SSD":
            ssd_devices.append("/dev/" + device_name)

    return ssd_devices

def main():
    module = AnsibleModule(
          argument_spec = dict(),
    )

    firstPath="/usr/Adaptec_Event_Monitor"
    secondPath="/usr/StorMan/arcconf"
    thirdPath="/opt/MegaRAID/storcli/storcli64"
    path = adaptecTest = lsiTest = diskProps = adapterInfo = ""

    if os.path.isdir(firstPath):
        path = firstPath
        cmd = ['%s/arcconf' % firstPath, 'getconfig', '1', 'LD']
        rc, out, err = module.run_command(cmd, check_rc=False)
        adaptecTest = search_output(out, "Controllers found: 1")
    elif os.path.isdir(secondPath):
        path = secondPath
        cmd = ['%s/arcconf' % secondPath, 'getconfig', '1', 'LD']
        rc, out, err = module.run_command(cmd, check_rc=False)
        adaptecTest = search_output(out, "Controllers found: 1")
    elif os.path.isfile(thirdPath):
        cmd = [thirdPath, '/c0', 'show', 'all']
        rc, out, err = module.run_command(cmd, check_rc=False)
        lsiTest = search_output(out, "Status = Success")

        cmd = ['lshw', '-class', 'disk']
        rc, diskProps, err = module.run_command(cmd, check_rc=False)

        cmd = ['/opt/MegaRAID/storcli/storcli64', '-CfgDsply', '-aALL']
        rc, adapterInfo, err = module.run_command(cmd, check_rc=False)

    ssd_devices = find_available_devices(module, adaptecTest, lsiTest, path, diskProps, adapterInfo)
    devices_dict = {'ssd_devices': ssd_devices}

    module.exit_json(changed=False, ansible_facts=devices_dict)

# this is magic, see lib/ansible/module_common.py
from ansible.module_utils.basic import *
main()
