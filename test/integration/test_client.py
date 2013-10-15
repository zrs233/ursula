# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright (c) 2013 Blue Box Group
# All Rights Reserved.

import unittest2 as unittest

import unittest_helper as helper


class TestClient(unittest.TestCase):
    def test_has_a_os_cacert_env_variable(self):
        cmd = 'grep OS_CACERT=/opt/stack/ssl/openstack.crt /root/stackrc'
        helper.run_on_group('controller', cmd)
