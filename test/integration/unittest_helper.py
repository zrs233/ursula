# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright 2013 Blue Box Group
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import os
import subprocess


def run_on_group(group, command):
    """
    Runs the given command on the provided ansible group.

    :param group: A string containing the ansible group.
    :param command: A string containing the command to run.
    :returns: A list of _run_command returns
    """
    hosts = _get_ansible_hosts(group)
    ssh_args = ' '.join(('-o LogLevel=quiet',
                         '-o StrictHostKeyChecking=no',
                         '-o UserKnownHostsFile=/dev/null',
                         '-o ControlMaster=auto',
                         '-o ControlPath=~/.ssh/ursula-%l-%r@%h:%p',
                         '-o ControlPersist=yes',
                         '-i ~/.ssh/int-test.pem'))
    return_list = []
    for host in hosts:
        cmd = "ssh {0} root@{1} 'source /root/stackrc; {2}'".format(ssh_args,
                                                                    host,
                                                                    command)
        result = _run_command(cmd)
        return_list.append(result)
    return return_list


def _run_command(command):
    """
    Runs the given command.

    :param command: A string containing the command to run.
    :returns: Raises subprocess.CalledProcessError if the command's
              return code was non-zero, otherwise returns a string.
    """
    return subprocess.check_output(command, shell=True)


def _get_ansible_hosts(group):
    """
    Obtain a list of hosts in the given ansible group.

    :param group: A string containing the ansible group.
    :returns: A list
    """
    root = os.path.dirname(__file__)
    inventory = os.path.join(root, '../' '../', 'envs', 'test', 'hosts')
    cmd = 'ansible -i {0} --list-hosts {1}'.format(inventory, group)
    output = _run_command(cmd)
    return [line.strip() for line in output.split('\n') if line]
