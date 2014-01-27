#!/bin/bash
# This script drops all expired entries from the keystone.token table.
# This is necessary, because otherwise the number of tokens would grow without bound.
# Intended to be run periodically by cron.

/usr/bin/mysql -e "delete from keystone.token where expires < now();"
