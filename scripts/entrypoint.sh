#!/bin/bash
set -e

echo "Waiting for PostgreSQL..."
while ! nc -z postgresql 5432; do
    sleep 1
done
echo "PostgreSQL is ready"

echo "Initializing database..."
python /backend/scripts/init_db.py

echo "Checking for Minio..."
while ! nc -z minio 9000; do
    sleep 1
done
echo "Minio is ready"

sh /backend/scripts/init_minio.sh

echo "Starting application..."
exec uvicorn main:app --host 0.0.0.0 --port 8000
