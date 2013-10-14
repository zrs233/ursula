# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright (c) 2013 Blue Box Group
# All Rights Reserved.

import unittest2 as unittest

import unittest_helper as helper


class TestNovaCommon(unittest.TestCase):
    def test_contains_a_memcached_servers_flag(self):
        cmd = ('egrep \\#memcached_servers=[0-9.]+:11211,[0-9.]+ '
               '/etc/nova/nova.conf')
        helper.run_on_group('controller', cmd)
