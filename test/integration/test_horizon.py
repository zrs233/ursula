# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright (c) 2013 Blue Box Group
# All Rights Reserved.

import unittest2 as unittest

import unittest_helper as helper


class TestHorizon(unittest.TestCase):
    def test_contains_memcached_servers(self):
        cmd = ("egrep \\'[0-9.]+:11211\\',\\'[0-9]+ "
               '/opt/stack/horizon/openstack_dashboard/local/local_settings.py')
        helper.run_on_group('controller', cmd)
