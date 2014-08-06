# Ursula

Ursula provides a series of Ansible playbooks for installing, managing and maintaining OpenStack powered clouds.

Ursula was originally created by a team at [Blue Box](https://www.bluebox.net) and is released under the MIT License (MIT).

# Installation

```bash
git clone git@github.com:blueboxgroup/ursula.git
cd ursula
sudo bin/install-ubuntu || sudo bin/install-osx
```

# Pre-Requisites

Ursula requires that you have access to a minimum of 3 hosts running ubuntu 12.04, and you can ssh to them from your workstation.

# Setup

Create a new environment, keep it somewhere outside this repo:

    cp envs/example /your/env

Add your hosts to the inventory:

    $editor /your/new/env/hosts

# Getting Started

Ursula comes bundled with Vagrant hooks to get started.  Once you've installed the pre-requesite software, you can get up and running with:

```
./bin/run_vagrant.sh
```

# Basic Usage

```bash
# run the main playbook to install and configure all the things
./bin/ursula /your/new/env site.yml
```

# Environments

An environment consists of two things:
- `hosts`: a host inventory
- `group_vars`: a directory of env-specific vars

To create a new env, copy the example env directory, and edit it to suit your needs:

```bash
cp -r envs/example /some/private/dir
# edit /some/private/dir/hosts, /some/private/dir/group_vars/all.yml
```

# Dev/Test Environment Running on VMs

Please see [this doc](https://github.com/blueboxgroup/ursula/blob/master/doc/dev-test.md) for more information on getting started.

# More Docs

See the `/doc` directory of this repo.