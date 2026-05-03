# carla_rviz2

RViz2 visualization package for the CARLA ROS 2 workspace. It starts only RViz2 with the provided CARLA display layout; it does not start CARLA or the ROS bridge.

---

## Main files

```text
carla_rviz2/
├── launch/rviz2.launch.py
└── rviz/carla_rviz2.rviz
```

| File                     | Purpose                              |
| ------------------------ | ------------------------------------ |
| `launch/rviz2.launch.py` | Starts RViz2 with launch arguments.  |
| `rviz/carla_rviz2.rviz`  | Default RViz2 visualization profile. |

---

## Aliases

Defined by the repository `autostart.sh` file.

| Alias                | Use                                                |
| -------------------- | -------------------------------------------------- |
| `bros`               | Build the ROS workspace.                           |
| `sros`               | Source ROS 2 and the workspace overlay.            |
| `dros`               | Install ROS dependencies.                          |
| `carla`              | Start the CARLA simulator.                         |
| `carla_ros2 rviz2`   | Build, source, then launch RViz2 only.             |
| `carla_ros2 bringup` | Build, source, then launch the full CARLA bringup. |

---

## Run

```bash
carla_ros2 rviz2
```

Direct launch, when already built and sourced:

```bash
ros2 launch carla_rviz2 rviz2.launch.py
```

---

## Launch file

### `rviz2.launch.py`

`generate_launch_description()` declares two arguments and starts the `rviz2` node.

| Argument       | Default                 | Description                    |
| -------------- | ----------------------- | ------------------------------ |
| `use_sim_time` | `true`                  | Use simulation time in RViz2.  |
| `rviz_config`  | `rviz/carla_rviz2.rviz` | RViz2 config loaded with `-d`. |

Started node:

| Package | Executable | Node name |
| ------- | ---------- | --------- |
| `rviz2` | `rviz2`    | `rviz2`   |
