#!/bin/bash

# Define the Nginx configuration file path
nginx_conf="/etc/nginx/conf.d/ssl_main.conf"

# Let Nginx serve the docker container running on port 8080 instead of a static web page
sed -i 's|root /var/www/html;|location \/ {\n    error_page 401 = @custom_401;\n    auth_request /validate;\n    auth_request_set $username $upstream_http_username;\n    proxy_set_header remote_user $username;\n    \tproxy_pass http:\/\/localhost:8080;\n    \tproxy_set_header Host $host;\n    \tproxy_set_header X-Real-IP $remote_addr;\n    }|' "$nginx_conf"
sed -i 's|index index.html index.htm;||' "$nginx_conf"

systemctl restart nginx.service
