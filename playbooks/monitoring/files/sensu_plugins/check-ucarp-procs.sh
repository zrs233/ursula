#!/bin/bash

ifquery --list | \
while read IFACE; do
  ifquery ${IFACE} | \
  awk '/^ucarp-vip:/ {print $2}' | \
  while read VIP; do
    if ! ps -ef | grep '/usr/sbin/ucarp' | grep ${VIP} >/dev/null; then
      echo "no ucarp process is running for IP ${VIP}"
      exit 2
    fi
  done
done
