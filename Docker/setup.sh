#!/bin/bash

#Set environment variables
set -o allexport
source .env
set +o allexport

#bluetooth
sudo apt install bluez*
modprobe btusb
sudo systemctl enable bluetooth.service
sudo systemctl start bluetooth.service

# Loki
echo "------- Loki ---------"
docker plugin install grafana/loki-docker-driver:latest --alias loki --grant-all-permissions
# Set following in /etc/docker/daemon.json
# {
#     "debug" : true,
#     "log-driver": "loki",
#     "log-opts": {
#         "loki-url": "http://localhost:3100/loki/api/v1/push"
#         "max-size": "30m",
#         "max-file": "3"
#         "keep-file": true
#     }
# }

# # configure influxdb
# echo "------- Inluxdb --------"
# docker exec influxdb influx setup \
#   --bucket $INFLUXDB_BUCKET \
#   --org $INFLUXDB_ORG \
#   --password $INFLUXDB_PASSWORD \
#   --username $INFLUXDB_USERNAME \
#   --force
# # get the token
# echo "token: "
# docker exec influxdb influx auth list | \
# awk -v username=$INFLUXDB_USERNAME '$5 ~ username {print $4 " "}'