# Base image: python version python/3.10.8
FROM public.ecr.aws/docker/library/python:3.10.8

# Adding User
RUN useradd -ms /bin/bash hubble

# Declared Environment Variables
ENV FLASK_ROOT=/home/hubble/app
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Set working directory, where the commands will be ran:
RUN mkdir -p $FLASK_ROOT
WORKDIR $FLASK_ROOT

# Adding project files
ADD --chown=hubble . .

# Adding Packages
RUN pip install poetry==1.3.1
RUN poetry config virtualenvs.create false
RUN poetry install --no-interaction --no-ansi --no-root
RUN pip install gunicorn

ADD docker/app/entrypoint.sh /usr/bin/
RUN chmod +x /usr/bin/entrypoint.sh
ENTRYPOINT ["entrypoint.sh"]

EXPOSE 8000

USER hubble

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "app:app"]