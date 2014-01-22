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

import collections
import yaml

from ansible.constants import DEFAULTS, get_config, load_config_file
from ansible.inventory.vars_plugins.group_vars import VarsModule \
    as GroupVarsModule
import ansible.inventory as inventory
import ansible.utils as utils

def deep_update_dict(d, u):
    for k, v in u.iteritems():
        if isinstance(v, collections.Mapping):
            r = deep_update_dict(d.get(k, {}), v)
            d[k] = r
        else:
            d[k] = u[k]
    return d


class VarsModule(GroupVarsModule):

    def init(self, inventory):
        super(VarsModule, self).__init__(inventory)

    def _get_defaults(self):
        p = load_config_file()
        defaults_file = get_config(p, DEFAULTS, 'var_defaults_file',
                                   'ANSIBLE_VAR_DEFAULTS_FILE', None)
        if defaults_file:
            return yaml.load(open(defaults_file))

    def run(self, host):
        default_vars = self._get_defaults()
        group_vars = super(VarsModule, self).run(host)
        if default_vars:
            return deep_update_dict(default_vars, group_vars)
        return group_vars


def monkeypatch_get_variables(self, hostname):
    host = self.get_host(hostname)
    if host is None:
        raise errors.AnsibleError("host not found: %s" % hostname)

    vars = {}
    vars_results = [ plugin.run(host) for plugin in self._vars_plugins ]
    for updated in vars_results:
        if updated is not None:
            vars = utils.combine_vars(vars, updated)

    vars = utils.combine_vars(vars, host.get_variables())
    if self.parser is not None:
        vars = utils.combine_vars(vars, self.parser.get_host_variables(host))
    return vars

inventory.Inventory._get_variables = monkeypatch_get_variables
