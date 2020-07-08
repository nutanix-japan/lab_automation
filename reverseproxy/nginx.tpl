user  nginx;
worker_processes  1;
error_log  /var/log/nginx/error.log warn;
pid        /var/run/nginx.pid;
events {
  worker_connections  1024;
}

http {
  include       /etc/nginx/mime.types;
  default_type  application/octet-stream;
  log_format  main  '$remote_addr - $remote_user [$time_local] "$request" '
                    '$status $body_bytes_sent "$http_referer" '
                    '"$http_user_agent" "$http_x_forwarded_for"';
  access_log  /var/log/nginx/access.log  main;
  sendfile        on;
  keepalive_timeout  65;

  server{
    listen {{REVERSE_PROXY_PORT}};
    server_name nginx;

    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-Host $host;
    proxy_set_header X-Forwarded-Server $host;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;

    location / {
      proxy_pass http://{{WEB_HOST}}:{{WEB_PORT}};
    }

    location /api/private/ {
      return 403;
    }
    
    location /api/public/cluster/v1/ {
      proxy_pass http://{{API_CLUSTER_STATUS_HOST}}:{{API_CLUSTER_STATUS_PORT}};
    }

    location /api/public/foundation/v1/ {
      proxy_pass http://{{API_FOUNDATION_HOST}}:{{API_FOUNDATION_PORT}};
    }

    location /api/public/eula/v1/ {
      proxy_pass http://{{API_EULA_HOST}}:{{API_EULA_PORT}};
    }
    
    location /api/public/setup/v1/ {
      proxy_pass http://{{API_SETUP_HOST}}:{{API_SETUP_PORT}};
    }

    location /api/public/power/v1/ {
      proxy_pass http://{{API_POWER_HOST}}:{{API_POWER_PORT}};
    }

    location /api/public/bulkactions/v1/ {
      proxy_pass http://{{API_BULK_HOST}}:{{API_BULK_PORT}};
    }
  }
}
