FROM nginx:latest
RUN apt-get update && apt-get install -y cron && apt-get install -y certbot
COPY crontab /etc/cron.d/crontab
RUN chmod 0644 /etc/cron.d/crontab &&\
    crontab /etc/cron.d/crontab
ARG SUBDOMAIN
ARG DOMAIN
COPY init.sh /certbot/init.sh
COPY certbot_renewal.sh /certbot/certbot_renewal.sh
# COPY config/app.conf /etc/nginx/conf.d/app.conf
RUN curl -s https://raw.githubusercontent.com/certbot/certbot/master/certbot-nginx/certbot_nginx/_internal/tls_configs/options-ssl-nginx.conf > /certbot/options-ssl-nginx.conf
RUN openssl dhparam -out /certbot/ssl-dhparams.pem 2048
ENTRYPOINT ["bash", "/certbot/init.sh"]
