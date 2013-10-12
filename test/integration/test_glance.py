# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright (c) 2013 Blue Box Group
# All Rights Reserved.

import unittest2 as unittest

import unittest_helper as helper


class TestGlance(unittest.TestCase):
    def test_has_the_cirros_image(self):
        helper.run_on_group('controller[0]',
                            'glance index | grep cirros')
