# LDAP Demo

Run a local ldap server, use docker for speed

Start ursula with ldap support

```
$ bin/run_vagrant ldap
...
...

```


install and setup ldap server:

```
$ apt-get install slapd ldap-utils
$ dpkg-reconfigure slapd
```

* Omit OpenLDAP server configuration? No
* DNS domain name : openstack.org
* Organization name : openstack
* Administrator password : asdf
* Database backend :HDB
* Remove the database when slapd is purged? No
* Move old database? Yes
* Allow LDAPv2 protocol? No

collect the uids of your users, groups, and tenants, and use that data to fill in the following `.ldif` files:

```
$ source /root/stackrc
$ keystone user-list
$ keystone tenant-list
$ keystone role-list
```

Create a openstack ldif file `/tmp/openstack.ldif`

```
dn: ou=Groups,dc=openstack,dc=org
objectClass: top
objectClass: organizationalUnit
ou: groups

dn: ou=Users,dc=openstack,dc=org
objectClass: top
objectClass: organizationalUnit
ou: users

dn: ou=Roles,dc=openstack,dc=org
objectClass: top
objectClass: organizationalUnit
ou: roles
```

Create a openstack users ldif file `/tmp/openstack_users.ldif`

```
# admin, Users, openstack.org
dn: cn=07b505df8a874d54a8c8aaf31a97b61b,ou=Users,dc=openstack,dc=org
cn: admin
cn: 07b505df8a874d54a8c8aaf31a97b61b
mail: admin@example.net
objectClass: inetOrgPerson
objectClass: top
sn: admin
userPassword: asdf

# provider_admin, Users, openstack.org
dn: cn=a4282e6afdf143e78a879aceb943fc49,ou=Users,dc=openstack,dc=org
cn: provider_admin
cn: a4282e6afdf143e78a879aceb943fc49
mail: admin@example.net
objectClass: inetOrgPerson
objectClass: top
sn: admin
userPassword: ghij


# a40d19bc15394032bfaf7fdd7854b2f8, Users, openstack.org
dn: cn=90d5a580e97b49e2830eb7739c3e6abd,ou=Users,dc=openstack,dc=org
cn: neutron
cn: 90d5a580e97b49e2830eb7739c3e6abd
sn: neutron
mail: neutron@example.net
objectClass: inetOrgPerson
objectClass: top
userPassword: asdf

# dd719a26107a4a41b655475083342173, Users, openstack.org
dn: cn=cc899e258af044e6b65e76a72336b8b4,ou=Users,dc=openstack,dc=org
cn: glance
cn: cc899e258af044e6b65e76a72336b8b4
sn: glance
mail: glance@example.net
objectClass: inetOrgPerson
objectClass: top
userPassword: asdf

# d5c0d7a3f48c412e947debfd6f312aff, Users, openstack.org
dn: cn=2ecf3d87e20a444f8b6a1007ceab337a,ou=Users,dc=openstack,dc=org
cn: nova
cn: 2ecf3d87e20a444f8b6a1007ceab337a
sn: nova
mail: nova@example.net
objectClass: inetOrgPerson
objectClass: top

# enabled_users, Users, openstack.org
dn: cn=enabled_users,ou=Users,dc=openstack,dc=org
cn: enabled_users
member: cn=07b505df8a874d54a8c8aaf31a97b61b,ou=Users,dc=openstack,dc=org
member: cn=90d5a580e97b49e2830eb7739c3e6abd,ou=Users,dc=openstack,dc=org
member: cn=cc899e258af044e6b65e76a72336b8b4,ou=Users,dc=openstack,dc=org
member: cn=2ecf3d87e20a444f8b6a1007ceab337a,ou=Users,dc=openstack,dc=org
objectClass: groupOfNames


# admin, Roles, openstack.org
dn: cn=a4d438c679254c6c916974914098d267,ou=Roles,dc=openstack,dc=org
objectClass: organizationalRole
ou: admin
cn: a4d438c679254c6c916974914098d267
description: Openstack admin Role
roleOccupant: cn=02cbaeff65464855913d895d41b72513,ou=Users,dc=openstack,dc=org


# member, Roles, openstack.org
dn: cn=9fe2ff9ee4384b1894a90878d3e92bab,ou=Roles,dc=openstack,dc=org
objectClass: organizationalRole
ou: _member_
cn: 9fe2ff9ee4384b1894a90878d3e92bab
description: Openstack Member Role

# service, Roles, openstack.org
dn: cn=7f6b41e5a5994866a9c6de916d4284d8,ou=Roles,dc=openstack,dc=org
objectClass: organizationalRole
ou: service
cn: 7f6b41e5a5994866a9c6de916d4284d8
description: Openstack Service Role

# admin, Groups, openstack.org
dn: cn=9560afdfbd484a9898f1b37a6311390f,ou=Groups,dc=openstack,dc=org
objectClass: groupOfNames
ou: admin
cn: 9560afdfbd484a9898f1b37a6311390f
description: Openstack admin Groups
member: cn=07b505df8a874d54a8c8aaf31a97b61b,ou=Users,dc=openstack,dc=org
member: cn=a4282e6afdf143e78a879aceb943fc49,ou=Users,dc=openstack,dc=org

# services, Groups, openstack.org
dn: cn=6a22e53f12794f788c6a0a1d9c9f646f,ou=Groups,dc=openstack,dc=org
objectClass: groupOfNames
ou: service
cn: 6a22e53f12794f788c6a0a1d9c9f646f
description: Services
member: cn=90d5a580e97b49e2830eb7739c3e6abd,ou=Users,dc=openstack,dc=org
member: cn=dd719a26107a4a41b655475083342173,ou=Users,dc=openstack,dc=org
member: cn=2ecf3d87e20a444f8b6a1007ceab337a,ou=Users,dc=openstack,dc=org
```

load those files into ldap and then test them:

```
$ ldapadd -x -w asdf -D"cn=admin,dc=openstack,dc=org" -f /tmp/openstack.ldif
$ ldapadd -x -w asdf -D"cn=admin,dc=openstack,dc=org" -f /tmp/openstack_users.ldif
$ slapcat
```

set `keystone.ldap.enabled: True` in `envs/vagrant/ldap/group_vars/all.yml` and rerun the keystone tags:

```
$ bin/run_vagrant ldap --tags=keystone 
```

Check that it works:

*if the user email addresses are @example.net then we're getting the data from keystone*

```
$ grep ldap /etc/keystone/keystone.conf
driver = keystone.identity.backends.ldap.Identity
[ldap]
url=ldap://127.0.0.1
$ keystone user-list
+----------------------------------+----------------+---------+---------------------+
|                id                |      name      | enabled |        email        |
+----------------------------------+----------------+---------+---------------------+
| 07b505df8a874d54a8c8aaf31a97b61b |     admin      |   True  |  admin@example.net  |
| cc899e258af044e6b65e76a72336b8b4 |     glance     |   True  |  glance@example.net |
| 90d5a580e97b49e2830eb7739c3e6abd |    neutron     |   True  | neutron@example.net |
| 2ecf3d87e20a444f8b6a1007ceab337a |      nova      |   True  |   nova@example.net  |
| a4282e6afdf143e78a879aceb943fc49 | provider_admin |   True  |  admin@example.net  |
+----------------------------------+----------------+---------+---------------------+
```
