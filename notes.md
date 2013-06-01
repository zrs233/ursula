

- install ansible: `./bootstrap`
- configure some hosts, e.g.: `echo 127.0.0.1 > ~/ansible_hosts`
- point ansible to them: `export ANSIBLE_HOSTS=~/ansible_hosts`
- _or_ put them in /etc/ansible/hosts
- `ansible all -m ping`
