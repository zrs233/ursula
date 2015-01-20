#!/bin/bash

# get arguments
while getopts 'k:v:' OPT; do
  case $OPT in
    k) KEY=$OPTARG;;  # ansible_nodename
    v) VALUE=$OPTARG;;  # vagrant
  esac
done

if [[ -z $VALUE ]]; then
  exit 0
fi

HOST=$(hostname)

if [[ $HOST != $NAME ]]; then
  if [[ -n $KEY ]]; then
    echo "hostname (${HOST}) should match ${KEY} (${VALUE})"
  else
    echo "hostname (${HOST}) should be set to ${VALUE}"
  fi
  exit 2
else
  exit 0
fi
