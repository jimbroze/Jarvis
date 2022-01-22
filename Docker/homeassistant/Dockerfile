FROM ghcr.io/home-assistant/home-assistant:stable

RUN [ ! -e /etc/nsswitch.conf ] && echo 'hosts: files dns' > /etc/nsswitch.conf