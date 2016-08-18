#!/bin/bash -xe

source /root/stackrc

install_rally() {
    attempt=1
    until [[ $attempt == ${RALLY_MAX_RETRY} ]]; do
        curl ${RALLY_INSTALL_URL} | bash -s -- -y -d rally
        if [[ -d rally ]]; then
            break
        else
            attempt=$[$attempt + 1]
            sleep ${RALLY_RETRY_SLEEP}
        fi
    done

    if [[ ! -d rally ]]; then
        echo "Could not install rally.  Check your connection?"
        exit 1
    fi
}

BUILD_TAG=${1:-master}
RALLY=rally/bin/rally
RALLY_INSTALL_URL=https://raw.githubusercontent.com/openstack/rally/master/install_rally.sh
RALLY_FILE=bbc-cloud-validate
RALLY_TEST_IMAGE="cirros"
RALLY_TEST_NET_ID=$(nova network-list | awk '/internal/{print $2}')
RALLY_TEST_VCPU_LIMIT=4
RALLY_MAX_RETRY=4
RALLY_RETRY_SLEEP=5

install_rally

cat << EOF > rally_args.yaml
---
image_name: ${RALLY_TEST_IMAGE}
net_id: ${RALLY_TEST_NET_ID}
vcpu_limit: ${RALLY_TEST_VCPU_LIMIT}
EOF

${RALLY} deployment create --fromenv --name=${BUILD_TAG}
${RALLY} task start bbc-cloud-validate.yml --task-args-file rally_args.yaml
${RALLY} task report --out=rally_report.html
