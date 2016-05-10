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

def _get_group_id(client, group_name):
   for group in client.groups.list():
       if group.name == group_name:
           return group.id
   return None

def _get_domain_id(client, domain_name):
    for domain in client.domains.list():
        if domain.name == domain_name:
            return domain.id
    return None

def _get_project_id(client, project_name):
    for project in client.projects.list():
        if project.name == project_name:
            return project.id
    return None

def _get_role_id(client, role_name):
    for role in client.roles.list():
        if role.name == role_name:
            return role.id
    return None

def _add_role_to_group(client, group_name, project_name, role, domain):
    
    domain_id = None
    if domain:
        domain_id = _get_domain_id(client, domain)
        if not domain_id:
            raise Exception("domain %s not found" % domain)
    role_id = None
    if role:
        role_id = _get_role_id(client, role)
        if not role_id:
            raise Exception("role %s not found" % role)
    client.roles
    project_id = None
    if project_name:
        project_id = _get_project_id(client, project_name)
        if not project_id:
            raise Exception("project %s not found" % project_name)
    group_id = None
    if group_name:
        group_id = _get_group_id(client, group_name)
        if not group_id:
            raise Exception("group %s not found" % group_name)

    if project_id:     
        client.roles.grant(role=role_id, project=project_id, group=group_id)
    else:
        client.roles.grant(role_id, domain=domain_id, group=group_id)       

def main():

    module = AnsibleModule(
        argument_spec=dict(
            auth_url=dict(default=None, required=True),
            username=dict(default=None, required=True),
            password=dict(default=None, required=True),
            project_name_to_auth=dict(default=None, required=True),
            domain_name_to_auth=dict(default=None, required=True),
            verify=dict(default=True, type='bool', required=False),
            group=dict(default=None, required=True),
            role=dict(default=None, required=True),
            project=dict(default=None, required=False),
            domain=dict(default=None, required=False),
            state=dict(default='present', required=False,
                       choices=['present', 'absent']),
        )
    )

    changed = False
    result = None
    action = "Adding" if module.params['state'] == 'present' else ""
    try:
        keystone = Client(auth_url=module.params['auth_url'],
                          username=module.params['username'],
                          password=module.params['password'],
                          verify=module.params['verify'],
                          project_name=module.params['project_name_to_auth'],
                          project_domain_name=module.params['domain_name_to_auth'])

        if module.params['state'] == 'present':
            params = {
                'client': keystone,
                'group_name': module.params['group'],
                'project_name': module.params['project'],
                'role': module.params['role'],
                'domain': module.params['domain']
            }
            _add_role_to_group(**params)
            changed = True
            result = 'added'
    except Exception as e:
        module.fail_json(msg="%s role failed: %s" % (action, e))

    module.exit_json(changed=changed, result=result, id=module.params['group'])


# this is magic, see lib/ansible/module_common.py
from ansible.module_utils.basic import *

main()
