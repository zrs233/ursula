# ursula

Ansible playbooks for operating OpenStack.

# installation

```bash
git clone git@github.com:blueboxgroup/ursula.git
cd ursula
sudo bin/install-ubuntu || sudo bin/install-osx
```

# basic usage

```bash
# run the main playbook on a host inventory file
ans /path/to/env
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
