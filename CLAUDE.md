## What this repo is

A **Docker-based development environment**, not a full ROS workspace. It builds a single image that combines:

- **CARLA 0.9.16** simulator (pulled from `carlasim/carla:0.9.16` as a multi-stage source)
- **ROS 2 Humble** (`osrf/ros:humble-desktop-full` base)
- The `carla-simulator/ros-bridge` repo, cloned at build time on the **`leaderboard-2.0`** branch (not `main` — see "Version pinning" below)
- The CARLA 0.9.16 Python wheel (`cp310`, `manylinux_2_31_x86_64`)
- Two local ROS 2 packages under `carla_pkgs_ros2/` (mounted live into the container)
- Shell aliases and a `carla_ros2` helper function (added to both the `carla` user's and `root`'s `.bashrc`)
- Two upstream patches applied at image build time

The repo itself contains no Python/C++ source code for the bridge — the bridge is cloned inside the container during `docker build`.

## Repo layout

```
carla-sim-ros2/
├── Dockerfile                 # Multi-stage build: copies CARLA into a ROS 2 Humble base
├── config.sh                  # Shared env vars sourced by all host-side scripts
├── autostart.sh               # Runs once during image build; sets up aliases + patches
├── scripts/
│   ├── build.sh               # docker build → ${DOCKER_IMAGE_NAME}
│   ├── run_docker.sh          # docker run (software rendering, /dev/dri)
│   ├── run_nvidia.sh          # docker run with --runtime=nvidia --gpus all
│   └── bash.sh                # docker exec -it ${CONTAINER_NAME} bash
└── carla_pkgs_ros2/           # Mounted into /carla_ws/src/carla_pkgs_ros2 at run time
    ├── carla_bringup/         # Full demo: bridge + ego vehicle + waypoints + RViz2
    │   ├── launch/bringup.launch.py
    │   ├── launch/carla_ros_bridge_with_example_ego_vehicle.launch.py
    │   ├── config/objects.json    # Ego vehicle + sensor definitions
    │   └── rviz/carla_rviz2.rviz
    └── carla_rviz2/           # RViz2-only launch (no bridge, no CARLA)
        ├── launch/rviz2.launch.py
        └── rviz/carla_rviz2.rviz
```

## Critical version pinning — do not break

Three pieces have to stay aligned. Changing one without the others will produce a startup version mismatch or a broken Python install.

| Piece              | Pinned value                                                                  | Where it lives                        |
| ------------------ | ----------------------------------------------------------------------------- | ------------------------------------- |
| CARLA              | `0.9.16`                                                                       | `Dockerfile` (`ARG CARLA_VERSION`) **and** `config.sh` (`CARLA_IMAGE`) |
| Python API wheel   | `carla-0.9.16-cp310-cp310-manylinux_2_31_x86_64.whl` (Python 3.10)             | `Dockerfile` `pip install` line       |
| `ros-bridge` branch | `leaderboard-2.0` (supports CARLA 0.9.15 / 0.9.16)                            | `Dockerfile` `git clone --branch …`   |

The `ros-bridge` **default branch (`main`) targets CARLA 0.9.13 and will refuse to start** against the 0.9.16 server. If you switch CARLA versions, you almost certainly need to switch the bridge branch and the wheel filename simultaneously.

The ROS 2 base image is `osrf/ros:humble-desktop-full` and `ROS_DISTRO=humble` is hardcoded.

## Container layout (inside the image)

```
/carla_ws/                            # ROS workspace ($WS, value of WS_ROS)
└── src/
    ├── ros-bridge/                   # Cloned at image build; ephemeral (no host mount)
    └── carla_pkgs_ros2/              # Bind-mounted from host → edits persist
        ├── carla_bringup/
        └── carla_rviz2/

/home/carla/                          # $CARLA_ROOT, owned by user `carla`
├── CarlaUE4.sh                       # Simulator entry point
└── PythonAPI/carla/dist/             # 0.9.16 wheel (installed during build)
```

- Default user: **`carla`** (uid created via `useradd`), not `root`.
- `$PYTHONPATH` is set to include `${CARLA_ROOT}/PythonAPI/carla` in both `.bashrc` files.
- Ports `2000`/`2001` are exposed (CARLA RPC + streaming).
- `--net=host` is used by both run scripts, so bridge↔CARLA traffic stays on `localhost:2000`.

## Host-side workflow (commands run from the repo root)

