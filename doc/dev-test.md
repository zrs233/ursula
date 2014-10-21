# How to set up a dev/test environment

NOTE: Ursula comes setup for Vagrant to complete dev/test work within.  Please see the [Ursula Vagrant](https://github.com/blueboxgroup/ursula#vagrant) instructions for more details.

Ursula also comes with scripts to automatically spin up a test environment inside of openstack vms (OpenStack on OpenStack).

## First-time workstation setup

Confirm that you have followed the [installation instructions for ursula](https://github.com/blueboxgroup/ursula#installation), it should have installed the required packages:

  - Ansible
  - Nova client
  - Keystone client
  - Neutron client
  - Glance client
  - Cinder client

  - openstack credentials in `$HOME/.stackrc` (t):

```bash
    $ cat $HOME/.stackrc
    export OS_USERNAME="example-username"
    export OS_PASSWORD="example-password"
    export OS_TENANT_NAME="example-project-name"
    export OS_AUTH_URL="https://openstack-example-domain.com:35357/v2.0/"
    export SERVICE_TYPE="compute"
```
## Spin up a new environment

```bash
    $ ./test/setup       # boot vms and write an ansible inventory to envs/example/hosts
    $ ./test/run         # run site.yml and run all the tests
```

## Iterate on an existing environment

You can save time on iterating by keeping your vms around for multiple ansible runs.

```bash
    $ ./test/run         # re-run site.yml (much faster this time)
```

## Re-run only a subset of tasks

    TODO

## Throw away the vms when you're done

```bash
    $ ./test/cleanup     # delete vms
```
