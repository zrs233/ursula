# Setting up a new OpenStack

This document describes at a high level the steps required to set up a new OpenStack cluster using this tool.


## Hardware Provisioning

* Select machines to serve as controller (1), network (1), and compute (N) nodes.
* Image all nodes with Ubuntu 12.04 (Precise)
* For each compute node:
    * Ensure KVM virtualization is enabled in the BIOS. (this can be checked from the running host): `apt-get install cpu-checker; kvm-ok`
    * If not enabled, enter BIOS settings and enable "Intel Virtualization Techonology"
* Ensure SSH access to all machines as root or a sudoer, either directly or through a bastion using ssh_config.

## Networking / Routing

* Provision a public ipv4 subnet, and route it to the network node

    ip route $PUBLIC_SUBNET $NETWORK_NODE_IP name $NAME


## Ansible Installation

    TODO

## Configuration

    TODO

## Deployment

    TODO
