ARG CARLA_VERSION=0.9.15

FROM carlasim/carla:${CARLA_VERSION} AS carla

FROM ros:foxy-ros-base-focal

SHELL ["/bin/bash", "-c"]

ARG CARLA_VERSION=0.9.15
ARG WS_ROS

ENV DEBIAN_FRONTEND=noninteractive \
    ROS_DISTRO=foxy \
    WS=/${WS_ROS} \
    CARLA_ROOT=/home/carla \
    USERNAME=carla

RUN apt-get update && apt-get install -y --no-install-recommends \
    bash-completion \
    build-essential \
    ca-certificates \
    curl \
    git \
    python3-pip \
    python3-dev \
    python3-setuptools \
    python3-wheel \
    python3-argcomplete \
    python3-colcon-common-extensions \
    python3-rosdep \
    software-properties-common \
    mesa-utils \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender1 \
    libvulkan1 \
    libsdl2-2.0-0 \
    libx11-xcb1 \
    libxcb-dri3-0 \
    libxcb-present0 \
    libxrandr2 \
    libxi6 \
    libxxf86vm1 \
    libglu1-mesa \
    libegl1 \
    libgl1 \
    && rm -rf /var/lib/apt/lists/*

RUN useradd -m -s /bin/bash ${USERNAME} \
    && mkdir -p ${WS}/src \
    && chown -R ${USERNAME}:${USERNAME} ${WS}

COPY --from=carla --chown=${USERNAME}:${USERNAME} /home/carla ${CARLA_ROOT}

RUN python3 -m pip install --upgrade pip wheel \
    && python3 -m pip install --no-cache-dir "setuptools==68.*" \
    && python3 -m pip uninstall -y carla || true \
    && python3 -m pip install --no-cache-dir "carla==${CARLA_VERSION}" "transforms3d" \
    && python3 -m pip install --no-cache-dir "importlib-metadata>=6.0" \
    && mkdir -p ${CARLA_ROOT}/PythonAPI/carla/dist \
    && python3 -m pip download --only-binary=:all: --no-deps \
    -d ${CARLA_ROOT}/PythonAPI/carla/dist "carla==${CARLA_VERSION}"

RUN cd ${WS}/src \
    && git clone --recurse-submodules https://github.com/carla-simulator/ros-bridge.git

RUN apt-get update && apt-get install -y --no-install-recommends \
    ros-${ROS_DISTRO}-rviz2 \
    ros-${ROS_DISTRO}-ackermann-msgs \
    ros-${ROS_DISTRO}-python-qt-binding \
    ros-${ROS_DISTRO}-pcl-conversions \
    ros-${ROS_DISTRO}-cv-bridge \
    python3-opencv \
    ros-${ROS_DISTRO}-vision-opencv \
    python3-pygame \
    ros-${ROS_DISTRO}-derived-object-msgs \
    && rm -rf /var/lib/apt/lists/*

RUN if [ ! -f /etc/ros/rosdep/sources.list.d/20-default.list ]; then rosdep init; fi \
    && rosdep update \
    && cd ${WS} \
    && source /opt/ros/${ROS_DISTRO}/setup.bash \
    && rosdep install --from-paths src --ignore-src -r -y --rosdistro ${ROS_DISTRO}

COPY ./autostart.sh ${WS}/autostart.sh

RUN chown -R ${USERNAME}:${USERNAME} /home/${USERNAME} ${WS} ${CARLA_ROOT} \
    && chmod +x ${WS}/autostart.sh \
    && ${WS}/autostart.sh

WORKDIR ${WS}

EXPOSE 2000 2001

USER ${USERNAME}

CMD ["/bin/bash"]