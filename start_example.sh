#!/usr/bin/env bash

docker build -t quick_example .
docker-compose -f quick_example.yaml up -d