```bash
# 1. Build image (≈30 GB total disk needed)
./scripts/build.sh

# 2. Start container (pick one)
./scripts/run_docker.sh        # software rendering via /dev/dri
./scripts/run_nvidia.sh        # NVIDIA Container Toolkit, recommended for CARLA

# 3. Open another shell in the running container
./scripts/bash.sh
```

All three run scripts source `config.sh`. Both `run_*` scripts use `--rm`, so **anything written inside the container outside `carla_pkgs_ros2/` is destroyed on exit**. To persist additional packages, add another `--volume` line, e.g.:
```bash
--volume="$(pwd)/my_packages:/carla_ws/src/my_packages"
```

## In-container workflow (aliases set by `autostart.sh`)

| Alias                | Meaning                                                                            |
| -------------------- | ---------------------------------------------------------------------------------- |
| `carla`              | `cd $CARLA_ROOT && ./CarlaUE4.sh -quality-level=Low -RenderOffScreen`              |
| `bros`               | `cd $WS && colcon build`                                                            |
| `dros`               | `cd $WS && rosdep update && rosdep install --from-paths src --ignore-src -r -y`     |
| `sros`               | `source /opt/ros/${ROS_DISTRO}/setup.bash && source $WS/install/setup.bash`         |
| `carla_ros2 bringup` | `bros && sros && ros2 launch carla_bringup bringup.launch.py`                       |
| `carla_ros2 rviz2`   | `bros && sros && ros2 launch carla_rviz2 rviz2.launch.py`                           |

Typical first-time bring-up inside the container:
```bash
dros   # install ROS dependencies (rosdep)
bros   # colcon build the workspace
sros   # source the overlay
# Terminal A:
carla
# Terminal B (after ./scripts/bash.sh):
carla_ros2 bringup
```

The `carla_ros2` function lives in both `.bashrc` files via the `# >>> carla_ros2 helpers >>>` block in `autostart.sh` (idempotent — uses `grep -qF` to avoid duplicate insertion). It has bash completion for `bringup|rviz2`.

## Patches applied at image build time

`autostart.sh` runs inside `RUN ${WS}/autostart.sh` during `docker build` and applies two patch sets:

