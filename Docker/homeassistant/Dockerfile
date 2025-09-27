FROM ghcr.io/home-assistant/home-assistant:stable

# RUN [ ! -e /etc/nsswitch.conf ] && echo 'hosts: files dns' > /etc/nsswitch.conf

RUN apt-get update && apt-get -y install cron

ADD cron-jobs /etc/cronjob

RUN crontab /etc/cron.d/cron-jobs
 
CMD cron && tail -f /var/log/cron.log