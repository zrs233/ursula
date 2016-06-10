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


def _find_identity_provider(client, attribute, value):
    for provider in client.federation.identity_providers.list():
        if getattr(provider, attribute) == value:
            return provider
    return None


def _identity_provider_exists(client, provider_id):
    return _find_identity_provider(client, 'id', provider_id) != None


def _create_identity_provider(client, provider_id, description=None,
                              remote_ids=[], enabled=True):
    client.federation.identity_providers.create(id=provider_id,
                                                description=description,
                                                remote_ids=remote_ids,
                                                enabled=enabled)


def _delete_identity_provider(client, provider_id):
    provider = _find_identity_provider(client, 'id', provider_id)
    client.federation.identity_providers.delete(identity_provider=provider)


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
            remote_ids=dict(default=None, type='list', required=False),
            enabled=dict(default=True, type='bool', required=False),
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
            if not _identity_provider_exists(keystone, module.params['name']):
                remote_ids = module.params['remote_ids']

                params = {
                    'client': keystone,
                    'provider_id': module.params['name'],
                    'description': module.params['description'],
                    'remote_ids': remote_ids,
                    'enabled': module.params['enabled']
                }
                _create_identity_provider(**params)
                changed = True
                result = 'created'
        else:
            if _identity_provider_exists(keystone, module.params['name']):
                _delete_identity_provider(keystone, module.params['name'])
                changed = True
                result = 'deleted'
    except Exception as e:
        module.fail_json(msg="%s identity provider failed: %s" % (action, e))

    module.exit_json(changed=changed, result=result, id=module.params['name'])


# this is magic, see lib/ansible/module_common.py
from ansible.module_utils.basic import *

main()
