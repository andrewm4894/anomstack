#!/usr/bin/env bash

set -ex

echo "start post create command..."

# copy .example.env to .env
cp .example.env .env

# docker compose up
docker compose up -d

echo "done post create command"