FROM influxdb:latest
RUN apt-get update -y && apt-get install -y cron
COPY crontab /etc/cron.d/crontab
RUN chmod 0644 /etc/cron.d/crontab &&\
    crontab /etc/cron.d/crontab
COPY backup.sh /backup.sh
COPY init.sh /init.sh
ENTRYPOINT ["bash", "/init.sh"]
