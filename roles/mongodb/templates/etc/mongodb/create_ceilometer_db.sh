#!/bin/bash
changed=1

mongo --host {{ primary_ip }} --eval 'rs.initiate()'
sleep 15
mongo --host {{ primary_ip }} --eval 'cfg=rs.conf(); cfg.members[0].host="{{ primary_ip }}:{{ mongodb.port }}"; rs.reconfig(cfg)'

mongo --host {{ primary_ip }} --eval 'db = db.getSiblingDB("admin"); db.getUser("admin")' | grep  "object" > /dev/null
if [ $? -gt 0 ]
then
  mongo --host {{ primary_ip }} --eval 'db = db.getSiblingDB("admin"); db.createUser({user: "admin", pwd: "{{ mongodb.ceilometer_password }}", roles: [{ role: "userAdminAnyDatabase", db: "admin" }]})'
  mongo --host {{ primary_ip }} --eval 'db = db.getSiblingDB("admin"); db.getUser("admin")' | grep  "object" > /dev/null
  if [ $? -gt 0 ]
  then
    exit 2
  else
    changed=0
  fi
fi

mongo --host {{ primary_ip }} --eval 'db = db.getSiblingDB("{{ mongodb.ceilometer_database }}"); db.getUser("{{ mongodb.ceilometer_user }}")' | grep  "object" > /dev/null
if [ $? -gt 0 ]
then
  mongo --host {{ primary_ip }} --eval 'db = db.getSiblingDB("{{ mongodb.ceilometer_database }}"); db.createUser({user: "{{ mongodb.ceilometer_user }}", pwd: "{{ mongodb.ceilometer_password }}", roles: [ "readWrite", "dbAdmin" ]})'
  mongo --host {{ primary_ip }} --eval 'db = db.getSiblingDB("{{ mongodb.ceilometer_database }}"); db.getUser("{{ mongodb.ceilometer_user }}")' | grep  "object" > /dev/null
  if [ $? -gt 0 ]
  then
    exit 2
  else
    changed=0
  fi
fi

exit $changed

