# CARLA ROS 2 Simulation Environment

## Overview

This repository provides a Docker-based development environment for running the CARLA simulator together with the CARLA ROS bridge on **ROS 2 Foxy**.

The project is intentionally lightweight: instead of storing a full ROS workspace in the repository, it builds a ready-to-use container image that:

- pulls a **CARLA 0.9.15** simulator base image,
- installs ROS 2 Foxy development dependencies,
- clones the official `ros-bridge` repository into a workspace,
- prepares the environment with helpful shell aliases for day-to-day development.

The result is a reproducible setup for experimenting with CARLA + ROS 2 without manually assembling the simulator, ROS dependencies, and bridge packages on the host machine.

## Repository structure

The repository is centered around a few files:

- `Dockerfile`: builds the CARLA + ROS 2 image and prepares the workspace.
- `config.sh`: central place for image, container, and workspace naming.
- `autostart.sh`: configures the shell environment and helper aliases inside the container.
- `scripts/build.sh`: builds the Docker image.
- `scripts/run_docker.sh`: runs the container with standard graphics support.
- `scripts/run_nvidia.sh`: runs the container with NVIDIA GPU support.
- `scripts/bash.sh`: opens a shell inside the running container.

## Key features

- **Containerized setup**: isolates simulator and ROS dependencies from the host.
- **ROS 2 Foxy environment**: based on the official ROS Foxy base image.
- **CARLA 0.9.15 integration**: simulator files and Python API are available inside the container.
- **CARLA ROS bridge workspace**: the image clones `carla-simulator/ros-bridge` during build.
- **GPU-ready workflow**: includes a dedicated NVIDIA run script.
- **Developer aliases included**: common ROS workspace commands are preconfigured in the shell.

## Requirements

Before using this project, make sure you have:

- Docker installed and running.
- A Linux environment with X11 forwarding available if you want to use the provided run scripts as-is.
- NVIDIA Container Toolkit installed if you want to use `scripts/run_nvidia.sh`.
- Sufficient disk space for CARLA, ROS packages, and Docker layers.

## Configuration

Project-level settings are defined in `config.sh`:

```bash
CARLA_IMAGE="carlasim/carla:0.9.15"
WS_ROS="carla_ws"

DOCKER_IMAGE_NAME="carla-sim-ros2-image"
CONTAINER_NAME="carla-sim-ros2-container"
ROS_NETWORK="host"
```

These values control the workspace name, Docker image tag, and container name used by the helper scripts.

## How to use

This project includes helper scripts in the `scripts/` directory to simplify building and running the environment.

### 1. Build the Docker image

Run:

```bash
./scripts/build.sh
```

This builds the project image, installs the required ROS 2 dependencies, downloads the CARLA Python package, and clones the CARLA ROS bridge into the container workspace.

### 2. Run the container

There are two included ways to start the environment.

#### Standard Docker run

```bash
./scripts/run_docker.sh
```

Use this when running with the default Docker runtime.

#### NVIDIA GPU run (Recommended)

```bash
./scripts/run_nvidia.sh
```

Use this when your host supports NVIDIA containers and you want GPU acceleration.

### 3. Access the running container

Open an interactive shell inside the container with:

```bash
./scripts/bash.sh
```

## Helper aliases and commands

When the image is built, `autostart.sh` adds a set of aliases to the container user's shell configuration.

### Core aliases

- `carla`: moves to the CARLA installation directory and starts the simulator.
- `bros`: builds the ROS workspace with `colcon build`.
- `dros`: installs missing ROS dependencies using `rosdep`.
- `sros`: sources both the ROS 2 installation and the workspace overlay.

Inside the container:

```bash
sros
bros
carla
```

## Workspace details

Inside the container, the ROS workspace is created at:

```bash
/carla_ws
```

The CARLA ROS bridge repository is cloned into:

```bash
/carla_ws/src/ros-bridge
```

This means you can extend the environment by adding your own ROS 2 packages under the workspace `src/` directory and rebuilding with `colcon`.

## Networking and display

The provided run scripts start the container with:

- host networking,
- X11 socket mounting,
- environment variables for graphical applications,
- optional NVIDIA runtime support.

This setup is intended to make graphical tools and the simulator accessible from the container while keeping the workflow simple.

## Limitations and notes

- The repository currently focuses on the **containerized environment**, not on custom ROS 2 packages stored directly in this repo.
- The included run scripts are tailored to an X11-based Linux workflow.
- `config.sh` defines `CARLA_IMAGE`, but the current Docker build logic does not use that value to change the CARLA version in the `Dockerfile`. If you want to switch versions, you should update the Dockerfile build argument handling as well.

## Extending the project

This repository is a good base if you want to:

- add your own ROS 2 packages to the workspace,
- integrate autonomous driving or perception nodes,
- test CARLA bridge workflows in a reproducible environment,
- create a larger simulation stack on top of ROS 2 Foxy and CARLA.
