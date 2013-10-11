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

import unittest2 as unittest

import unittest_helper as helper


class TestNovaCommon(unittest.TestCase):
    def test_contains_a_memcached_servers_flag(self):
        cmd = ('egrep memcached_servers=[0-9.]+:11211,[0-9.]+ '
               '/etc/nova/nova.conf')
        helper.run_on_group('controller[0]', cmd)
