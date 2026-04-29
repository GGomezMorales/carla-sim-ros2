ARG CARLA_VERSION=0.9.16

FROM carlasim/carla:${CARLA_VERSION} AS carla

FROM osrf/ros:humble-desktop-full

ARG WS_ROS
ARG CARLA_VERSION=0.9.16
ENV DEBIAN_FRONTEND=noninteractive
ENV ROS_DISTRO=humble
ENV CARLA_ROOT=/home/carla
ENV USERNAME=carla
ENV WS=/${WS_ROS}
WORKDIR ${WS}

RUN useradd -m -s /bin/bash ${USERNAME} \
    && mkdir -p ${WS}/src

COPY --from=carla --chown=root:root /workspace ${CARLA_ROOT}
RUN chown -R ${USERNAME}:${USERNAME} ${CARLA_ROOT}

RUN apt-get update && apt-get install -y --no-install-recommends \
    python3-opencv \
    python3-pygame \
    python3-pip \
    ca-certificates \
    iputils-ping \
    net-tools \
    curl \
    git \
    nano

RUN python3 -m pip install \
    ${CARLA_ROOT}/PythonAPI/carla/dist/carla-${CARLA_VERSION}-cp310-cp310-manylinux_2_31_x86_64.whl

RUN pip3 install -U transforms3d networkx

RUN mkdir -p ${WS}/src && cd ${WS}/src \
    && git clone --recurse-submodules \
    --branch leaderboard-2.0 \
    https://github.com/carla-simulator/ros-bridge.git

RUN chown -R ${USERNAME}:${USERNAME} ${WS}

RUN apt-get update && apt-get install -y --no-install-recommends \
    ros-${ROS_DISTRO}-rviz2 \
    ros-${ROS_DISTRO}-ackermann-msgs \
    ros-${ROS_DISTRO}-python-qt-binding \
    ros-${ROS_DISTRO}-pcl-conversions \
    ros-${ROS_DISTRO}-cv-bridge \
    ros-${ROS_DISTRO}-vision-opencv \
    ros-${ROS_DISTRO}-derived-object-msgs \
    ros-${ROS_DISTRO}-tf2-eigen \
    ros-${ROS_DISTRO}-tf2-geometry-msgs \
    ros-${ROS_DISTRO}-tf2-ros \
    && rm -rf /var/lib/apt/lists/*

COPY ./autostart.sh ${WS}/autostart.sh
RUN chmod +x ${WS}/autostart.sh \
    && ${WS}/autostart.sh

USER ${USERNAME}

EXPOSE 2000 2001

CMD ["bash"]
