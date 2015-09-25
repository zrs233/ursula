#!/usr/bin/python
#coding: utf-8 -*-

DOCUMENTATION = '''
---
author: Siva Mullapudi
module: ceph_disks
short_description: Outputs a list of valid devices
description:
    - Outputs a list of devices based on the osd type.
options: none
'''

EXAMPLES = '''
# Assuming a journal_collocation osd type
- ceph_disks:
  register: ssds
'''

import os
import re
import subprocess
import json
from subprocess import Popen, PIPE

def run_command(cmd):
    process = Popen(cmd, stdout=PIPE, stderr=PIPE, shell=True)
    stdout, stderr = process.communicate()
    return stdout.rstrip('\n')

def has_valid_mountpoint(device_name, lsblk_devices):
    partition_pattern = re.compile(device_name + "[0-9]")

    for device in lsblk_devices.splitlines():
        if partition_pattern.match(device.split()[0]):
            if len(device.split()) >= 7:
                mountPoint = device.split()[6]
                if mountPoint == "/boot" or mountPoint == "/" or mountPoint == "[SWAP]":
                    return False

    return True

def disk_type(device_name, device_size, adaptecTest, lsiTest, path):
    #ADAPTEC CONTROLLER
    if adaptecTest:
        temp = run_command("/lib/udev/scsi_id --whitelist -p 0x80 --device=/dev/" + device_name + " --export | grep ID_SERIAL_SHORT")
        serial = temp.rpartition('=')[0]

        if serial:
            temp = run_command(path + "/arcconf getconfig 1 LD | grep -A20 \"" + serial + "\" | grep \"Segment 0\"")
            longSerial = temp[-15:]
            isSSD = run_command(path + "/arcconf getconfig 1 PD | grep -A13 " + longSerial + " | grep SSD | grep Yes")

            if isSSD:
                return "SSD"
        else:
            module.fail_json(msg="The disk may be corrupted. Please check the disk.")
            return "Error"

    #LSI CONTROLLER
    elif lsiTest:
        targetIdFromLSHW = run_command("cat /tmp/diskProps.txt | grep -B1 " + device_name + "| grep scsi | awk -F\":\" '{print $3}' |  awk -F\".\" '{print $2}'")
        diskTypes = run_command("cat /tmp/adapterInfo.txt | grep -A75 \"(Target Id: " + targetIdFromLSHW + ")\" | grep \"Media Type:\" | awk '{print $3 \" \" $4 \" \" $5}'")
        ssdDiskCount = run_command("echo \"" + diskTypes + "\" | sort | uniq -c | grep \"Solid State Device\" | awk '{print $1}'")

        if ssdDiskCount:
            return "SSD"

    #NO CONTROLLERS (DEFAULT CHECK) - Assuming that an ssd is less than 2TB
    else:
        if device_size <= 2e12:
            return "SSD"

    return "HDD"

def find_available_devices(adaptecTest, lsiTest, path):
    ssd_devices = []
    hdd_devices = []
    lsblk_devices = run_command("lsblk -l -b -n")

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

        device_disk_type = disk_type(device_name, float(device_size), adaptecTest, lsiTest, path)

        if device_disk_type == "SSD":
            ssd_devices.append("/dev/" + device_name)
        elif device_disk_type == "HDD":
            hdd_devices.append("/dev/" + device_name)

    return ssd_devices

def main():
    module = AnsibleModule(
          argument_spec = dict(),
    )

    firstPath="/usr/Adaptec_Event_Monitor"
    secondPath="/usr/StorMan/arcconf"
    thirdPath="/opt/MegaRAID/storcli/storcli64"
    path = ""
    adaptecTest = ""
    lsiTest = ""

    if os.path.isdir(firstPath):
        path = firstPath
        adaptecTest = run_command(firstPath + "/arcconf getconfig 1 LD | grep \"Controllers found: 1\"")
    elif os.path.isdir(secondPath):
        path = secondPath
        adaptecTest = run_command(secondPath + "/arcconf getconfig 1 LD | grep \"Controllers found: 1\"")
    elif os.path.isfile(thirdPath):
        lsiTest = run_command(thirdPath + " /c0 show all | grep \"Status = Success\"")
        run_command("lshw -class disk > /tmp/diskProps.txt")
        run_command("/opt/MegaRAID/storcli/storcli64 -CfgDsply -aALL > /tmp/adapterInfo.txt")

    ssd_devices = find_available_devices(adaptecTest, lsiTest, path)

    module.exit_json(changed=False, ssds=ssd_devices)

# this is magic, see lib/ansible/module_common.py
from ansible.module_utils.basic import *
main()
