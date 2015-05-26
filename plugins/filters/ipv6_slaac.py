
import netaddr
from ansible import errors

# Returns the SLAAC address within a network for a given HW/MAC address.
# Usage:
#
#  - prefix | slaac(mac)
def _slaac(prefix, mac):
    ''' Get the SLAAC address within given network '''
    try:
        eui = netaddr.EUI(mac)
    except:
        raise errors.AnsibleFilterError('slaac: not a hardware address: %s' % mac)

    try:
        ip = netaddr.IPNetwork(prefix)
    except:
        raise errors.AnsibleFilterError('slaac: not an recognized address: %s' % prefix)

    if ip.version != 6:
        raise errors.AnsibleFilterError('slaac: not an IPv6 address: %s' % str(ip))

    return eui.ipv6(ip.network)


class FilterModule(object):
    def filters(self):
        return { 'slaac': _slaac }
