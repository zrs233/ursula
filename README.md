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

Ursula comes bundled with Vagrant hooks to get started.  see [docs/vagrant.md](docs/vagrant.md) for using it.

# Basic Usage

```bash
# run the main playbook to install and configure all the things
ursula /your/new/env site.yml
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

# support for proxy servers

There are a few attributes that allow you to use a proxy server in several different ways.

### Enable proxy only during the ansible run

This sets the `http_proxy` environment variable in `/etc/environment` for the duration of the ansible run.

`common.ansible_proxy: http://10.230.7.181:3128`

### Set proxy during ansible run and leave it there

This sets the `http_proxy` environment variable in `/etc/environment` but does not remove it like the above.

`common.global_proxy: http://10.230.7.181:3128`

### Enable proxy only for APT

This sets your proxy only for apt repositories:

`common.apt_cache: http://10.230.7.181:3128`


# Dev/Test Environment Running on VMs

Please see [this doc](https://github.com/blueboxgroup/ursula/blob/master/doc/dev-test.md) for more information on getting started.

# More Docs

See the `/doc` directory of this repo.
