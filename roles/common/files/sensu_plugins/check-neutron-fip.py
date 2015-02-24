#!/usr/bin/env python
#
# Check OpenStack Neutron API Status
# ===
#
# Dependencies
# -----------
# - python-neutronclient and related libraries
#
# Performs API query to get usage of neutron
# floating IPs
#
# Author: Paul Czarkowski (pczarkowski@bluebox.net)
# Significantly based on existing openstack checks found
# in https://github.com/sensu/sensu-community-plugins
#
# Released under the same terms as Sensu (the MIT license);
# see LICENSE for details.

# #RED
import sys
import argparse
import logging
import os

from neutronclient.neutron import client

STATE_OK = 0
STATE_WARNING = 1
STATE_CRITICAL = 2
STATE_UNKNOWN = 3

logging.basicConfig(level=logging.INFO)
#logging.basicConfig(level=logging.DEBUG)

parser = argparse.ArgumentParser(description='Check OpenStack Neutron API status')

parser.add_argument('-u', '--user', default=os.environ['OS_USERNAME'])
parser.add_argument('-p', '--password', default=os.environ['OS_PASSWORD'])
parser.add_argument('-t', '--tenant', default=os.environ['OS_TENANT_NAME'])
parser.add_argument('-a', '--auth-url', default=os.environ['OS_AUTH_URL'])
parser.add_argument('-w', '--warn', default=10, type=int)
parser.add_argument('-c', '--crit', default=1, type=int)
args = parser.parse_args()

try:
    c = client.Client('2.0',
                      username=args.user,
                      tenant_name=args.tenant,
                      password=args.password,
                      auth_url=args.auth_url)
    fips_obj = c.list_floatingips()
    fips = fips_obj['floatingips']
    if len(fips) == 0:
        print "OK - no floating ips are configured on this openstack."
        sys.exit(STATE_OK)
    count_used_fips = 0
    count_free_fips = 0
    for fip in fips:
        if fip['fixed_ip_address']:
            count_used_fips += 1
        else:
            count_free_fips += 1

except Exception as e:
    print str(e)
    sys.exit(STATE_CRITICAL)

if count_free_fips < args.crit:
    exit_state = STATE_CRITICAL
    state_string = "CRITICAL"
elif count_free_fips < args.warn:
    exit_state = STATE_WARNING
    state_string = "WARNING"
else:
    exit_state = STATE_OK
    state_string = "OK"
#print "something something: {fips_str}".format(fips_str=fips['floatingips'])
print "{state_str} - {free} available floating ip(s) out of {fips}".format(state_str=state_string, free=count_free_fips, fips=len(fips))
sys.exit(exit_state)
