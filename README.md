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

| Variable            | Purpose                                                                     |
| ------------------- | --------------------------------------------------------------------------- |
| `CARLA_IMAGE`       | The CARLA Docker image used as the simulator base                           |
| `WS_ROS`            | Name of the ROS workspace directory inside the container (`/carla_ws`)      |
| `DOCKER_IMAGE_NAME` | Tag given to the built Docker image                                         |
| `CONTAINER_NAME`    | Name assigned to the running container                                      |
| `ROS_NETWORK`       | Docker network mode (`host` gives the container access to the host network) |

> **Note:** `config.sh` defines `CARLA_IMAGE`, but the CARLA version is also hardcoded in the `Dockerfile` via the `CARLA_VERSION` build argument. If you change the version, update both files to keep them consistent.

---

## Shell aliases

The following aliases are added to both the `carla` user's and `root`'s `.bashrc` by `autostart.sh`:

| Alias   | Expands to                                                                        | Purpose                               |
| ------- | --------------------------------------------------------------------------------- | ------------------------------------- |
| `carla` | `cd $CARLA_ROOT && ./CarlaUE4.sh -quality-level=Low -RenderOffScreen`             | Start the CARLA simulator             |
| `bros`  | `cd ${WS} && colcon build`                                                        | Build the ROS workspace               |
| `dros`  | `cd ${WS} && rosdep update && rosdep install --from-paths src --ignore-src -r -y` | Install ROS dependencies              |
| `sros`  | `source /opt/ros/${ROS_DISTRO}/setup.bash && source ${WS}/install/setup.bash`     | Source ROS and the workspace overlay  |
| `apt`   | `sudo apt`                                                                        | Run apt without typing sudo each time |

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
dros   # install missing ROS dependencies via rosdep
bros   # build the workspace with colcon
sros   # source ROS 2 Humble and the workspace overlay
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

---

### 6. Simple A → B navigation example

This example uses only existing CARLA ROS bridge launch files and ROS 2 CLI commands. It does not require custom launch files, custom nodes, or new Python scripts.

The goal is to move the ego vehicle from its current position **A** to a destination **B**

#### Terminal 1: Start CARLA

```bash
carla
```

Leave this terminal running.

#### Terminal 2: Start the ROS bridge with an example ego vehicle

```bash
ros2 launch carla_ros_bridge carla_ros_bridge_with_example_ego_vehicle.launch.py
```

Leave this terminal running.

_Optional_: Check that the ego vehicle exists:

```bash
ros2 topic echo /carla/ego_vehicle/odometry --once
```

_If this command prints odometry data, the vehicle exists and its current position is point **A**._

#### Terminal 3: Start the waypoint publisher

```bash
ros2 launch carla_waypoint_publisher carla_waypoint_publisher.launch.py
```

This node creates the route from **A** to **B**. It does not drive the vehicle by itself.

_Optional_: Check that the waypoint and goal topics exist:

```bash
ros2 topic list | grep -E "goal|waypoints"
```

_You should see:_

```bash
/carla/ego_vehicle/goal
/carla/ego_vehicle/waypoints
```

#### Terminal 4: Start the autonomous driving agent

```bash
ros2 launch carla_ad_agent carla_ad_agent.launch.py role_name:=ego_vehicle avoid_risk:=False
```

This starts the AD agent and local planner. These nodes convert waypoints into throttle, brake, and steering commands.

_Optional_: Check that the local planner is ready to publish vehicle commands:

```bash
ros2 topic info /carla/ego_vehicle/vehicle_control_cmd -v
```

_The output should show:_

```text
Publisher count: 1
```

#### Terminal 5: Publish the target speed

Publish the target speed and leave this command running:

```bash
ros2 topic pub /carla/ego_vehicle/target_speed std_msgs/msg/Float64 "{data: 10.0}" -r 1
```

This tells the agent to drive at 10 m/s.

#### Terminal 6: Publish the destination B

Publish a goal pose. This is point **B**:

```bash
ros2 topic pub --once /carla/ego_vehicle/goal geometry_msgs/msg/PoseStamped \
"{header: {frame_id: 'map'}, pose: {position: {x: 50.0, y: 0.0, z: 0.0}, orientation: {w: 1.0}}}"
```

The waypoint publisher should now compute a route from the vehicle's current position **A** to the goal position **B**.

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
- There is a known upstream bug in `ros-bridge` ([#737](https://github.com/carla-simulator/ros-bridge/issues/737)) where `pcl_recorder` is missing a `tf2_eigen` dependency and uses a deprecated header. The `autostart.sh` patches both automatically during the build — no manual action is needed.

---

## Extending the project

This repository is a minimal base. Common extensions include:

- Adding your own ROS 2 perception or control packages under `/carla_ws/src/`.
- Integrating autonomous driving stacks (Autoware, Nav2, etc.).
- Writing custom CARLA scenario scripts using the Python API.
- Pinning the `ros-bridge` to a specific commit for reproducibility.
