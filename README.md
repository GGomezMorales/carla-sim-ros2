
# CARLA ROS 2 Simulation Environment

## Overview

This repository provides a Docker-based development environment for running the CARLA simulator together with the CARLA ROS bridge on **ROS 2 Humble**.

Instead of storing a full ROS workspace in the repository, it builds a ready-to-use container image that:

- pulls a **CARLA 0.9.16** simulator base image,
- installs ROS 2 Humble development dependencies,
- clones the `ros-bridge` repository (the `leaderboard-2.0` branch, which targets CARLA 0.9.15+),
- installs the CARLA 0.9.16 Python API wheel,
- prepares the environment with helpful shell aliases for day-to-day development.

The result is a reproducible setup for experimenting with CARLA + ROS 2 without manually assembling the simulator, ROS dependencies, and bridge packages on the host machine.

> **Version compatibility note:** The `ros-bridge` default branch (`main`) targets CARLA 0.9.13 and will refuse to start against a 0.9.16 server. This project pins the bridge to the `leaderboard-2.0` branch, which supports 0.9.15 and 0.9.16.

---

## Repository structure

```
carla-sim-ros2/
├── Dockerfile          # Builds the CARLA + ROS 2 image
├── config.sh           # Central configuration (image name, container name, workspace)
├── autostart.sh        # Shell aliases and environment setup inside the container
└── scripts/
    ├── build.sh        # Builds the Docker image
    ├── run_docker.sh   # Runs the container (standard graphics)
    ├── run_nvidia.sh   # Runs the container (NVIDIA GPU)
    └── bash.sh         # Opens a shell in the running container
```

---

## Requirements

- Docker installed and running.
- A Linux host with X11 forwarding available (required by the provided run scripts as-is).
- NVIDIA Container Toolkit installed if you want to use `scripts/run_nvidia.sh`.
- Sufficient disk space for CARLA, ROS packages, and Docker layers (~30 GB recommended).

---

## Configuration

All project-level settings are defined in `config.sh`:

```bash
CARLA_IMAGE="carlasim/carla:0.9.16"
WS_ROS="carla_ws"

DOCKER_IMAGE_NAME="carla-sim-ros2-image"
CONTAINER_NAME="carla-sim-ros2-container"
ROS_NETWORK="host"
```

| Variable              | Purpose                                                                       |
| --------------------- | ----------------------------------------------------------------------------- |
| `CARLA_IMAGE`       | The CARLA Docker image used as the simulator base                             |
| `WS_ROS`            | Name of the ROS workspace directory inside the container (`/carla_ws`)      |
| `DOCKER_IMAGE_NAME` | Tag given to the built Docker image                                           |
| `CONTAINER_NAME`    | Name assigned to the running container                                        |
| `ROS_NETWORK`       | Docker network mode (`host` gives the container access to the host network) |

> **Note:** `config.sh` defines `CARLA_IMAGE`, but the CARLA version is also hardcoded in the `Dockerfile` via the `CARLA_VERSION` build argument. If you change the version, update both files to keep them consistent.

---

## How to use

### 1. Build the Docker image

```bash
./scripts/build.sh
```

This builds the image, installs all ROS 2 dependencies, downloads the CARLA 0.9.16 Python wheel, and clones the ROS bridge into the container workspace.

---

### 2. Run the container

There are two ways to start the container depending on your GPU setup.

#### Standard (no NVIDIA runtime)

```bash
./scripts/run_docker.sh
```

Uses the default Docker runtime with `/dev/dri` device access for software rendering.

#### NVIDIA GPU (recommended for CARLA)

```bash
./scripts/run_nvidia.sh
```

Passes `--runtime=nvidia --gpus all` and exposes full NVIDIA driver capabilities. Use this when running CARLA with GPU rendering.

Both scripts mount the X11 socket and set the required display environment variables so graphical applications (CARLA, RViz2) can render on the host screen.

---

### 3. Open a shell in the running container

```bash
./scripts/bash.sh
```

This runs `docker exec -it <container> bash` against the container started in step 2.

---

### 4. Set up and build the ROS workspace

Inside the container, run the following once to install dependencies and build:

```bash
sros   # source ROS 2 Humble and the workspace overlay
dros   # install missing ROS dependencies via rosdep
bros   # build the workspace with colcon
```

Then source the workspace again to pick up the freshly built packages:

```bash
sros
```

---

### 5. Launch the CARLA ROS bridge

In one terminal inside the container, start the CARLA simulator:

```bash
carla
```

In a second terminal inside the container (after `sros`), launch the bridge:

```bash
ros2 launch carla_ros_bridge carla_ros_bridge.launch.py
```

The bridge connects to `localhost:2000` by default.

---

## Shell aliases

The following aliases are added to the container user's `.bashrc` by `autostart.sh`:

| Alias     | Expands to                                                                              | Purpose                              |
| --------- | --------------------------------------------------------------------------------------- | ------------------------------------ |
| `carla` | `cd /home/carla && ./CarlaUE4.sh -quality-level=Low -RenderOffScreen`                 | Start the CARLA simulator            |
| `bros`  | `cd /carla_ws && colcon build`                                                        | Build the ROS workspace              |
| `dros`  | `cd /carla_ws && rosdep update && rosdep install --from-paths src --ignore-src -r -y` | Install ROS dependencies             |
| `sros`  | `source /opt/ros/humble/setup.bash && source /carla_ws/install/setup.bash`            | Source ROS and the workspace overlay |

---

## Workspace layout

Inside the container:

```
/carla_ws/              ← ROS workspace (WS_ROS)
└── src/
    └── ros-bridge/     ← Cloned from carla-simulator/ros-bridge (leaderboard-2.0 branch)

/home/carla/            ← CARLA installation (CARLA_ROOT)
└── PythonAPI/
    └── carla/
        └── dist/       ← carla-0.9.16-*.whl (installed during image build)
```

You can add your own ROS 2 packages under `/carla_ws/src/` and rebuild with `bros`.

---

## Networking and display

The run scripts start the container with:

- `--net=host` — the container shares the host network stack, so the bridge can reach CARLA on `localhost:2000` without any port mapping.
- X11 socket mounted at `/tmp/.X11-unix` with the `DISPLAY` and `XAUTHORITY` environment variables forwarded — graphical tools render on the host display.
- `--privileged` — required for hardware device access (GPU, DRI).
- `--rm` — the container is removed automatically when it exits.

---

## Known limitations

- The run scripts are written for an **X11-based Linux workflow**. Wayland or macOS users may need to adjust the display forwarding.
- The `--rm` flag means **any changes made inside the container are lost when it stops**. Mount a host directory if you need to persist work:
  ```bash
  -v $(pwd)/my_packages:/carla_ws/src/my_packages
  ```
- The `leaderboard-2.0` bridge branch supports CARLA 0.9.15 and 0.9.16. Using the `main` branch of `ros-bridge` against this image will fail at startup with a version mismatch error.

---

## Extending the project

This repository is a minimal base. Common extensions include:

- Adding your own ROS 2 perception or control packages under `/carla_ws/src/`.
- Integrating autonomous driving stacks (Autoware, Nav2, etc.).
- Writing custom CARLA scenario scripts using the Python API.
- Pinning the `ros-bridge` to a specific commit for reproducibility.
