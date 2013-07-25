

# TODO

## make a nice wrapper deployment script

    ansible-playbook -i envs/$ENV/hosts -u root -M ./library playbooks/site.yml
    export ANSIBLE_NOCOWS=1

- fail on a dirty git tree?
- log ansible commands and git status
- use sudo rules to hide ssh key from normal users?
- playbook to set it all up

## split into global/default config and site config


# Bugs

## glance image create times out sometimes

- manual workaround:
    glance image-create --name cirros --disk-format=qcow2 --container-format=bare --is-public=True --is-protected=True --location https://launchpad.net/cirros/trunk/0.3.0/+download/cirros-0.3.0-x86_64-disk.img

## automate configuration of quantum external bridge

## default security group

    neutron security-group-rule-create --direction ingress --protocol tcp --port_range_min 22 --port_range_max 22 UUID
    neutron security-group-rule-create --direction ingress --protocol icmp --port_range_min 0 --port_range_max 0 UUID


## hypervisor type shows as qemu

    `nova hypervisor-show` and horizon show type qemu even though kvm is configured

[see bug here](https://bugs.launchpad.net/nova/+bug/1195361)

## ip forwarding was not enabled on net node by default

it should be set and persisted.

    # test
    sysctl net.ipv4.ip_forward

    # set until reboot
    sysctl -w net.ipv4.ip_forward=1

    # persist
    # TODO


## ovs agent dies on dedicated compute because of no br-ex

br-ex appears in the neutron config, but is not currently installed on compute nodes.

should it be removed from config on compute nodes?

    ovs-vsctl --no-wait -- --may-exist add-br br-ex

## default m1.tiny flavor "root disk" size is too small to boot ubuntu.
