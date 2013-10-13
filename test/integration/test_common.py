# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright (c) 2013 Blue Box Group
# All Rights Reserved.

import unittest2 as unittest

import unittest_helper as helper


class TestCommon(unittest.TestCase):
    def test_system_time_is_utc(self):
        helper.run_on_group('all',
                            'grep Etc/UTC /etc/timezone')
        helper.run_on_group('all',
                            'date | grep UTC')
