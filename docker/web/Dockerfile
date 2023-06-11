# Base image: nginx version nginx/1.23.1
FROM public.ecr.aws/nginx/nginx:1.23.1
#FROM nginx:1.23.1

# Install dependencies
RUN apt-get update -qq && apt-get -y install apache2-utils curl build-essential

# RUN wget https://www.python.org/ftp/python/3.10.9/Python-3.10.9.tgz 
# RUN tar xzf Python-3.10.9.tgz 
# RUN cd Python-3.10.9
# RUN ./configure --enable-optimizations 
# RUN make altinstall

# establish where Nginx should look for files\
ENV HUBBLE_ROOT=/var/app

# Set our working directory inside the image
WORKDIR $HUBBLE_ROOT

ADD docker/web/webserver.conf /etc/nginx/conf.d/default.conf

ADD docker/web/nginx.conf /etc/nginx/nginx.conf

RUN mkdir -p /var/app/staticfiles

#Log Config
RUN ln -sf /dev/stdout /var/log/nginx/access.log \
    && ln -sf /dev/stderr /var/log/nginx/error.log

ADD docker/web/entrypoint.sh /usr/bin/
RUN chmod +x /usr/bin/entrypoint.sh
ENTRYPOINT ["entrypoint.sh"]

EXPOSE 80

# Use the "exec" form of CMD so Nginx shuts down gracefully on SIGTERM (i.e. `docker stop`)
CMD [ "nginx", "-g", "daemon off;" ]