FROM nginx:latest

RUN apt-get update && \
    apt-get install -y cron python3 python3-dev python3-venv libaugeas-dev gcc curl perl libdata-validate-ip-perl libjson-any-perl automake autoconf make && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install Certbot
RUN python3 -m venv /opt/certbot/ && \
    /opt/certbot/bin/pip install --upgrade pip && \
    /opt/certbot/bin/pip install certbot certbot-dns-cloudflare && \
    ln -s /opt/certbot/bin/certbot /usr/bin/certbot

RUN mkdir /certbot && \
    curl -s https://raw.githubusercontent.com/certbot/certbot/master/certbot-nginx/certbot_nginx/_internal/tls_configs/options-ssl-nginx.conf > /certbot/options-ssl-nginx.conf && \
    openssl dhparam -out /certbot/ssl-dhparams.pem 2048

# Install DDClient for Dynamic DNS updates
RUN curl -L -o /tmp/ddclient-4.0.0.tar.gz https://github.com/ddclient/ddclient/archive/refs/tags/v4.0.0.tar.gz && \
    cd /tmp && tar xvfa ddclient-4.0.0.tar.gz && \
    cd ddclient-4.0.0 && \
    ./autogen && \
    ./configure \
    --prefix=/usr \
    --sysconfdir=/etc \
    --localstatedir=/var && \
    make && \
    make install

# COPY crontab /etc/cron.d/crontab
RUN touch /etc/cron.d/crontab && \
    chmod 0644 /etc/cron.d/crontab && \
    crontab /etc/cron.d/crontab && \
    echo "0 0,12 * * * root /opt/certbot/bin/python -c 'import random; import time; time.sleep(random.random() * 3600)' && certbot renew -q" | tee -a /etc/cron.d/crontab > /dev/null

ARG SUBDOMAIN
ARG DOMAIN
ARG DOMAIN_NAME
ARG EMAIL

COPY init.sh /certbot/init.sh
COPY certbot_renewal.sh /certbot/certbot_renewal.sh

ENTRYPOINT ["bash", "/certbot/init.sh"]
