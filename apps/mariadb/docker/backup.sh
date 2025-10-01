#!/bin/bash
mysqldump --user=${MARIADB_USER} --password=${MARIADB_PASSWORD} --lock-tables --all-databases > /backup/dbs.sql