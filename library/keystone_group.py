#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright 2016, IBM
# Copyright 2016, Craig Tracey <craigtracey@gmail.com>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

try:
    from keystoneclient.v3.client import Client
except ImportError:
    print("failed=True msg='keystoneclient is required'")


def _get_domain_id(client, domain_name):
    for domain in client.domains.list():
        if domain.name == domain_name:
            return domain.id
    return None


def _group_exists(client, group_name):
    for group in client.groups.list():
        if group.name == group_name:
            return True
    return False


def _create_group(client, group_name, description=None, domain=None):
    domain_id = None
    if domain:
        domain_id = _get_domain_id(client, domain)
        if not domain_id:
            raise Exception("domain %s not found" % domain)

    client.groups.create(name=group_name, description=description,
                         domain=domain_id)


def _delete_group(client, group_name):
    group = None
    for group in client.groups.list():
        if group.name == group_name:
            group = group
    client.groups.delete(group=group)


def main():

    module = AnsibleModule(
        argument_spec=dict(
            auth_url=dict(default=None, required=True),
            username=dict(default=None, required=True),
            password=dict(default=None, required=True),
            project_name_to_auth=dict(default=None, required=True),
            domain_name_to_auth=dict(default=None, required=True),
            verify=dict(default=True, type='bool', required=False),
            name=dict(default=None, required=True),
            description=dict(default=None, required=False),
            domain=dict(default=None, required=False),
            state=dict(default='present', required=False,
                       choices=['present', 'absent']),
        )
    )

    changed = False
    result = None
    action = "Creating" if module.params['state'] == 'present' else "Deleting"
    try:
        keystone = Client(auth_url=module.params['auth_url'],
                          username=module.params['username'],
                          password=module.params['password'],
                          verify=module.params['verify'],
                          project_name=module.params['project_name_to_auth'],
                          project_domain_name=module.params['domain_name_to_auth'])

        if module.params['state'] == 'present':
            if not _group_exists(keystone, module.params['name']):
                params = {
                    'client': keystone,
                    'group_name': module.params['name'],
                    'description': module.params['description'],
                    'domain': module.params['domain']
                }
                _create_group(**params)
                changed = True
                result = 'created'
        else:
            if _group_exists(keystone, module.params['name']):
                _delete_group(keystone, module.params['name'])
                changed = True
                result = 'deleted'
    except Exception as e:
        module.fail_json(msg="%s group failed: %s" % (action, e))

    module.exit_json(changed=changed, result=result, id=module.params['name'])


# this is magic, see lib/ansible/module_common.py
from ansible.module_utils.basic import *

main()
