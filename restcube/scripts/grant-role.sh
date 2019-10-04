#! /usr/bin/env bash

set -e

datacube system init

PGPASSWORD=$ADMIN_PASSWORD psql -h $DB_HOSTNAME -p $DB_PORT -U $ADMIN_USERNAME -d postgres <<-SQL
GRANT agdc_admin TO "$DB_USERNAME";
SQL

