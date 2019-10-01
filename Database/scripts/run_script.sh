#!/bin/sh
psql -f $1 -v schema=$2 $DATABASE_URL