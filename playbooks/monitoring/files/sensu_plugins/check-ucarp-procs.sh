#!/bin/bash
grep ucarp-vip /etc/network/interfaces | awk '{print $2}' | while read ip; do
  if ! ps -ef | grep '/usr/sbin/ucarp' | grep $ip >/dev/null; then
    echo "no ucarp process is running for ip $ip"
    exit 2
  fi
done
