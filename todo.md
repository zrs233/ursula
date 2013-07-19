

# TODO

## new deploy

ds489 - ✓ controller
ds669 - ✓ compute
ds590 - ✓ network (should really be compute) - has power info
ds482 - NEED POWER INFO, check raid+VT+networking
ds483 - NEED POWER INFO, check raid+VT+networking

## make a nice wrapper deployment script

    ansible-playbook -i envs/tim/hosts -u root -M ./library playbooks/site.yml

## ubuntu image(s)

## store config in seperate repo

## split into global/default config and site config

## glance image create times out sometimes

- tried setting 'timeout' parameter to glance_image ansible module, but it fails with str/numeric mismatch.
- manual workaround:
    glance image-create --name cirros --disk-format=qcow2 --container-format=bare --is-public=True --is-protected=FTrue --location https://launchpad.net/cirros/trunk/0.3.0/+download/cirros-0.3.0-x86_64-disk.img

## automate configuration of quantum external bridge

## default security group

    neutron security-group-rule-create --direction ingress --protocol tcp --port_range_min 22 --port_range_max 22 UUID    neutron security-group-rule-create --direction ingress --protocol icmp --port_range_min 0 --port_range_max 0 UUID

## change virt type from qemu to kvm

this may make the below /dev/net/tun thing unncessary.

## /dev/net/tun

issue with precise and ovs:  https://lists.launchpad.net/openstack/msg12269.html

workaround for precise: add /dev/net/tun to cgroup_device_acl in /etc/libvirt/qemu.conf, restart libvirt-bin

## release tool

- accept env name as parameter
- fail on a dirty git tree?
- log ansible commands and git status
- use sudo rules to hide ssh key from normal users?
- playbook to set it all up

