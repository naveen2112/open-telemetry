# Base image: nginx version nginx/1.23.1
FROM public.ecr.aws/nginx/nginx:1.23.1
# Install dependencies
RUN apt-get update -qq && apt-get -y install apache2-utils curl build-essential

# establish where Nginx should look for files\
ENV FLASK_ROOT=/var/app

# Set our working directory inside the image
WORKDIR $FLASK_ROOT

ADD docker/web/http_webserver.conf /app/http_webserver.conf
ADD docker/web/https_webserver.conf /app/https_webserver.conf

ADD docker/web/nginx.conf /etc/nginx/nginx.conf

#Log Config
RUN ln -sf /dev/stdout /var/log/nginx/access.log \
    && ln -sf /dev/stderr /var/log/nginx/error.log

# add permissions
RUN chown -R www-data:www-data /var && chmod -R 755 /var && \
    chown -R www-data:www-data /etc/nginx && chmod -R 755 /etc/nginx

ADD docker/web/entrypoint.sh /usr/bin/
RUN chmod +x /usr/bin/entrypoint.sh
ENTRYPOINT ["entrypoint.sh"]

USER www-data

EXPOSE 80

# Use the "exec" form of CMD so Nginx shuts down gracefully on SIGTERM (i.e. `docker stop`)
CMD [ "nginx", "-g", "daemon off;" ]