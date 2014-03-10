#!/bin/bash

if lspci | grep RAID | grep -i 3ware >> /dev/null; then
   sudo /etc/sensu/plugins/check_3ware_raid.py -b /usr/sbin/tw-cli
fi;
