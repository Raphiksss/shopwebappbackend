#!/bin/sh
set -e

/usr/bin/docker-entrypoint.sh minio server /data --console-address ":9001" &

until mc alias set local http://localhost:9000 "${MINIO_ROOT_USER}" "${MINIO_ROOT_PASSWORD}"; do
  sleep 1
done

mc mb local/just-images
mc anonymous set download local/just-images

wait