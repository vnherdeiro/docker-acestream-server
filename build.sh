#!/bin/bash -e

DOCKER_IMAGE_NAME="ace-server"


docker build . -t "$DOCKER_IMAGE_NAME"
