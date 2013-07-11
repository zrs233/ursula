

- install ansible: `./bin/install-ubuntu` or `./bin/install-osx`
- configure some hosts, e.g.: `echo 127.0.0.1 > ~/ansible_hosts`
- point ansible to them: `export ANSIBLE_HOSTS=~/ansible_hosts`
- _or_ put them in /etc/ansible/hosts
- `ansible all -m ping`


# glance image create hangs, manual workaround:

glance image-create --name cirros --disk-format=qcow2 --container-format=bare --is-public=True --is-protected=FTrue --location https://launchpad.net/cirros/trunk/0.3.0/+download/cirros-0.3.0-x86_64-disk.img
