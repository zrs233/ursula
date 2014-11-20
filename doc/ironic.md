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
=====

Create Flavor
--------------------

```
$ nova flavor-create baremetal auto 4096 40 2
$ nova flavor-key baremetal set cpu_arch=x86_64
```

Get DIB and built Ubuntu Images
------------------------------------------------

```
$ git clone https://github.com/openstack/diskimage-builder.git
$ cd diskimage-builder
$ python setup.py develop
$ bin/disk-image-create -u ubuntu -o my-image
$ bin/disk-image-get-kernel -d ./ -o my -i $(pwd)/my-image.qcow2
$ bin/ramdisk-image-create ubuntu deploy-ironic -o my-deploy-ramdisk
```

Load into glance
------------------------

```
glance image-create --name my-kernel --public \
--disk-format aki  < my-vmlinuz

glance image-create --name my-ramdisk --public \
--disk-format ari  < my-initrd

glance image-create --name my-image --public \
--disk-format qcow2 --container-format bare --property \
kernel_id=$MY_VMLINUZ_UUID --property \
ramdisk_id=$MY_INITRD_UUID < my-image.qcow2

glance image-create --name deploy-vmlinuz --public \
--disk-format aki < my-deploy-ramdisk.kernel

glance image-create --name deploy-initrd --public \
--disk-format ari < my-deploy-ramdisk.initramfs
```

Initiate Bare Metal Node
-----------------------------------

```
export node_options="\
-i deploy_kernel=$MY_VMLINUZ_UUID \
-i deploy_ramdisk=$MY_INITRD_UUID \
-i ssh_virt_type=virsh \
-i ssh_address=$IP \
-i ssh_port=22 \
-i ssh_username=ubuntu \
-i ssh_key_filename=/root/int-test.pem"

chassis_id=$(ironic chassis-create -d "ironic test chassis" | grep " uuid " | awk -F'|' '{ print $3 }')

node_id=$(ironic node-create --chassis_uuid $chassis_id \
--driver agent_ssh \
-p cpus=2 \
-p memory_mb=4906 \
-p local_gb=40 \
-p cpu_arch=x86_64 \
$node_options \
| grep " uuid " | grep " uuid " | awk -F'|' '{ print $3 }')

nova boot --flavor baremetal --image my-image loltest --nic net-id=162d0320-9350-4b63-9416-64e3bb2fd376
```
