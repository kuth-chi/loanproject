#!/bin/sh

echo "Initializing postgres db..."

while ! nc -z $DB_HOST $DB_PORT; do
  sleep 1
done

echo "Postgres database has initialized successfully"

exec "$@"
