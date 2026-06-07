# carla_scenario_manager

ROS 2 package for CARLA scenario operations. It starts a manager node that exposes service based world, weather, actor, and scenario state controls, plus status diagnostics.

---

## Main files

```text
carla_scenario_manager/
├── carla_scenario_manager/
│   ├── carla_client_adapter.py
│   ├── scenario_manager_core.py
│   ├── world_feature.py
│   ├── weather_feature.py
│   ├── actor_feature.py
│   └── scenario_feature.py
├── config/scenario_manager.yaml
├── launch/scenario_manager.launch.py
└── scripts/scenario_manager_node.py
```

| File                                              | Purpose                                                                      |
| ------------------------------------------------- | ---------------------------------------------------------------------------- |
| `scripts/scenario_manager_node.py`                | ROS 2 node entry point. Declares parameters, services, and status publisher. |
| `launch/scenario_manager.launch.py`               | Launches only the scenario manager node.                                     |
| `config/scenario_manager.yaml`                    | Default parameter values for manager behavior.                               |
| `carla_scenario_manager/carla_client_adapter.py`  | CARLA API adapter for world/weather/actor operations.                        |
| `carla_scenario_manager/scenario_manager_core.py` | Facade that composes world, weather, actor, and scenario features.           |

---

## Aliases

Defined by the repository `autostart.sh` file.

| Alias                | Use                                                           |
| -------------------- | ------------------------------------------------------------- |
| `carla`              | Start CARLA in off-screen low-quality mode.                   |
| `bros`               | Build the ROS workspace with `colcon build`.                  |
| `sros`               | Source ROS 2 and the workspace overlay.                       |
| `dros`               | Install ROS dependencies with `rosdep`.                       |

## Run

Build and source:

```bash
bros
sros
```

Run manager only:

```bash
ros2 launch carla_scenario_manager scenario_manager.launch.py
```

Run CARLA bringup + scenario manager together:

```bash
carla
carla_ros2 bringup
ros2 launch carla_scenario_manager scenario_manager.launch.py
```

---

## Launch files

### `scenario_manager.launch.py`

Creates the manager-only launch. Public arguments:

| Argument      | Default                        | Description                                             |
| ------------- | ------------------------------ | ------------------------------------------------------- |
| `host`        | `localhost`                    | CARLA host. Forwarded to node parameter `carla.host`.   |
| `port`        | `2000`                         | CARLA port. Forwarded to node parameter `carla.port`.   |
| `timeout`     | `5.0`                          | CARLA timeout in seconds. Forwarded to `carla.timeout`. |
| `params_file` | `config/scenario_manager.yaml` | Parameter YAML loaded by the node.                      |

Started node:

| Package                  | Executable                 | Node name                |
| ------------------------ | -------------------------- | ------------------------ |
| `carla_scenario_manager` | `scenario_manager_node.py` | `carla_scenario_manager` |

---

## ROS interfaces

### Services

All services use `std_srvs/srv/Trigger` with empty request payload (`{}`).

| Service                                       | Uses parameters        | Behavior                                                          |
| --------------------------------------------- | ---------------------- | ----------------------------------------------------------------- |
| `/carla_scenario_manager/reset_world`         | none                   | Reloads current map and resets manager state to `IDLE`.           |
| `/carla_scenario_manager/reload_world`        | `target_town`          | Loads selected town and resets manager state to `IDLE`.           |
| `/carla_scenario_manager/set_weather_profile` | `weather.*`            | Applies `weather.profile` and then numeric overrides.             |
| `/carla_scenario_manager/spawn_vehicle`       | `spawn.*`              | Spawns one vehicle from spawn configuration.                      |
| `/carla_scenario_manager/destroy_actor`       | `target_actor_id`      | Destroys actor by id.                                             |
| `/carla_scenario_manager/start_scenario`      | `scenario.active_name` | Sets manager state to `RUNNING` with selected scenario name.      |
| `/carla_scenario_manager/stop_scenario`       | none                   | Stops active scenario and returns manager state to `IDLE`.        |
| `/carla_scenario_manager/list_actors`         | none                   | Returns actor count summary and preview in response message text. |

### Topic

