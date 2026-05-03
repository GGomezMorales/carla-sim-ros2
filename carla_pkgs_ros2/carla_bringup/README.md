# carla_bringup

Top-level ROS 2 launch package for the CARLA demo. It starts the CARLA ROS bridge, spawns the example ego vehicle, starts waypoint publishing, publishes default speed/goal topics, and opens RViz2.

For visualization only, use `carla_rviz2`.

---

## Main files

```text
carla_bringup/
├── config/objects.json
├── launch/bringup.launch.py
├── launch/carla_ros_bridge_with_example_ego_vehicle.launch.py
└── rviz/carla_rviz2.rviz
```

| File                                                         | Purpose                                                           |
| ------------------------------------------------------------ | ----------------------------------------------------------------- |
| `launch/bringup.launch.py`                                   | Full startup entry point.                                         |
| `launch/carla_ros_bridge_with_example_ego_vehicle.launch.py` | Wraps bridge, ego vehicle spawn, and manual control launch files. |
| `config/objects.json`                                        | Ego vehicle, sensors, and pseudo-sensor definitions.              |
| `rviz/carla_rviz2.rviz`                                      | RViz2 layout used by the bringup launch.                          |

---

## Aliases

Defined by the repository `autostart.sh` file.

| Alias                | Use                                                           |
| -------------------- | ------------------------------------------------------------- |
| `carla`              | Start CARLA in off-screen low-quality mode.                   |
| `bros`               | Build the ROS workspace with `colcon build`.                  |
| `sros`               | Source ROS 2 and the workspace overlay.                       |
| `dros`               | Install missing ROS dependencies with `rosdep`.               |
| `carla_ros2 bringup` | Build, source, then launch `carla_bringup bringup.launch.py`. |
| `carla_ros2 rviz2`   | Build, source, then launch RViz2 only.                        |

---

## Run

Start CARLA in one terminal:

```bash
carla
```

Start the full ROS 2 bringup in another terminal:

```bash
carla_ros2 bringup
```

Direct launch, when already built and sourced:

```bash
ros2 launch carla_bringup bringup.launch.py
```

---

## Launch files

### `bringup.launch.py`

Creates the full CARLA ROS 2 demo launch. Public arguments:

| Argument       | Default                 | Description                                |
| -------------- | ----------------------- | ------------------------------------------ |
| `use_sim_time` | `true`                  | Enables simulated time for RViz2.          |
| `rviz_config`  | `rviz/carla_rviz2.rviz` | RViz2 config file.                         |
| `town`         | `Town01`                | CARLA map forwarded to the bridge wrapper. |

Started/Included actions:

- RViz2 through `carla_rviz2`.
- Bridge + ego vehicle wrapper.
- Delayed waypoint publisher.
- Default `/carla/ego_vehicle/target_speed` publisher.
- Default `/carla/ego_vehicle/goal` publisher.

### `carla_ros_bridge_with_example_ego_vehicle.launch.py`

Wraps upstream CARLA launch files:

| Launch file                           | Purpose                                                |
| ------------------------------------- | ------------------------------------------------------ |
| `carla_ros_bridge.launch.py`          | Connect ROS 2 to CARLA.                                |
| `carla_example_ego_vehicle.launch.py` | Spawn the ego vehicle and sensors from `objects.json`. |
| `carla_manual_control.launch.py`      | Start manual-control support for `ego_vehicle`.        |

Useful arguments include `host`, `port`, `timeout`, `role_name`, `vehicle_filter`, `objects_definition_file`, `town`, `passive`, and `fixed_delta_seconds`.
