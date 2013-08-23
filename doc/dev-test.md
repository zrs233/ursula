
# how-to set up a dev / test environment

This repo comes with scripts to automatically spin up a test environment on openstack vms.

## first-time workstation setup

On your workstation, you'll need:

  - the latest ansible:

```bash
    pip install git+https://github.com/ansible/ansible.git
```

  - nova client:

```bash
    pip install git+https://github.com/openstack/python-novaclient.git
```

  - openstack credentials in `$HOME/.stackrc`:

```bash
    $ cat $HOME/.stackrc
    export OS_USERNAME="example-username"
    export OS_PASSWORD="example-password"
    export OS_TENANT_NAME="example-project-name"
    export OS_AUTH_URL="https://openstack-example-domain.com:35357/v2.0/"
    export SERVICE_TYPE="compute"
```

  - your default security group must have all tcp ports opened up for access. this can be done in horizon (easiest), or with neutron client.

## spin up a new environment

```bash
    ./test/setup       # boot vms and write an ansible inventory to envs/example/hosts
    ./test/run         # run site.yml and run all the tests
```

## iterate on an existing environment

You can save time on iterating by keeping your vms around for multiple ansible runs.

```bash
    ./test/run         # re-run site.yml (much faster this time)
```

## re-run only a subset of tasks

    TODO

## throw away the vms when you're done

```bash
    ./test/cleanup     # delete vms
```
