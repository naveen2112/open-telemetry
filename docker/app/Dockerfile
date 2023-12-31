# Base image: python version python/3.10.9
FROM public.ecr.aws/docker/library/python:3.10.9
# FROM python:3.10.9

# Declared Environment Variables
ENV HUBBLE_ROOT=/var/app
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

ARG AUTHORITY_SIGN_ON_SIGN_OUT
ARG CLIENT_ID
ARG CLIENT_SECRET
ARG DATABASE_URL
ARG DEBUG
ARG ENV_NAME
ARG REDIRECT_PATH
ARG SECRET_KEY
ARG SESSION_TYPE
ARG TEAMS_LOGGING_WEBHOOK_URL

# Set working directory, where the commands will be ran:
RUN mkdir -p $HUBBLE_ROOT
WORKDIR $HUBBLE_ROOT

ADD poetry.lock poetry.lock
ADD pyproject.toml pyproject.toml

# Adding Packages
RUN pip install poetry==1.3.2
RUN poetry config virtualenvs.create false
RUN poetry install --no-interaction --no-ansi --no-root --no-dev

# Adding project files
ADD . .
RUN mkdir -p /var/app/session_files
RUN mkdir -p /var/app/staticfiles
RUN mkdir -p /var/app/copystaticfiles
RUN python manage.py collectstatic --noinput --clear

RUN cp -r /var/app/staticfiles/* /var/app/copystaticfiles/

ADD docker/app/entrypoint.sh /usr/bin/
RUN chmod +x /usr/bin/entrypoint.sh
ENTRYPOINT ["entrypoint.sh"]

EXPOSE 8000

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "hubble_report.wsgi"]