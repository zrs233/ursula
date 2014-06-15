#!/bin/bash

set -e

function get_vagrant_hosts {
    STATUS=`vagrant status | grep virtualbox | awk '{print $1}'`
    echo ${STATUS}
}

TYPE=$1

if [ -z "${TYPE}" ]; then
    echo "You must specify a type"
    exit -1
fi

if [ "${TYPE}" == "swift" ]; then
    BOXES="controller1 swiftnode1 swiftnode2 swiftnode3"
elif [ "${TYPE}" == "standard" ]; then
    BOXES="controller1 controller2 compute1"
else
    echo "I dont know how to provision '${TYPE}'"
    exit -1
fi

vagrant up --no-provision ${BOXES}

TEMPFILE=`mktemp 2>/dev/null || mktemp -t 'ursula-fifo'`
for I in ${BOXES}; do
    vagrant ssh-config $I >> ${TEMPFILE}
done

export ANSIBLE_SSH_ARGS="${ANSIBLE_SSH_ARGS} -F ${TEMPFILE}"
./bin/ursula envs/vagrant/${TYPE} site.yml -s -u vagrant
rm ${TEMPFILE}
