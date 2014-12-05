Using Ironic on the Ursula Stack
====================

Bootstrapping
---------------------

set the following in your `envs/ENVIRONMENT/defaults.yml`:

```
ironic:
  enabled: True
```

and then launch Ursula in the regular way.


Testing
=======

Vagrant and Vbox power driver
-----------------------------

Create a ssh key-pair on the vagrant box:

```
$ ssh-keygen -f /var/lib/ironic/key -N '' && \
   chown ironic:ironic /var/lib/ironic/key && \
   cat /var/lib/ironic/key.pub
```

and copy the public key into `~/.ssh/authorized_keys` on your host machine and then make sure you can ssh back into your host from inside vagrant `ssh <username>@10.0.2.2`.

Create a VM in virtualbox with:
* 512mb RAM, 21Gb disk, 1 CPU.
* change boot order to Network, HDD
* set network to be the same as allinone's adapter 3.
* Set MAC to 080027A03A50


Create Flavor
-------------

```
$ nova flavor-create baremetal auto 512 21 1 && \
    nova flavor-key baremetal set cpu_arch=x86_64
```

Get DIB and built Ubuntu Images
------------------------------------------------

```
$ git clone https://github.com/openstack/diskimage-builder.git && \
  cd diskimage-builder && \
  python setup.py develop && \
  bin/disk-image-create -u ubuntu -o ubuntu && \
  bin/disk-image-get-kernel -d ./ -o ubuntu -i $(pwd)/ubuntu.qcow2 && \
  bin/ramdisk-image-create ubuntu deploy-ironic -o ubuntu-deploy-ramdisk
```

Load into glance
------------------------

```
#!/bin/bash
export MY_VMLINUZ_UUID=$(glance image-create --name ubuntu-kernel \
  --disk-format aki --is-public=true < ubuntu-vmlinuz \
   | grep id | awk -F'|' '{print $3}' | sed 's/\s//g')

export MY_INITRD_UUID=$(glance image-create --name ubuntu-ramdisk \
  --disk-format ari --is-public=true < ubuntu-initrd \
   | grep id | awk -F'|' '{print $3}' | sed 's/\s//g')

glance image-create --name ubuntu-image  \
  --disk-format qcow2 --container-format bare \
  --property kernel_id=${MY_VMLINUZ_UUID} \
  --property ramdisk_id=${MY_INITRD_UUID} \
   --is-public=true < ubuntu.qcow2

export DEPLOY_VMLINUZ_UUID=$(glance image-create --name deploy-vmlinuz \
--disk-format aki  --is-public=true < ubuntu-deploy-ramdisk.kernel\
   | grep id | awk -F'|' '{print $3}' | sed 's/\s//g')

export DEPLOY_INITRD_UUID=$(gglance image-create --name deploy-initrd \
--disk-format ari  --is-public=true < ubuntu-deploy-ramdisk.initramfs\
   | grep id | awk -F'|' '{print $3}' | sed 's/\s//g')

```

Initiate Bare Metal Node
-----------------------------------

```
export SSHUSER=<username on host>
export MAC=08:00:27:A0:3A:50
export node_options="\
-i pxe_deploy_kernel=$DEPLOY_VMLINUZ_UUID \
-i pxe_deploy_ramdisk=$DEPLOY_INITRD_UUID \
-i ssh_virt_type=vbox \
-i ssh_address=10.0.2.2 \
-i ssh_port=22 \
-i ssh_username=$SSHUSER \
-i ssh_key_filename=/var/lib/ironic/key"

node_id=$(ironic node-create \
--driver pxe_ssh \
-p cpus=1 \
-p memory_mb=512 \
-p local_gb=20 \
-p cpu_arch=x86_64 \
$node_options \
| grep " uuid " | grep " uuid " | awk -F'|' '{ print $3 }')

ironic port-create --address ${MAC} --node_uuid $node_id

nova boot --flavor baremetal --image ubuntu-image loltest
```
