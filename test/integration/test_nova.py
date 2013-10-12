# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright (c) 2013 Blue Box Group
# All Rights Reserved.

import unittest2 as unittest

import unittest_helper as helper


class TestNova(unittest.TestCase):
    def test_has_a_working_nova_api(self):
        helper.run_on_group('controller[0]',
                            'nova list | grep ID')
