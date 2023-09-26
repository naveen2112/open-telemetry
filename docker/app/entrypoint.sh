#!/bin/sh

set -e
     python manage.py migrate --noinput
     cp -r /var/app/copystaticfiles/* /var/app/staticfiles/
exec "$@"