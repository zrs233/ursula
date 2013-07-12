

# TODO

## make a nice wrapper deployment script

    ansible-playbook -i envs/tim/hosts -u root -M ./library playbooks/site.yml


## glance image create times out

- tried setting 'timeout' parameter to glance_image ansible module, but it fails with str/numeric mismatch.
- manual workaround:
    glance image-create --name cirros --disk-format=qcow2 --container-format=bare --is-public=True --is-protected=FTrue --location https://launchpad.net/cirros/trunk/0.3.0/+download/cirros-0.3.0-x86_64-disk.img

## configure quantum external bridge

all nodes running ovs-agent need br-int.
network node needs br-ex.

    ovs-vsctl add-br br-int
    ovs-vsctl add-br br-ex
    ovs-vsctl add-port br-ex eth1

## notifications are not always happening

e.g. pip installs, rootwrap syncs.

## change virt type from qemu to kvm

this may make the below /dev/net/tun thing unncessary.

## /dev/net/tun

issue with precise and ovs:  https://lists.launchpad.net/openstack/msg12269.html

workaround for precise: add /dev/net/tun to cgroup_device_acl in /etc/libvirt/qemu.conf, restart libvirt-bin

## nova metadata is not working

change metadata-ip from dns name to ip in metadata__agent.ini ??

## instances can't access outside network

- default router isn't 'external' by default currently
- default router isn't connected to 'tenants' network

http://docs.openstack.org/trunk/openstack-network/admin/content/l3_workflow.html

## forwarding

- ipv4 forwarding is enabled, but not sure what enabled it.
    cat /proc/sys/net/ipv4/ip_forward

## novnc doesn't work

just run nova-novncproxy after insalling novnc from source, to avoid bogus nova-common dependency:

    #!/bin/bash
    set -ex
    git clone --depth=1 https://github.com/kanaka/noVNC.git /opt/stack/novnc
    install -d -m 0755 -o root -g root /usr/share/novnc
    install -m 0644 -o root -g root /opt/stack/novnc/favicon.ico /usr/share/novnc
    install -m 0644 -o root -g root /opt/stack/novnc/*.html /usr/share/novnc
    install -d -m 0755 -o root -g root /usr/share/novnc/include
    install -m 0644 -o root -g root /opt/stack/novnc/include/*.css /usr/share/novnc/include
    install -m 0644 -o root -g root /opt/stack/novnc/include/*.js /usr/share/novnc/include

## release tool

- accept env name as parameter
- fail on a dirty git tree?
- log ansible commands and git status
- use sudo rules to hide ssh key from normal users?
- playbook to set it all up

## horizon branding

copy over logo.png and logo-splash.ping, but still allow for git pulls.  fork?
