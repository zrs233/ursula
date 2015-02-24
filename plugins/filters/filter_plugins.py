def ursula_controller_ips(hostvars, groups, controller_name='controller'):
    controller_ips = set()
    for host in groups[controller_name]:
        controller_primary_interface = hostvars[host]['primary_interface']
        ip = hostvars[host][controller_primary_interface]['ipv4']['address']
        controller_ips.add(ip)
    return sorted(list(controller_ips))
       

def ursula_memcache_hosts(hostvars, groups, memcache_port, controller_name='controller'):
    controller_ips = ursula_controller_ips(hostvars, groups, controller_name)
    host_strings = ['%s:%s' % (c, memcache_port) for c in controller_ips]
    return ','.join(host_strings)


class FilterModule(object):
    ''' ursula utility filters '''

    def filters(self):
        return {
            'ursula_controller_ips': ursula_controller_ips,
            'ursula_memcache_hosts': ursula_memcache_hosts
        }