| Topic                            | Type                                   | Behavior                                                                 |
| -------------------------------- | -------------------------------------- | ------------------------------------------------------------------------ |
| `/carla_scenario_manager/status` | `diagnostic_msgs/msg/DiagnosticStatus` | Publishes manager state and active scenario at `status.publish_rate_hz`. |

---

## Runtime discovery snippets (dynamic sets)

List weather presets from installed CARLA Python API:

```bash
python3 -c "import carla; print([k for k in dir(carla.WeatherParameters) if k and k[0].isupper()])"
```

List available map/town names from running CARLA server:

```bash
python3 -c "import carla; c=carla.Client('localhost',2000); c.set_timeout(5.0); print(c.get_available_maps())"
```

List vehicle blueprint ids and filter examples:

```bash
python3 -c "import carla; c=carla.Client('localhost',2000); c.set_timeout(5.0); w=c.get_world(); b=[bp.id for bp in w.get_blueprint_library().filter('vehicle.*')]; print('count:', len(b)); print('sample:', b[:25]); print('filters: vehicle.* , vehicle.tesla.* , vehicle.tesla.model3')"
```

---

## Usage workflows

### Reload world/town

```bash
ros2 param set /carla_scenario_manager target_town Town03
ros2 service call /carla_scenario_manager/reload_world std_srvs/srv/Trigger "{}"
```

### Apply weather profile and overrides

```bash
ros2 param set /carla_scenario_manager weather.profile ClearSunset
ros2 param set /carla_scenario_manager weather.precipitation 50.0
ros2 param set /carla_scenario_manager weather.cloudiness 50.0
ros2 service call /carla_scenario_manager/set_weather_profile std_srvs/srv/Trigger "{}"
```

### Spawn random vehicle

```bash
ros2 param set /carla_scenario_manager spawn.blueprint_filter vehicle.tesla.model3
ros2 param set /carla_scenario_manager spawn.use_random_spawn true
ros2 param set /carla_scenario_manager spawn.spawn_point_index 2
ros2 service call /carla_scenario_manager/spawn_vehicle std_srvs/srv/Trigger "{}"
```

### Spawn manual transform vehicle

```bash
ros2 param set /carla_scenario_manager spawn.use_random_spawn false
ros2 param set /carla_scenario_manager spawn.x 10.0
ros2 param set /carla_scenario_manager spawn.y 15.0
ros2 param set /carla_scenario_manager spawn.z 0.5
ros2 param set /carla_scenario_manager spawn.yaw 90.0
ros2 service call /carla_scenario_manager/spawn_vehicle std_srvs/srv/Trigger "{}"
```

### Destroy actor by id

```bash
ros2 param set /carla_scenario_manager target_actor_id 42
ros2 service call /carla_scenario_manager/destroy_actor std_srvs/srv/Trigger "{}"
```

### Start and stop scenario state

```bash
ros2 param set /carla_scenario_manager scenario.active_name lane_change_test
ros2 service call /carla_scenario_manager/start_scenario std_srvs/srv/Trigger "{}"
ros2 service call /carla_scenario_manager/stop_scenario std_srvs/srv/Trigger "{}"
```

### List actors and monitor status

```bash
ros2 service call /carla_scenario_manager/list_actors std_srvs/srv/Trigger "{}"
ros2 topic echo /carla_scenario_manager/status
```

### Parameter override at launch

```bash
ros2 launch carla_scenario_manager scenario_manager.launch.py \
  host:=localhost \
  port:=2000 \
  timeout:=5.0 \
  params_file:=/absolute/path/to/scenario_manager.yaml
```

---

## Troubleshooting

- `CARLA Python API is not available`: verify CARLA Python module installation and `PYTHONPATH`.
- `No blueprint matches filter`: adjust `spawn.blueprint_filter` to a valid vehicle blueprint.
- `CARLA rejected the spawn request`: try a different spawn point or set `spawn.use_random_spawn=true`.
- `target_town must not be empty`: provide a non-empty town before `/reload_world`.
- `status.publish_rate_hz must be > 0.0`: set a positive publish rate.
- `target_actor_id must be > 0`: use a positive actor id.

---

## Notes

- `start_scenario` and `stop_scenario` update internal manager state only; they do not run ScenarioRunner.
- Service responses use `std_srvs/srv/Trigger`; structured details are included in backend result data but returned as message text.
