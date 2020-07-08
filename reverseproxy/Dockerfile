From nginx:1.17.5-alpine
COPY ./start.sh /usr/local/bin/start.sh
RUN chmod +x /usr/local/bin/start.sh
COPY ./nginx.tpl /etc/nginx/nginx.tpl
CMD ["/usr/local/bin/start.sh"]