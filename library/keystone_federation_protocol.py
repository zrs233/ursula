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


def _get_identity_provider(client, identity_provider_id):
    for idp in client.federation.identity_providers.list():
        if idp.id == identity_provider_id:
            return idp
    return None


def _get_mapping(client, mapping_id):
    for mapping in client.federation.mappings.list():
        if mapping.id == mapping_id:
            return mapping
    return None


def _get_federation_protocol(client, protocol_id, identity_provider):
    for protocol in client.federation.protocols.list(identity_provider):
        if protocol.id == protocol_id:
            return protocol
    return None


def _federation_protocol_exists(client, protocol_id, identity_provider_id):
    identity_provider = _get_identity_provider(client, identity_provider_id)
    rc = _get_federation_protocol(client, protocol_id, identity_provider)
    return rc != None


def _create_federation_protocol(client, protocol_id, identity_provider_id,
                                mapping_id):
    identity_provider = _get_identity_provider(client, identity_provider_id)
    mapping = _get_mapping(client, mapping_id)
    client.federation.protocols.create(protocol_id=protocol_id,
                                       identity_provider=identity_provider,
                                       mapping=mapping)


def _delete_federation_protocol(client, protocol_id, identity_provider_id):
    identity_provider = _get_identity_provider(client, identity_provider_id)
    protocol = _get_federation_protocol(client, protocol_id, identity_provider)
    client.federation.protocols.delete(identity_provider=identity_provider,
                                       protocol=protocol)


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
            identity_provider=dict(default=None, required=True),
            mapping=dict(default=None, required=True),
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
                          project_name=module.params['project_name_to_auth'],
                          project_domain_name=module.params['domain_name_to_auth'],
                          verify=module.params['verify'])
        idp = module.params['identity_provider']

        if module.params['state'] == 'present':
            if not _federation_protocol_exists(keystone,
                                               module.params['name'], idp):
                params = {
                    'client': keystone,
                    'protocol_id': module.params['name'],
                    'identity_provider_id': module.params['identity_provider'],
                    'mapping_id': module.params['mapping']
                }
                _create_federation_protocol(**params)
                changed = True
                result = 'created'
        else:
            if _federation_protocol_exists(keystone, module.params['name'],
                                           idp):
                _delete_federation_protocol(keystone, module.params['name'],
                                            idp)
                changed = True
                result = 'deleted'
    except Exception as e:
        module.fail_json(msg="%s federation protocol failed: %s" % (action, e))

    module.exit_json(changed=changed, result=result, id=module.params['name'])


# this is magic, see lib/ansible/module_common.py
from ansible.module_utils.basic import *

main()
