#!/usr/bin/env python3

import rclpy
from diagnostic_msgs.msg import DiagnosticStatus, KeyValue
from rcl_interfaces.msg import SetParametersResult
from rclpy.node import Node
from std_srvs.srv import Trigger

from carla_scenario_manager.carla_client_adapter import CarlaClientAdapter
from carla_scenario_manager.scenario_manager_core import ManagerState, ScenarioManagerCore
from carla_scenario_manager.core_context import OperationResult


class ScenarioManagerNode(Node):
    """
    ROS-facing node for scenario manager operations.

    This class wraps the ScenarioManagerCore and CarlaClientAdapter, exposing
    their functionalities via ROS2 services and parameters. It also periodically
    publishes the manager's state to a diagnostic topic.
    """

    def __init__(self):
        """
        Initialize node, parameters, publishers, timers, and services.

        Sets up the CARLA client adapter using ROS parameters, initializes the
        core scenario manager, sets up a parameter modification callback, and
        registers all available services.
        """
        super().__init__('carla_scenario_manager')

        self._declare_parameters()

        adapter: CarlaClientAdapter = CarlaClientAdapter(
            host=self.get_parameter('carla.host').value,
            port=self.get_parameter('carla.port').value,
            timeout=self.get_parameter('carla.timeout').value
        )
        self._core: ScenarioManagerCore = ScenarioManagerCore(adapter)

        self.add_on_set_parameters_callback(self._on_parameters_set)

        self._status_pub = self.create_publisher(
            DiagnosticStatus,
            '/carla_scenario_manager/status',
            10
        )

        self._status_timer = self.create_timer(
            float(self.get_parameter('status.publish_rate_hz').value) ** -1,
            self._publish_status
        )

        self._register_services()

        self.get_logger().info('' \
        '[CARLA ROS2 - START] carla_scenario_manager node started.'
        )

    def _declare_parameters(self):
        """
        Declare runtime parameters used by the scenario manager.

        Registers all required ROS2 parameters for CARLA connection, weather
        profiles, spawning configurations, and scenario management with their
        default values.
        """
        self.declare_parameter('carla.host', 'localhost')
        self.declare_parameter('carla.port', 2000)
        self.declare_parameter('carla.timeout', 5.0)

        self.declare_parameter('target_town', 'Town01')
        self.declare_parameter('target_actor_id', 1)
        self.declare_parameter('status.publish_rate_hz', 1.0)

        self.declare_parameter('weather.profile', 'ClearNoon')
        self.declare_parameter('weather.cloudiness', 0.0)
        self.declare_parameter('weather.precipitation', 0.0)
        self.declare_parameter('weather.precipitation_deposits', 0.0)
        self.declare_parameter('weather.wind_intensity', 0.0)
        self.declare_parameter('weather.sun_azimuth_angle', 0.0)
        self.declare_parameter('weather.sun_altitude_angle', 45.0)
        self.declare_parameter('weather.fog_density', 0.0)
        self.declare_parameter('weather.fog_distance', 0.0)
        self.declare_parameter('weather.wetness', 0.0)

        self.declare_parameter('spawn.blueprint_filter', 'vehicle.*')
        self.declare_parameter('spawn.role_name', 'scenario_vehicle')
        self.declare_parameter('spawn.use_random_spawn', True)
        self.declare_parameter('spawn.spawn_point_index', 0)
        self.declare_parameter('spawn.autopilot', False)
        self.declare_parameter('spawn.x', 0.0)
        self.declare_parameter('spawn.y', 0.0)
        self.declare_parameter('spawn.z', 0.5)
        self.declare_parameter('spawn.roll', 0.0)
        self.declare_parameter('spawn.pitch', 0.0)
        self.declare_parameter('spawn.yaw', 0.0)

        self.declare_parameter('scenario.active_name', 'default_scenario')

    def _register_services(self):
        """
        Register ROS services exposed by this node.

        Maps ROS2 `std_srvs/srv/Trigger` services to their corresponding
        callback methods in this class.
        """
        self.create_service(
            Trigger, '/carla_scenario_manager/reset_world', self.OnResetWorld
        )
        self.create_service(
            Trigger, '/carla_scenario_manager/reload_world', self.OnReloadWorld
        )
        self.create_service(
            Trigger, '/carla_scenario_manager/set_weather_profile', self.OnSetWeatherProfile
        )
        self.create_service(
            Trigger, '/carla_scenario_manager/spawn_vehicle', self.OnSpawnVehicle
        )
        self.create_service(
            Trigger, '/carla_scenario_manager/destroy_actor', self.OnDestroyActor
        )
        self.create_service(
            Trigger, '/carla_scenario_manager/start_scenario', self.OnStartScenario
        )
        self.create_service(
            Trigger, '/carla_scenario_manager/stop_scenario', self.OnStopScenario
        )
        self.create_service(
            Trigger, '/carla_scenario_manager/list_actors', self.OnListActors
        )

    def _trigger_response(self, result: OperationResult) -> Trigger.Response:
        """
        Convert a core operation result into a ROS2 Trigger response.

        Args:
            result: An object containing `success` (bool) and `message` (str) attributes 
                returned by operations in the ScenarioManagerCore.

        Returns:
            Trigger.Response: The ROS2 service response populated with success and message data.
        """
        response = Trigger.Response()
        response.success = bool(result.success)
        response.message = str(result.message)
        return response

    def _weather_overrides(self) -> dict[str, float]:
        """Collect weather override values from node parameters.

        Returns:
            dict[str, float]: A dictionary mapping weather parameter names to their 
                current float values configured in the ROS node.
        """
        return {
            'cloudiness': self.get_parameter('weather.cloudiness').value,
            'precipitation': self.get_parameter('weather.precipitation').value,
            'precipitation_deposits': self.get_parameter('weather.precipitation_deposits').value,
            'wind_intensity': self.get_parameter('weather.wind_intensity').value,
            'sun_azimuth_angle': self.get_parameter('weather.sun_azimuth_angle').value,
            'sun_altitude_angle': self.get_parameter('weather.sun_altitude_angle').value,
            'fog_density': self.get_parameter('weather.fog_density').value,
            'fog_distance': self.get_parameter('weather.fog_distance').value,
            'wetness': self.get_parameter('weather.wetness').value
        }

    def _spawn_config(self) -> dict[str, object]:
        """
        Collect vehicle spawn configuration values from node parameters.

        Returns:
            dict[str, object]: A dictionary of spawn settings including blueprint filters,
                spawn locations, and autopilot toggles.
        """
        return {
            'blueprint_filter': self.get_parameter('spawn.blueprint_filter').value,
            'role_name': self.get_parameter('spawn.role_name').value,
            'use_random_spawn': self.get_parameter('spawn.use_random_spawn').value,
            'spawn_point_index': self.get_parameter('spawn.spawn_point_index').value,
            'autopilot': self.get_parameter('spawn.autopilot').value,
            'x': self.get_parameter('spawn.x').value,
            'y': self.get_parameter('spawn.y').value,
            'z': self.get_parameter('spawn.z').value,
            'roll': self.get_parameter('spawn.roll').value,
            'pitch': self.get_parameter('spawn.pitch').value,
            'yaw': self.get_parameter('spawn.yaw').value
        }

    def _publish_status(self):
        """
        Publish current manager status on the diagnostic topic.

        Gathers the current state (RUNNING, ERROR, IDLE), active scenario, 
        and last error from the core logic, and publishes them as a 
        `DiagnosticStatus` message.
        """
        msg = DiagnosticStatus()
        msg.name = 'carla_scenario_manager'

        if self._core.state == ManagerState.RUNNING:
            msg.level = DiagnosticStatus.OK
            msg.message = 'RUNNING'
        elif self._core.state == ManagerState.ERROR:
            msg.level = DiagnosticStatus.ERROR
            msg.message = 'ERROR'
        else:
            msg.level = DiagnosticStatus.OK
            msg.message = 'IDLE'

        msg.hardware_id = 'carla'
        msg.values = [
            KeyValue(key='state', value=self._core.state.value),
            KeyValue(key='active_scenario', value=self._core.active_scenario),
        ]

        self._status_pub.publish(msg)

    def _on_parameters_set(self, params) -> SetParametersResult:
        """
        Validate dynamic parameter updates and refresh timers when needed.

        Args:
            params (list[rclpy.parameter.Parameter]): A list of parameters being modified.

        Returns:
            SetParametersResult: The result indicating whether the parameter update 
                was successful or rejected due to invalid values.
        """
        updated_status_rate = None

        for param in params:
            if param.name == 'status.publish_rate_hz' and float(param.value) <= 0.0:
                return SetParametersResult(
                    successful=False,
                    reason='status.publish_rate_hz must be > 0.0'
                )
            if param.name == 'status.publish_rate_hz':
                updated_status_rate = float(param.value)

            if param.name == 'target_actor_id' and int(param.value) <= 0:
                return SetParametersResult(
                    successful=False,
                    reason='target_actor_id must be > 0'
                )

        if updated_status_rate is not None:
            self._status_timer.cancel()
            self.destroy_timer(self._status_timer)
            self._status_timer = self.create_timer(
                updated_status_rate ** -1,
                self._publish_status
            )

        return SetParametersResult(successful=True)

    def OnResetWorld(self, _request, _response) -> Trigger.Response:
        """
        Handle reset-world trigger requests.

        Args:
            _request: The Trigger request object (unused).
            _response: The Trigger response object (unused).

        Returns:
            Trigger.Response: The outcome of the reset operation.
        """
        return self._trigger_response(self._core.ResetWorld())

    def OnReloadWorld(self, _request, _response) -> Trigger.Response:
        """
        Handle reload-world trigger requests.

        Args:
            _request: The Trigger request object (unused).
            _response: The Trigger response object (unused).

        Returns:
            Trigger.Response: The outcome of loading the town specified in parameters.
        """
        town = self.get_parameter('target_town').value
        return self._trigger_response(self._core.ReloadWorld(town))

    def OnSetWeatherProfile(self, _request, _response) -> Trigger.Response:
        """
        Handle set-weather-profile trigger requests.

        Args:
            _request: The Trigger request object (unused).
            _response: The Trigger response object (unused).

        Returns:
            Trigger.Response: The outcome of applying the configured weather profile.
        """
        profile = self.get_parameter('weather.profile').value
        return self._trigger_response(self._core.SetWeatherProfile(profile, self._weather_overrides()))

    def OnSpawnVehicle(self, _request, _response) -> Trigger.Response:
        """
        Handle spawn-vehicle trigger requests.

        Args:
            _request: The Trigger request object (unused).
            _response: The Trigger response object (unused).

        Returns:
            Trigger.Response: The outcome of the vehicle spawn operation.
        """
        return self._trigger_response(self._core.SpawnVehicle(self._spawn_config()))

    def OnDestroyActor(self, _request, _response) -> Trigger.Response:
        """
        Handle destroy-actor trigger requests.

        Args:
            _request: The Trigger request object (unused).
            _response: The Trigger response object (unused).

        Returns:
            Trigger.Response: The outcome of the actor destruction.
        """
        actor_id = int(self.get_parameter('target_actor_id').value)
        return self._trigger_response(self._core.DestroyActor(actor_id))

    def OnStartScenario(self, _request, _response) -> Trigger.Response:
        """
        Handle start-scenario trigger requests.

        Args:
            _request: The Trigger request object (unused).
            _response: The Trigger response object (unused).

        Returns:
            Trigger.Response: The outcome of attempting to start the configured scenario.
        """
        scenario_name = self.get_parameter('scenario.active_name').value
        return self._trigger_response(self._core.StartScenario(scenario_name))

    def OnStopScenario(self, _request, _response) -> Trigger.Response:
        """
        Handle stop-scenario trigger requests.

        Args:
            _request: The Trigger request object (unused).
            _response: The Trigger response object (unused).

        Returns:
            Trigger.Response: The outcome of stopping the currently active scenario.
        """
        return self._trigger_response(self._core.StopScenario())

    def OnListActors(self, _request, _response) -> Trigger.Response:
        """
        Handle list-actors trigger requests.

        Args:
            _request: The Trigger request object (unused).
            _response: The Trigger response object (unused).

        Returns:
            Trigger.Response: A message containing the summary string of active actors.
        """
        return self._trigger_response(self._core.ListActors())


def main(args=None):
    """
    Run the scenario manager node lifecycle.

    Initializes the ROS2 context, spins the ScenarioManagerNode to process
    callbacks and events, and handles graceful shutdown upon interrupt.

    Args:
        args (list[str], optional): Command-line arguments passed to the ROS node.
    """
    rclpy.init(args=args)
    node = ScenarioManagerNode()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
