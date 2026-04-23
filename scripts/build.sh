#!/bin/bash

set -e

PROJECT_ROOT="$(cd "$(dirname "$0")"; cd ..; pwd)"
source ${PROJECT_ROOT}/config.sh

cd "$PROJECT_ROOT"

docker build --build-arg IMAGE=${CARLA_IMAGE}  --build-arg WS_ROS=${WS_ROS} -t ${DOCKER_IMAGE_NAME} .
