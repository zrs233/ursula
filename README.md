# ursula

Ansible playbooks for operating OpenStack.

# installation

```bash
git clone git@github.com:blueboxgroup/ursula.git
cd ursula
sudo bin/install-ubuntu || sudo bin/install-osx
```

# prerequisites

You have some hosts running ubuntu 12.04, and you can ssh to them from your workstation.

# setup

create a new environment, keep it somewhere outside this repo:

    cp envs/example /your/env

add your hosts to the inventory:

    $editor /your/new/env/hosts


# basic usage

```bash
# run the main playbook to install and configure all the things
./bin/ursula /your/new/env playbooks/site.yml
```

# envs

An environment consists of two things:
- `hosts`: a host inventory
- `group_vars`: a directory of env-specific vars

To create a new env, copy the example env directory, and edit it to suit your needs:

```bash
cp -r envs/example /some/private/dir
# edit /some/private/dir/hosts, /some/private/dir/group_vars/all.yml
```

# detailed documentation

See the `/doc` directory of this repo.
