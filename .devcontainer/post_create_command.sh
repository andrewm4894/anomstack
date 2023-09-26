#!/usr/bin/env bash

set -ex

echo "start post create command"

# show pwd
echo "pwd: $(pwd)"

# copy .env.example to .env
cp .env.example .env

# docker compose up
docker compose up -d

echo "done post create command"