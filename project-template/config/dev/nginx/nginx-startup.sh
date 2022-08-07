#!/bin/bash

if [ -f /dev-config/nginx-local.crt ];then
    # User has specified a cert, use that
    cp /dev-config/nginx-local.crt /etc/nginx/site.crt
    cp /dev-config/nginx-local.key /etc/nginx/site.key
elif [ ! -e /etc/nginx/site.crt ];then
    # Build a self signed key
    openssl req -x509 -newkey rsa:2048 -keyout /etc/nginx/site.key -out /etc/nginx/site.crt -sha256 -nodes -subj "/C=AU/ST=VIC/L=Melbourne/O=github-com-splondike/OU=Org/CN=app.localtest.me" -days 3650
else
    # Nothing to do, we already have a cert
    true
fi

exec nginx -g 'daemon off;'
