
echo url="https://www.duckdns.org/update?domains=${SUBDOMAIN}&token=${TOKEN}&ip=" | curl -v -k -K -

cert_file="/etc/letsencrypt/live/$SUBDOMAIN.$DOMAIN/privkey.pem"
if [ ! -e "$cert_file" ]; then
    echo 'No certificates found. Fetching certs.'
    certbot certonly --standalone -n --agree-tos -m $EMAIL -d $SUBDOMAIN.$DOMAIN -d www.$SUBDOMAIN.$DOMAIN 
fi

service cron start
# crond
envsubst '${DOMAIN} ${SUBDOMAIN}' < /etc/nginx/conf.d/app.conf.template > /etc/nginx/conf.d/app.conf
nginx -g 'daemon off;'