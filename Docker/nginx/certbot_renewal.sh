certbot renew
# service nginx stop
# certbot certonly --standalone -n --agree-tos -m $EMAIL -d $SUBDOMAIN.$DOMAIN -d www.$SUBDOMAIN.$DOMAIN
# service nginx start