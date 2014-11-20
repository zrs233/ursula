Ursula on Vagrant
=================

Vagrant is an excellent tool for easily testing out new tools or systems without having to install a bunch of crap to your userland.

Prerequistites
==============

* Virtualbox
* Vagrant
* Ansible ( 1.7ish )

Using
=====

Vagrant can be used to stand up three types of environments:  allinone, standard, swift.

Do not use `vagrant up` directly we have wrapped a tool around it called `./bin/run_vagrant`.

The `run_vagrant` tool will bootstrap and provision your nodes in three steps.

1. It runs vagrant up on the required machines described in the Vagrantfile.
2. It runs `ursula` against the nodes to provision openstack.
3. It does any final post-provisioning steps required.

allinone
--------

This will stand up a single monolithic Openstack VM.  It's much quicker than standard, but sacrifices HA and multi-node:

```
$ ./bin/run_vagrant allinone
```

standard
--------

This will stand up two controllers and a compute node.  It includes all the appropriate HA pieces and is a fairly good facsimile of a production install:

```
$ ./bin/run_vagrant standard
```

swift
-----

This will stand up a multi-node swift cluster:

```
$ ./bin/run_vagrant swift
```
