#!/bin/bash

service cron start
# crond

/bin/bash /entrypoint.sh influxd