1. **`patch_737`** — fixes upstream [`ros-bridge#737`](https://github.com/carla-simulator/ros-bridge/issues/737):
   - `pcl_recorder/CMakeLists.txt`: adds `tf2_eigen` to `ament_target_dependencies`.
   - `pcl_recorder/include/PclRecorderROS2.h`: rewrites `tf2_eigen/tf2_eigen.h` → `…hpp` (deprecated header).

2. **`patch_nodes`** — replaces two files on the `leaderboard-2.0` branch with their counterparts from `ros-bridge/master` so the simple A → B navigation flow works on CARLA 0.9.16:
   - `carla_waypoint_publisher/src/carla_waypoint_publisher/carla_waypoint_publisher.py` (replaced when it still uses `global_route_planner_dao` or lacks `from nav_msgs.msg import Path`).
   - `carla_ad_agent/src/carla_ad_agent/local_planner.py` (replaced when it still uses `create_service_client`).

Both functions use `curl` against `raw.githubusercontent.com`, so the image build needs internet. The patches are conditional (`grep` guards) and **idempotent** — running `autostart.sh` again is safe.

If you ever edit `autostart.sh`:
- Use `append_once` / `append_block_once` (defined at the top of the file) — they grep before writing to avoid duplicates across rebuilds.
- The script ends with `exec "$@"`, so it's also safe to use as a container entrypoint.
- Anything you add must work for **both** `/home/carla/.bashrc` **and** `/root/.bashrc` — the script writes to both.

## How `carla_bringup` is composed

`bringup.launch.py` is the top-level entry. It includes/starts in order:

1. **RViz2** (via `carla_rviz2/rviz2.launch.py`, uses `carla_bringup/rviz/carla_rviz2.rviz` by default).
2. **Bridge + ego vehicle + manual control** (via local `carla_ros_bridge_with_example_ego_vehicle.launch.py`, which wraps three upstream launch files from `carla_ros_bridge`, `carla_spawn_objects`, and `carla_manual_control`). The ego vehicle and sensor suite come from `carla_bringup/config/objects.json`.
3. **Delayed waypoint publisher** — wrapped in `TimerAction(period=8.0)` so the bridge has time to come up before waypoint publishing starts.
4. Two `ExecuteProcess` actions repeatedly publishing:
   - `/carla/ego_vehicle/target_speed` (`std_msgs/Float64`) at **1 Hz**, value `10.0`.
   - `/carla/ego_vehicle/goal` (`geometry_msgs/PoseStamped`) at **0.05 Hz**, fixed pose `x=50, y=0`.

If you change the ego vehicle behavior, also check whether `objects.json` (sensor suite + spawn pose) needs to match — the spawn point there is `x=202.55, y=-55.84, yaw=180.0` on `Town01`.

To engage the autonomous driving stack the bringup is built for, in another shell run:
```bash
ros2 launch carla_ad_agent carla_ad_agent.launch.py role_name:=ego_vehicle avoid_risk:=False
```

## Conventions used by the launch files

Both local packages follow the same style — keep new launch files consistent:

- `generate_launch_description()` has a docstring listing every launch argument with default + description, every included launch file, and every started node/process.
- Sections are delimited by long `###…` comment bars and `<!-- … -->` headers.
- Package shares resolved via `FindPackageShare(...)` then composed with `PathJoinSubstitution`.
- `DeclareLaunchArgument` calls always specify a `default_value`.
- Sim time defaults to `'true'`.

Both packages use `ament_cmake` (CMakeLists installs `launch/`, `rviz/`, and where applicable `config/` to `share/${PROJECT_NAME}/`). `package.xml` declares only `<buildtool_depend>ament_cmake</buildtool_depend>` and `<exec_depend>rviz2</exec_depend>` — runtime CARLA-bridge deps are pulled in via `rosdep` (`dros`) rather than declared per-package.

## Gotchas

- **CARLA version is duplicated** between `Dockerfile` (`ARG CARLA_VERSION=0.9.16`, twice) and `config.sh` (`CARLA_IMAGE`). Keep them in sync.
- **`build.sh` passes `--build-arg IMAGE=…`**, but the `Dockerfile` doesn't declare an `IMAGE` ARG — it uses `CARLA_VERSION` directly. Harmless, but don't rely on `IMAGE` propagating.
- **`config.sh` defines `ROS_NETWORK="host"`** but neither run script reads it — both hardcode `--net=host`. Treat that variable as informational only.
- **`run_docker.sh` requires `$XAUTHORITY` and `$DISPLAY` set on the host** (X11 only). Wayland or macOS hosts need adjusted display forwarding.
- **`run_*` scripts use `--rm`** — only `carla_pkgs_ros2/` survives. New ROS packages developed inside the container must be in a mounted directory or they're lost on exit.
- **`carla` user is uid'd via `useradd -m`** without an explicit uid; bind-mounted file ownership on the host may not match. Adjust the `useradd` line if you need uid alignment.
- **Patches re-fetch files from GitHub on every build.** A network outage during build will not break the bridge clone (that's `git`) but will silently skip the patch (`curl -fsSL`).
- **`carla_bringup/bringup.launch.py` starts both speed and goal publishers immediately** — even before the bridge is up. They publish at low rates and the bridge tolerates this, but if you change rates significantly, prefer wrapping them in `TimerAction` too.
- **The `town` argument is declared in `bringup.launch.py` but only forwarded to the bridge wrapper** — RViz2 won't reload its fixed frame if you change towns. Check `carla_rviz2.rviz` if you switch maps.

## When making changes

- **Bridge or CARLA source edits** → must happen inside the container under `/carla_ws/src/ros-bridge/` (ephemeral) **or** be added to `autostart.sh` as another idempotent patch function so they survive rebuilds.
- **New local ROS 2 packages** → drop them under `carla_pkgs_ros2/` (mounted) and rebuild with `bros` inside the container. Match the existing `ament_cmake` + launch-file conventions.
- **New aliases or env vars** → add via `append_once` inside `setup_aliases()` in `autostart.sh` so both `carla` and `root` get them, and rebuild the image.
- **Changing CARLA version** → update `Dockerfile` `ARG CARLA_VERSION` (both occurrences), `config.sh` `CARLA_IMAGE`, the wheel filename in the `pip install` line, **and** verify the `ros-bridge` branch still supports it.
- Don't commit anything under `build/`, `install/`, `log/`, or `devel/` — already covered by `.gitignore`.

## Quick reference — environment variables inside the container

| Var           | Default      | Source                |
| ------------- | ------------ | --------------------- |
| `ROS_DISTRO`  | `humble`     | `Dockerfile` `ENV`    |
| `CARLA_ROOT`  | `/home/carla` | `Dockerfile` `ENV`   |
| `WS`          | `/carla_ws`  | `Dockerfile` `ENV` (from `WS_ROS` build arg) |
| `USERNAME`    | `carla`      | `Dockerfile` `ENV`    |
| `PYTHONPATH`  | `${CARLA_ROOT}/PythonAPI/carla:${PYTHONPATH}` | `autostart.sh` → `.bashrc` |