#!/bin/bash
set -e
MYSQL_ROOT_PASSWORD=${MYSQL_ROOT_PASSWORD:-}

until mysqladmin ping -h mysql_service -u root -p"$MYSQL_ROOT_PASSWORD" --ssl=OFF --silent; do
  echo "Waiting for MySQL..."
  sleep 2
done
exec alembic upgrade head