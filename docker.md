# Hubble Reports

### Configuration:

    Python - **`3.10.8`**
    Database - **`PostgreSQL - 9.6`**

### Basic Local Configuration:

    Install the docker desktop application and clone the branch either from docker-development or developement branch.
    Create the .env file and name it as ".env".
    Store all the ENV variables in .env file.
    Change the host, username and password in trygg.env file.
    hostname - docker.for.mac.host.internal

### Run the all the below comments in terminal

    psql hubble_local < hubble_schema.sql
    psql hubble_local < hubble_data.sql
    psql hubble_local < hubble_eff_data.sql

### Initial setup:

    docker-compose up -d --build

To start, stop and restart the docker use the below commands :

    docker start <service> : to start the constainer.
    docker stop <service> : to stop the container.
    docker restart <service> : to restart the service whenever the gem install and application failed.

    docker-compose up :  to start the services defined in the compose file.
    docker-compose up <service> :  to start a specific service defined in the compose file.
    docker-compose build : to build the services defined in the compose file.
    docker-compose build <service> : to build a specific service defined in the compose file.
    docker ps : to list all the running container .
    docker exec -it <service> bash : to SSH into the container.
    docker-compose down : to stop the services defined in the compose file.
    docker-compose down <service> : to stop a specific service defined in the compose file.
