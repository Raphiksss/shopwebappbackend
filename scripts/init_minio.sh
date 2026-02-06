#!/bin/sh
set -e

until mc alias set local http://minio:9000 "${MINIO_ROOT_USER}" "${MINIO_ROOT_PASSWORD}"; do
  sleep 1
done

mc mb local/just-images || true
mc anonymous set download local/just-images

wait