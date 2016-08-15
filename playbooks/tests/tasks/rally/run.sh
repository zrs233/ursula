#!/bin/bash

DIR=`pwd`

sudo -s -u root
source /root/stackrc

BUILD_TAG=${1:-master}
RALLY=${DIR}/rally/bin/rally
RALLY_INSTALL_URL=https://raw.githubusercontent.com/openstack/rally/master/install_rally.sh
RALLY_FILE=bbc-cloud-validate
RALLY_TEST_IMAGE="cirros"
RALLY_TEST_NET_ID=$(openstack network show internal -c id -f value)
RALLY_TEST_VCPU_LIMIT=4

read -r -d '' RALLY_TASK_ARGS <<EOM
{"image_name": "${RALLY_TEST_IMAGE}",
 "net_id": "${RALLY_TEST_NET_ID}",
 "vcpu_limit": "${RALLY_TEST_VCPU_LIMIT}"}
EOM

curl ${RALLY_INSTALL_URL} | bash -s -- -y -d ${DIR}/rally

${RALLY} deployment create --fromenv --name=${BUILD_TAG}
${RALLY} task start ${DIR}/bbc-cloud-validate.yml --task-args ${RALLY_TASK_ARGS}
${RALLY} task report --out=${DIR}/${BUILD_TAG}_rally_report.html
