# CARLA ROS 2 Simulation Environment

## Overview

This repository provides a Docker-based development environment for running the CARLA simulator together with the CARLA ROS bridge on **ROS 2 Humble**.

Instead of storing a full ROS workspace in the repository, it builds a ready-to-use container image that:

- pulls a **CARLA 0.9.16** simulator base image,
- installs ROS 2 Humble development dependencies,
- clones the `ros-bridge` repository (the `leaderboard-2.0` branch, which targets CARLA 0.9.15+),
- installs the CARLA 0.9.16 Python API wheel plus the Python packages needed by the bridge (`transforms3d`, `networkx`),
- applies a patch for a known upstream bug in `pcl_recorder` ([#737](https://github.com/carla-simulator/ros-bridge/issues/737)),
- applies small compatibility patches for `carla_waypoint_publisher` and `carla_ad_agent/local_planner` so the simple A → B navigation flow works with CARLA 0.9.16,
- includes local ROS 2 packages under `carla_pkgs_ros2`,
- prepares the environment with helpful shell aliases and a `carla_ros2` helper command for day-to-day development.

The result is a reproducible setup for experimenting with CARLA + ROS 2 without manually assembling the simulator, ROS dependencies, and bridge packages on the host machine.

> **Version compatibility note:** The `ros-bridge` default branch (`main`) targets CARLA 0.9.13 and will refuse to start against a 0.9.16 server. This project pins the bridge to the `leaderboard-2.0` branch, which supports 0.9.15 and 0.9.16.

---

## Repository structure

```
carla-sim-ros2/
├── Dockerfile              # Builds the CARLA + ROS 2 image
├── config.sh               # Central configuration (image name, container name, workspace)
├── autostart.sh            # Shell aliases, helper commands, and compatibility patches
├── carla_pkgs_ros2/        # Local ROS 2 packages mounted into the container workspace
│   ├── carla_bringup/      # Launches bridge, waypoint publisher, and RViz2 together
│   └── carla_rviz2/        # RViz2 launch file and CARLA RViz configuration
└── scripts/
    ├── build.sh            # Builds the Docker image
    ├── run_docker.sh       # Runs the container (standard graphics)
    ├── run_nvidia.sh       # Runs the container (NVIDIA GPU)
    └── bash.sh             # Opens a shell in the running container
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

| Variable            | Purpose                                                                           |
| ------------------- | --------------------------------------------------------------------------------- |
| `CARLA_IMAGE`       | The CARLA Docker image used as the simulator base                                 |
| `WS_ROS`            | Name of the ROS workspace directory inside the container (`/carla_ws`)            |
| `DOCKER_IMAGE_NAME` | Tag given to the built Docker image                                               |
| `CONTAINER_NAME`    | Name assigned to the running container                                            |
| `ROS_NETWORK`       | Intended Docker network mode; the provided run scripts currently use `--net=host` |

> **Note:** `config.sh` defines `CARLA_IMAGE`, but the CARLA version is also hardcoded in the `Dockerfile` via the `CARLA_VERSION` build argument. If you change the version, update both files to keep them consistent.

---

## Shell aliases

The following aliases are added to both the `carla` user's and `root`'s `.bashrc` by `autostart.sh`:

| Alias   | Expands to                                                                        | Purpose                              |
| ------- | --------------------------------------------------------------------------------- | ------------------------------------ |
| `carla` | `cd $CARLA_ROOT && ./CarlaUE4.sh -quality-level=Low -RenderOffScreen`             | Start the CARLA simulator            |
| `bros`  | `cd ${WS} && colcon build`                                                        | Build the ROS workspace              |
| `dros`  | `cd ${WS} && rosdep update && rosdep install --from-paths src --ignore-src -r -y` | Install ROS dependencies             |
| `sros`  | `source /opt/ros/${ROS_DISTRO}/setup.bash && source ${WS}/install/setup.bash`     | Source ROS and the workspace overlay |

`autostart.sh` also adds a small helper function with shell completion:

| Command              | What it does                                                                                       |
| -------------------- | -------------------------------------------------------------------------------------------------- |
| `carla_ros2 bringup` | Builds, sources, and launches `carla_bringup`, including the bridge, waypoint publisher, and RViz2 |
| `carla_ros2 rviz2`   | Builds, sources, and launches only the RViz2 configuration from `carla_rviz2`                      |

---

## Workspace layout

Inside the container:

```
/carla_ws/                    ← ROS workspace (WS_ROS)
└── src/
    ├── ros-bridge/           ← Cloned from carla-simulator/ros-bridge (leaderboard-2.0 branch)
    └── carla_pkgs_ros2/      ← Mounted from this repository by the run scripts
        ├── carla_bringup/    ← Combined launch for bridge, waypoint publisher, and RViz2
        └── carla_rviz2/      ← RViz2 launch file and configuration

/home/carla/                  ← CARLA installation (CARLA_ROOT)
└── PythonAPI/
    └── carla/
        └── dist/             ← carla-0.9.16-*.whl (installed during image build)
```

The provided run scripts mount `./carla_pkgs_ros2` from the host into `/carla_ws/src/carla_pkgs_ros2`, so changes to those local packages persist outside the container. You can add your own ROS 2 packages under `/carla_ws/src/` and rebuild with `bros`.

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

Both scripts mount the X11 socket and set the required display environment variables so graphical applications (CARLA, RViz2) can render on the host screen.

---

### 3. Open a shell in the running container

```bash
./scripts/bash.sh
```

---

### 4. Set up and build the ROS workspace

Inside the container, run the following once to install dependencies and build:

```bash
# install missing ROS dependencies via rosdep
dros
# install missing ROS dependencies via rosdep
bros
# source ROS 2 Humble and the workspace overlay
sros
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
ros2 launch carla_ros_bridge carla_ros_bridge_with_example_ego_vehicle.launch.py
```

The bridge connects to `localhost:2000` by default.

You can also use the project bringup helper after starting CARLA:

```bash
carla_ros2 bringup
```

This command builds the workspace, sources the overlay, launches the example ego vehicle bridge, starts the waypoint publisher after a short delay, and opens RViz2 with the included CARLA configuration.

To open only RViz2 with the project configuration, use:

```bash
carla_ros2 rviz2
```

## Known limitations

- The run scripts are written for an **X11-based Linux workflow**. Wayland or macOS users may need to adjust the display forwarding.
- The `--rm` flag means **any changes made only inside the container are lost when it stops**. The provided `carla_pkgs_ros2` directory is already mounted from the host, but mount another host directory if you need to persist additional work:
  ```bash
  -v $(pwd)/my_packages:/carla_ws/src/my_packages
  ```
- The `leaderboard-2.0` bridge branch supports CARLA 0.9.15 and 0.9.16. Using the `main` branch of `ros-bridge` against this image will fail at startup with a version mismatch error.
- There is a known upstream bug in `ros-bridge` ([#737](https://github.com/carla-simulator/ros-bridge/issues/737)) where `pcl_recorder` is missing a `tf2_eigen` dependency and uses a deprecated header. The `autostart.sh` patches both automatically during the build — no manual action is needed.

---

## Extending the project

This repository is a minimal base. Common extensions include:

- Adding your own ROS 2 perception or control packages under `/carla_ws/src/`.
- Integrating autonomous driving stacks (Autoware, Nav2, etc.).
- Writing custom CARLA scenario scripts using the Python API.
- Pinning the `ros-bridge` to a specific commit for reproducibility.
