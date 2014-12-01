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

Create a ssh key-pair on the vagrant box with `$ ssh-keygen`, store the private key in `/tmp/id_rsa` owned by the `ironic` user and copy the public key into `~/.ssh/authorized_keys` on your host machine and then make sure you can ssh back into your host from inside vagrant `ssh <username>@10.0.2.2`.

Create a VM in virtualbox with:
* 512mb RAM, 21Gb disk, 1 CPU.
* change boot order to Network, HDD
* set network to be the same as allinone's adapter 3.
* get a copy of the MAC



Create Flavor
-------------

```
$ nova flavor-create baremetal auto 512 21 1
$ nova flavor-key baremetal set cpu_arch=x86_64
```

Get DIB and built Ubuntu Images
------------------------------------------------

```
#!/bin/sh
git clone https://github.com/openstack/diskimage-builder.git
cd diskimage-builder
python setup.py develop
bin/disk-image-create -u ubuntu -o ubuntu
bin/disk-image-get-kernel -d ./ -o ubuntu -i $(pwd)/ubuntu.qcow2
bin/ramdisk-image-create ubuntu deploy-ironic -o ubuntu-deploy-ramdisk
```

Load into glance
------------------------

```
#!/bin/bash
export MY_VMLINUZ_UUID=$(glance image-create --name ubuntu-kernel --public \
  --disk-format aki  < ubuntu-vmlinuz \
   | grep id | awk -F'|' '{print $3}' | sed 's/\s//g')

export MY_INITRD_UUID=$(glance image-create --name ubuntu-ramdisk --public \
  --disk-format ari  < ubuntu-initrd \
   | grep id | awk -F'|' '{print $3}' | sed 's/\s//g')

glance image-create --name ubuntu-image --public \
  --disk-format qcow2 --container-format bare \
  --property kernel_id=${MY_VMLINUZ_UUID} \
  --property ramdisk_id=${MY_INITRD_UUID} < ubuntu.qcow2

glance image-create --name deploy-vmlinuz --public \
--disk-format aki < ubuntu-deploy-ramdisk.kernel

glance image-create --name deploy-initrd --public \
--disk-format ari < ubuntu-deploy-ramdisk.initramfs
```

Initiate Bare Metal Node
-----------------------------------

```
e=<username on host>
MAC=<MAC of ironic node>
export node_options="\
-i deploy_kernel=$MY_VMLINUZ_UUID \
-i deploy_ramdisk=$MY_INITRD_UUID \
-i ssh_virt_type=vbox \
-i ssh_address=10.0.2.2 \
-i ssh_port=22 \
-i ssh_username=$SSHUSER \
-i ssh_key_filename=/tmp/id_rsa"

chassis_id=$(ironic chassis-create -d "ironic test chassis" | grep " uuid " | awk -F'|' '{ print $3 }')

node_id=$(ironic node-create --chassis_uuid $chassis_id \
--driver agent_ssh \
-p cpus=1 \
-p memory_mb=512 \
-p local_gb=20 \
-p cpu_arch=x86_64 \
$node_options \
| grep " uuid " | grep " uuid " | awk -F'|' '{ print $3 }')

ironic port-create --address ${MAC} --node_uuid $node_id

nova boot --flavor baremetal --image ubuntu-image loltest
```
