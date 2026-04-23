#!/bin/bash

PROJECT_ROOT="$(cd "$(dirname "$0")"; cd ..; pwd)"
source ${PROJECT_ROOT}/config.sh

docker run --privileged --rm -it \
    --name $CONTAINER_NAME \
    --device /dev/dri \
    -e DISPLAY \
    -e TERM \
    -e XDG_RUNTIME_DIR=/tmp \
    -e QT_X11_NO_MITSHM=1 \
    -e XAUTHORITY \
    -v /tmp/.X11-unix:/tmp/.X11-unix \
    -v $XAUTHORITY:$XAUTHORITY \
    --net=host \
    -t \
    ${DOCKER_IMAGE_NAME} 
