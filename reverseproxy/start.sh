#!/bin/sh
sed -e "s/{{REVERSE_PROXY_PORT}}/$REVERSE_PROXY_PORT/g" /etc/nginx/nginx.tpl > /etc/nginx/nginx.conf
sed -i -e "s/{{WEB_HOST}}/$WEB_HOST/g" /etc/nginx/nginx.conf
sed -i -e "s/{{WEB_PORT}}/$WEB_PORT/g" /etc/nginx/nginx.conf

sed -i -e "s/{{API_CLUSTER_STATUS_HOST}}/$API_CLUSTER_STATUS_HOST/g" /etc/nginx/nginx.conf
sed -i -e "s/{{API_CLUSTER_STATUS_PORT}}/$API_CLUSTER_STATUS_PORT/g" /etc/nginx/nginx.conf
sed -i -e "s/{{API_FOUNDATION_HOST}}/$API_FOUNDATION_HOST/g" /etc/nginx/nginx.conf
sed -i -e "s/{{API_FOUNDATION_PORT}}/$API_FOUNDATION_PORT/g" /etc/nginx/nginx.conf
sed -i -e "s/{{API_EULA_HOST}}/$API_EULA_HOST/g" /etc/nginx/nginx.conf
sed -i -e "s/{{API_EULA_PORT}}/$API_EULA_PORT/g" /etc/nginx/nginx.conf
sed -i -e "s/{{API_SETUP_HOST}}/$API_SETUP_HOST/g" /etc/nginx/nginx.conf
sed -i -e "s/{{API_SETUP_PORT}}/$API_SETUP_PORT/g" /etc/nginx/nginx.conf
sed -i -e "s/{{API_POWER_HOST}}/$API_POWER_HOST/g" /etc/nginx/nginx.conf
sed -i -e "s/{{API_POWER_PORT}}/$API_POWER_PORT/g" /etc/nginx/nginx.conf
sed -i -e "s/{{API_BULK_HOST}}/$API_BULK_HOST/g" /etc/nginx/nginx.conf
sed -i -e "s/{{API_BULK_PORT}}/$API_BULK_PORT/g" /etc/nginx/nginx.conf

echo "======="
cat /etc/nginx/nginx.conf
echo "======="

exec nginx -g "daemon off;"