# LDAP Demo

Start ursula with ldap support:

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
* DNS domain name : openstack.example.org
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
dn: ou=Groups,dc=openstack,dc=example,dc=org
objectClass: top
objectClass: organizationalUnit
ou: groups

dn: ou=Users,dc=openstack,dc=example,dc=org
objectClass: top
objectClass: organizationalUnit
ou: users

dn: ou=Roles,dc=openstack,dc=example,dc=org
objectClass: top
objectClass: organizationalUnit
ou: roles
```

Create a openstack users ldif file `/tmp/openstack_users.ldif`

```
# admin, Users, openstack.example.org
dn: cn=<ADMIN_USER_ID>,ou=Users,dc=openstack,dc=example,dc=org
cn: <ADMIN_USER_ID>
mail: admin@openstack.example.org
objectClass: inetOrgPerson
objectClass: top
sn: admin
userPassword: asdf

# provider_admin, Users, openstack.example.org
dn: cn=<PROVIDER_ADMIN_USER_ID>,ou=Users,dc=openstack,dc=example,dc=org
cn: <PROVIDER_ADMIN_USER_ID>
mail: admin@openstack.example.org
objectClass: inetOrgPerson
objectClass: top
sn: provider_admin
userPassword: ghij


# neutron, Users, openstack.example.org
dn: cn=<NEUTRON_USER_ID>,ou=Users,dc=openstack,dc=example,dc=org
cn: <NEUTRON_USER_ID>
sn: neutron
mail: neutron@openstack.example.org
objectClass: inetOrgPerson
objectClass: top
userPassword: asdf

# glance, Users, openstack.example.org
dn: cn=<GLANCE_USER_ID>,ou=Users,dc=openstack,dc=example,dc=org
cn: <GLANCE_USER_ID>
sn: glance
mail: glance@openstack.example.org
objectClass: inetOrgPerson
objectClass: top
userPassword: asdf

# nova, Users, openstack.example.org
dn: cn=<NOVA_USER_ID>,ou=Users,dc=openstack,dc=example,dc=org
cn: <NOVA_USER_ID>
sn: nova
mail: nova@openstack.example.org
objectClass: inetOrgPerson
objectClass: top

# enabled_users, Users, openstack.example.org
dn: cn=enabled_users,ou=Users,dc=openstack,dc=example,dc=org
cn: enabled_users
member: cn=<PROVIDER_ADMIN_USER_ID>,ou=Users,dc=openstack,dc=example,dc=org
member: cn=<ADMIN_USER_ID>,ou=Users,dc=openstack,dc=example,dc=org
member: cn=<NEUTRON_USER_ID>,ou=Users,dc=openstack,dc=example,dc=org
member: cn=<GLANCE_USER_ID>,ou=Users,dc=openstack,dc=example,dc=org
member: cn=<NOVA_USER_ID>,ou=Users,dc=openstack,dc=example,dc=org
objectClass: groupOfNames


# admin, Roles, openstack.example.org
dn: cn=<ADMIN_ROLE_ID>,ou=Roles,dc=openstack,dc=example,dc=org
objectClass: organizationalRole
ou: admin
cn: <ADMIN_ROLE_ID>
description: Openstack admin Role
roleOccupant: cn=02cbaeff65464855913d895d41b72513,ou=Users,dc=openstack,dc=example,dc=org


# member, Roles, openstack.example.org
dn: cn=<MEMBER_ROLE_ID>,ou=Roles,dc=openstack,dc=example,dc=org
objectClass: organizationalRole
ou: _member_
cn: <MEMBER_ROLE_ID>
description: Openstack Member Role

# service, Roles, openstack.example.org
dn: cn=<SERVICE_RROLE_ID>,ou=Roles,dc=openstack,dc=example,dc=org
objectClass: organizationalRole
ou: service
cn: <SERVICE_RROLE_ID>
description: Openstack Service Role

# admin, Groups, openstack.example.org
dn: cn=<ADMIN_GROUP_ID>,ou=Groups,dc=openstack,dc=example,dc=org
objectClass: groupOfNames
ou: admin
cn: <ADMIN_GROUP_ID>
description: Openstack admin Groups
member: cn=<ADMIN_USER_ID>,ou=Users,dc=openstack,dc=example,dc=org
member: cn=<PROVIDER_ADMIN_USER_ID>,ou=Users,dc=openstack,dc=example,dc=org

# services, Groups, openstack.example.org
dn: cn=<SERVICES_GROUP_ID>,ou=Groups,dc=openstack,dc=example,dc=org
objectClass: groupOfNames
ou: service
cn: <SERVICES_GROUP_ID>
description: Services
member: cn=<NEUTRON_USER_ID>,ou=Users,dc=openstack,dc=example,dc=org
member: cn=dd719a26107a4a41b655475083342173,ou=Users,dc=openstack,dc=example,dc=org
member: cn=<NOVA_USER_ID>,ou=Users,dc=openstack,dc=example,dc=org
```

load those files into ldap and then test them:

```
$ ldapadd -x -w asdf -D"cn=admin,dc=openstack,dc=example,dc=org" -f /tmp/openstack.ldif
$ ldapadd -x -w asdf -D"cn=admin,dc=openstack,dc=example,dc=org" -f /tmp/openstack_users.ldif
$ slapcat
```

set `keystone.ldap.enabled: True` in `envs/vagrant/ldap/group_vars/all.yml` and rerun the keystone tags:

```
$ bin/run_vagrant ldap --tags=keystone 
```

Check that it works:

*if the user email addresses are @openstack.example.org then we're getting the data from keystone*

```
$ grep ldap /etc/keystone/keystone.conf
driver = keystone.identity.backends.ldap.Identity
[ldap]
url=ldap://127.0.0.1
$ keystone user-list
+----------------------------------+----------------+---------+---------------------+
|                id                |      name      | enabled |        email        |
+----------------------------------+----------------+---------+---------------------+
| <ADMIN_USER_ID> |     admin      |   True  |  admin@openstack.example.org  |
| <GLANCE_USER_ID> |     glance     |   True  |  glance@openstack.example.org |
| <NEUTRON_USER_ID> |    neutron     |   True  | neutron@openstack.example.org |
| <NOVA_USER_ID> |      nova      |   True  |   nova@openstack.example.org  |
| <PROVIDER_ADMIN_USER_ID> | provider_admin |   True  |  admin@openstack.example.org  |
+----------------------------------+----------------+---------+---------------------+
```
