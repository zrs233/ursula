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
    print("failed=True msg='keystoneclient and pyyaml are required'")


def _get_federation_mapping(client, mapping_id):
    for mapping in client.federation.mappings.list():
        if mapping.id == mapping_id:
            return mapping
    return None


def _federation_mapping_exists(client, mapping_id):
    return _get_federation_mapping(client, mapping_id) != None


def _create_federation_mapping(client, mapping_id, rules):
    client.federation.mappings.create(mapping_id=mapping_id, rules=rules)


def _delete_federation_mapping(client, mapping_id):
    mapping = _get_federation_mapping(client, mapping_id)
    client.federation.mappings.delete(mapping=mapping)


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
            rules=dict(default=None, type='list', required=False),
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
            if not _federation_mapping_exists(keystone,
                                              module.params['name']):
                params = {
                    'client': keystone,
                    'mapping_id': module.params['name'],
                    'rules': module.params['rules']
                }
                _create_federation_mapping(**params)
                changed = True
                result = 'created'
        else:
            if _federation_mapping_exists(keystone, module.params['name']):
                _delete_federation_mapping(keystone, module.params['name'])
                changed = True
                result = 'deleted'
    except Exception as e:
        module.fail_json(msg="%s federation mapping failed: %s" % (action, e))

    module.exit_json(changed=changed, result=result, id=module.params['name'])


# this is magic, see lib/ansible/module_common.py
from ansible.module_utils.basic import *

main()
