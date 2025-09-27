envsubst '${DOMAIN_NAME}' < /etc/nginx/config/templates/ddclient.conf > /etc/ddclient.conf
ddclient -file /etc/ddclient.conf

envsubst '${CLOUDFLARE_DNS_TOKEN}' < /etc/nginx/config/cloudflare.ini > /etc/letsencrypt/cloudflare.ini

cert_file="/etc/letsencrypt/live/$DOMAIN_NAME/fullchain.pem"
FETCH_CERTIFICATES="${FETCH_CERTIFICATES:-false}"

if [ ! -e "$cert_file" ] || [ "$FETCH_CERTIFICATES" = "true" ]; then
    echo "Starting Nginx on port 80 for cert challenge."
    # Use a temporary config that only serves HTTP for the challenge
    envsubst '${DOMAIN_NAME}' < /etc/nginx/config/templates/certbot.conf > /etc/nginx/conf.d/app.conf

    # Start nginx in the background to handle the challenge
    nginx -g 'daemon on;'

    echo 'Fetching certs.'
    certbot certonly \
        --dns-cloudflare \
        --dns-cloudflare-credentials /etc/letsencrypt/cloudflare.ini \
        -n \
        --agree-tos \
        --non-interactive \
        --expand \
        -v \
        -m $EMAIL \
        -d $DOMAIN_NAME \
        -d *.$DOMAIN_NAME

    # Stop the temporary Nginx daemon
    nginx -s stop
fi


service cron start
# crond
rm -f /etc/nginx/conf.d/app.conf
mkdir /etc/nginx/snippets
envsubst '${DOMAIN_NAME}' < /etc/nginx/config/templates/app.conf > /etc/nginx/conf.d/app.conf
envsubst '${DOMAIN_NAME}' < /etc/nginx/config/templates/ssl.conf > /etc/nginx/snippets/ssl.conf
exec nginx -g 'daemon off;'