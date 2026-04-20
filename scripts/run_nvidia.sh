#!/bin/bash

PROJECT_ROOT="$(cd "$(dirname "$0")"; cd ..; pwd)"
source ${PROJECT_ROOT}/config.sh

OS=$(uname -s | tr '[:upper:]' '[:lower:]')
OS_SIMPLE=${OS:0:1}

docker run --privileged --rm -it \
    --name $CONTAINER_NAME \
    --runtime=nvidia \
    --gpus all \
    -e NVIDIA_VISIBLE_DEVICES=all \
    -e NVIDIA_DRIVER_CAPABILITIES=all \
    -e DISPLAY \
    -e TERM \
    -e XDG_RUNTIME_DIR=/tmp \
    -e QT_X11_NO_MITSHM=1 \
    -e XAUTHORITY \
    -v /tmp/.X11-unix:/tmp/.X11-unix \
    -v $XAUTHORITY:$XAUTHORITY \
    --ipc="host" \
    --net=host \
    -t \
    ${DOCKER_IMAGE_NAME} 
