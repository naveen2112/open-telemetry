#!/usr/bin/env bash

# Exit the script as soon as something fails.
set -e

# Docker image that is linked to nginx.
UPSTREAM_NAME="$UPSTREAM_NAME"
UPSTREAM_APP="$UPSTREAM_APP"
UPSTREAM_PORT="$UPSTREAM_PORT"
REPORT_HOSTNAME="$REPORT_HOSTNAME"
TRAINING_HOSTNAME="$TRAINING_HOSTNAME"
UPSTREAM_PLACEHOLDER_NAME="$UPSTREAM_PLACEHOLDER_NAME"

# Where is our default config located?
DEFAULT_CONFIG_PATH="/etc/nginx/conf.d/default.conf"

# Replace all instances of the placeholders with the values above.
sed -i "s/REPORT_HOSTNAME/${REPORT_HOSTNAME}/g" "${DEFAULT_CONFIG_PATH}"
sed -i "s/TRAINING_HOSTNAME/${TRAINING_HOSTNAME}/g" "${DEFAULT_CONFIG_PATH}"
sed -i "s/UPSTREAM_NAME/${UPSTREAM_NAME}/g" "${DEFAULT_CONFIG_PATH}"
sed -i "s/UPSTREAM_APP/${UPSTREAM_APP}/g" "${DEFAULT_CONFIG_PATH}"
sed -i "s/UPSTREAM_PORT/${UPSTREAM_PORT}/g" "${DEFAULT_CONFIG_PATH}"
sed -i "s/UPSTREAM_PLACEHOLDER_NAME/${UPSTREAM_PLACEHOLDER_NAME}/g" "${DEFAULT_CONFIG_PATH}"

# Execute the CMD from the Dockerfile and pass in all of its arguments.
exec "$@"