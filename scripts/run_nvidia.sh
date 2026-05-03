#!/bin/bash

PROJECT_ROOT="$(cd "$(dirname "$0")"; cd ..; pwd)"
source ${PROJECT_ROOT}/config.sh

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
    --volume="${PROJECT_ROOT}/carla_pkgs_ros2:/${WS_ROS}/src/carla_pkgs_ros2" \
    --ipc="host" \
    --net=host \
    -t \
    ${DOCKER_IMAGE_NAME} 
