#!/usr/bin/env bash

set -ex

echo "start post create command..."

# install requirements-dev.txt
pip install -r requirements-dev.txt

# install pre-commit
pre-commit install

# copy .example.env to .env
cp .example.env .env

# docker compose up
# docker compose up -d

echo "done post create command"
