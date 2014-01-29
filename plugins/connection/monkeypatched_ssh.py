# -*- coding: utf-8 -*-
# (c) 2014, Craig Tracey <craigtracey@gmail.com>
#
# This module is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This software is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this software.  If not, see <http://www.gnu.org/licenses/>.

# We need to monkeypatch ssh for Vagrant because of this bug in Ansible:
# https://github.com/ansible/ansible/pull/5732

import ansible.constants as constants
from ansible.runner.connection_plugins.ssh import Connection as SSHConnection


def monkeypatch_get_config(p, section, key, env_var, default, boolean=False,
                           integer=False, floating=False):
    ''' return a configuration variable with casting '''
    value = constants._get_config(p, section, key, env_var, default)
    if boolean:
        return contants.mk_boolean(value)
    if value and integer:
        return int(value)
    if value and floating:
        return float(value)
    return value

constants.get_config = monkeypatch_get_config
constants.DEFAULT_REMOTE_PORT = constants.get_config(constants.p,
                                                     constants.DEFAULTS,
                                                     'remote_port',
                                                     'ANSIBLE_REMOTE_PORT',
                                                     None, integer=True)


class Connection(SSHConnection):
    pass
