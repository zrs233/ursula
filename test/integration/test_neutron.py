# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright (c) 2013 Blue Box Group
# All Rights Reserved.

import unittest2 as unittest

import unittest_helper as helper


class TestNeutron(unittest.TestCase):
    def setUp(self):
        pass

    def test_has_an_internal_network(self):
        cmd = 'neutron net-list | grep internal'
        helper.run_on_group('controller[0]', cmd)

    def test_has_a_network_with_network_type_gre(self):
        cmd = ('neutron net-show internal '
               '| grep provider:network_type | grep gre')
        helper.run_on_group('controller[0]', cmd)

    def test_has_a_network_with_provider_physical_network_empty(self):
        cmd = ('neutron net-show internal '
               '| grep provider:physical_network')
        helper.run_on_group('controller[0]', cmd)

    def test_has_a_network_with_segmentation_id_256(self):
        cmd = ('neutron net-show internal '
               '| grep provider:segmentation_id | grep 256')
        helper.run_on_group('controller[0]', cmd)

    def test_has_a_network_with_router_external_False(self):
        cmd = ('neutron net-show internal '
               '| grep router:external | grep False')
        helper.run_on_group('controller[0]', cmd)

    def test_has_a_network_with_internal_subnet(self):
        cmd = ('neutron net-list '
               '| grep internal | grep 172.16.255.0/24')
        helper.run_on_group('controller[0]', cmd)

    def test_has_the_internal_subnet(self):
        cmd = 'neutron subnet-list | grep internal'
        helper.run_on_group('controller[0]', cmd)

    def test_has_the_internal_subnet_with_cidr(self):
        cmd = ('neutron subnet-show internal '
               '| grep cidr | grep 172.16.255.0/24')
        helper.run_on_group('controller[0]', cmd)

    def test_has_the_internal_subnet_with_cidr_start_end_addresses(self):
        cmd = ('neutron subnet-show internal '
               '| grep allocation_pools | egrep "172.16.255.2.*172.16.255.254"')  # NOQA
        helper.run_on_group('controller[0]', cmd)

    def test_has_the_internal_subnet_with_dns_nameservers_empty(self):
        cmd = ('neutron subnet-show internal '
               '| grep dns_nameservers')
        helper.run_on_group('controller[0]', cmd)

    def test_has_the_internal_subnet_with_enable_dhcp_True(self):
        cmd = ('neutron subnet-show internal '
               '| grep enable_dhcp | grep True')
        helper.run_on_group('controller[0]', cmd)

    def test_has_the_internal_subnet_with_gateway_gateway_ip(self):
        cmd = ('neutron subnet-show internal '
               '| grep gateway | grep gateway_ip')
        helper.run_on_group('controller[0]', cmd)

    def test_it_has_the_default_router(self):
        cmd = 'neutron router-list | grep default'
        helper.run_on_group('controller[0]', cmd)
