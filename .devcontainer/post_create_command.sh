#!/usr/bin/env bash

set -ex

# copy .env.example to .env
cp .env.example .env

# docker compose up
docker compose up -d

echo "done"