#!/usr/bin/env bash

set -eux

docker compose -f ./docker-compose.yaml build
docker compose -f ./docker-compose.yaml up -d