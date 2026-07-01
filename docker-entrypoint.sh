#!/bin/sh
# Apply database migrations, retrying until Postgres is reachable, then start the app.
set -e

echo "Applying database migrations..."
until alembic upgrade head; do
  echo "Database not ready yet — retrying in 2s..."
  sleep 2
done
echo "Migrations applied."

exec "$@"
