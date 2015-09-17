#!/usr/bin/python
#coding: utf-8 -*-

DOCUMENTATION = """
---
author: Michael Sambol
module: ceph_pool
short_description: Creates ceph pool and ensures correct pg count
description:
  There are three possible outcomes:
    1/ Create a new pool if it doesn't exist
    2/ Set the pool's pg count to correct number
    3/ Nothing: pool is created and pg count is correct
options:
  pool_name:
    description:
      - The pool in question: create it or ensure correct pg count
    required: true
"""

EXAMPLES = """
# ceph_pool can only be run on nodes that have an admin keyring
# pool_name = default
- ceph_pool:
    pool_name: default
  register: pool_output
  run_once: true
  delegate_to: "{{ groups[ceph.monitor_group_name][0] }}"
"""

import time


def increase_pg_count(module, osds, pool_name,
                      current_pg_count, desired_pg_count):
    max_increase_per_pass = osds * 32
    diff = desired_pg_count - current_pg_count

    while diff > 0:
        if diff <= max_increase_per_pass:
            cmd = ['ceph', 'osd', 'pool', 'set', pool_name,
                   'pg_num', str(desired_pg_count)]
            rc, out, err = module.run_command(cmd, check_rc=True)
            # needs at least 10 seconds or the second command will fail
            time.sleep(10)
            cmd = ['ceph', 'osd', 'pool', 'set', pool_name,
                   'pgp_num', str(desired_pg_count)]
            rc, out, err = module.run_command(cmd, check_rc=True)
            diff = 0
        else:
            current_pg_count = current_pg_count + max_increase_per_pass
            cmd = ['ceph', 'osd', 'pool', 'set', pool_name,
                   'pg_num', str(current_pg_count)]
            rc, out, err = module.run_command(cmd, check_rc=True)
            # needs at least 10 seconds or the second command will fail
            time.sleep(10)
            cmd = ['ceph', 'osd', 'pool', 'set', pool_name,
                   'pgp_num', str(current_pg_count)]
            rc, out, err = module.run_command(cmd, check_rc=True)
            diff = diff - max_increase_per_pass


def main():
    module = AnsibleModule(
        argument_spec=dict(
            pool_name=dict(required=True),
        ),
    )

    pool_name = module.params.get('pool_name')

    # determine number of osds in cluster
    cmd = ['ceph', 'osd', 'stat']
    rc, out, err = module.run_command(cmd, check_rc=True)
    ## Example
    # out.splitlines()[0] = "osdmap e1564: 9 osds: 9 up, 9 in"
    # osds = 9
    osds = int(out.splitlines()[0].split(":")[1].strip().split(" ")[0])

    # calculate desired pg count
    # 100 is a constant and 3 is the number of copies
    # read more about pg count here: http://ceph.com/pgcalc/
    total_pg_count = (osds * 100) / 3
    i = 0
    desired_pg_count = 0
    while desired_pg_count < total_pg_count:
        desired_pg_count = 2**i
        i += 1

    # does the pool exist already?
    cmd = ['ceph', 'osd', 'pool', 'get', pool_name, 'pg_num']
    rc, out, err = module.run_command(cmd, check_rc=False)

    # no
    if rc != 0:
        # create the pool
        cmd = ['ceph', 'osd', 'pool', 'create', pool_name,
               str(desired_pg_count), str(desired_pg_count)]
        rc, out, err = module.run_command(cmd, check_rc=True)
        module.exit_json(changed=True, msg="new pool was created")
    # yes
    else:
        # does the current pg count match the desired pg count?
        ## Example
        # out.splitlines()[0] = "pg_num: 256"
        # current_pg_count = 256
        current_pg_count = int(out.splitlines()[0].split(":")[1].strip())
        # no
        if current_pg_count < desired_pg_count:
            increase_pg_count(module, osds, pool_name,
                              current_pg_count, desired_pg_count)
            module.exit_json(changed=True, msg="pool's pg count was changed")
        # yes
        else:
            module.exit_json(changed=False)

from ansible.module_utils.basic import *
main()
