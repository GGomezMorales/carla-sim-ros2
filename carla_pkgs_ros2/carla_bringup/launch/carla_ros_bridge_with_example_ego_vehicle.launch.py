from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    """
    Generate the ROS 2 launch description for the CARLA ROS bridge with an example ego vehicle.

    This launch file starts the CARLA ROS bridge, spawns an example ego vehicle
    using ``carla_spawn_objects``, and brings up the ``carla_manual_control`` node.
    It declares configurable launch arguments to control the connection to the
    CARLA simulator, the ego vehicle properties, and the simulation behavior.

    Launch arguments:
        host (str): Host where the CARLA simulator is running.
            Defaults to ``"localhost"``.
        port (str): TCP port of the CARLA simulator.
            Defaults to ``"2000"``.
        timeout (str): Connection timeout in seconds.
            Defaults to ``"10"``.
        role_name (str): Role name assigned to the ego vehicle.
            Defaults to ``"ego_vehicle"``.
        vehicle_filter (str): Blueprint filter used to select the ego vehicle.
            Defaults to ``"vehicle.*"``.
        objects_definition_file (str): .
            Defaults to ``"None"``.
        town (str): CARLA town/map to load.
            Defaults to ``"Town01"``.
        passive (str): Whether the bridge runs in passive mode.
            Defaults to ``"False"``.
        synchronous_mode_wait_for_vehicle_control_command (str): Whether the
            bridge waits for vehicle control commands in synchronous mode.
            Defaults to ``"False"``.
        fixed_delta_seconds (str): Fixed simulation step in seconds.
            Defaults to ``"0.05"``.

    Returns:
        LaunchDescription: A ROS 2 launch description containing the declared
        launch arguments and the CARLA ROS bridge, ego vehicle spawn, and
        manual control launch includes.
    """

    ###########################################################################################################

    # <!-- Shared packages -->
    carla_bringup_pkg = FindPackageShare('carla_bringup')
    carla_ros_bridge_pkg = FindPackageShare('carla_ros_bridge')
    carla_spawn_objects_pkg = FindPackageShare('carla_spawn_objects')
    carla_manual_control_pkg = FindPackageShare('carla_manual_control')
    ###########################################################################################################

    # <!-- Config arguments -->
    host = LaunchConfiguration('host')
    port = LaunchConfiguration('port')
    timeout = LaunchConfiguration('timeout')
    role_name = LaunchConfiguration('role_name')
    vehicle_filter = LaunchConfiguration('vehicle_filter')
    town = LaunchConfiguration('town')
    passive = LaunchConfiguration('passive')
    objects_definition_file = LaunchConfiguration('objects_definition_file')
    synchronous_mode_wait_for_vehicle_control_command = LaunchConfiguration(
        'synchronous_mode_wait_for_vehicle_control_command'
    )
    fixed_delta_seconds = LaunchConfiguration('fixed_delta_seconds')
    ###########################################################################################################

    # <!-- Paths -->
    carla_ros_bridge_launch_path = PathJoinSubstitution(
        [
            carla_ros_bridge_pkg,
            'carla_ros_bridge.launch.py'
        ]
    )

    carla_example_ego_vehicle_launch_path = PathJoinSubstitution(
        [
            carla_spawn_objects_pkg,
            'carla_example_ego_vehicle.launch.py'
        ]
    )

    carla_manual_control_launch_path = PathJoinSubstitution(
        [
            carla_manual_control_pkg,
            'carla_manual_control.launch.py'
        ]
    )

    objects_definition_file_path = PathJoinSubstitution(
        [
            carla_bringup_pkg,
            'config',
            'objects.json'
        ]
    )
    ###########################################################################################################

    # <!-- Declare arguments -->
    declare_host_cmd = DeclareLaunchArgument(
        'host',
        default_value='localhost'
    )

    declare_port_cmd = DeclareLaunchArgument(
        'port',
        default_value='2000'
    )

    declare_timeout_cmd = DeclareLaunchArgument(
        'timeout',
        default_value='10'
    )

    declare_role_name_cmd = DeclareLaunchArgument(
        'role_name',
        default_value='ego_vehicle'
    )

    declare_vehicle_filter_cmd = DeclareLaunchArgument(
        'vehicle_filter',
        default_value='vehicle.*'
    )

    declare_objects_definition_file_cmd = DeclareLaunchArgument(
        'objects_definition_file',
        default_value=objects_definition_file_path
    )

    declare_town_cmd = DeclareLaunchArgument(
        'town',
        default_value='Town01'
    )

    declare_passive_cmd = DeclareLaunchArgument(
        'passive',
        default_value='False'
    )

    declare_synchronous_mode_wait_for_vehicle_control_command_cmd = DeclareLaunchArgument(
        'synchronous_mode_wait_for_vehicle_control_command',
        default_value='False'
    )

    declare_fixed_delta_seconds_cmd = DeclareLaunchArgument(
        'fixed_delta_seconds',
        default_value='0.05'
    )
    ###########################################################################################################

    # <!-- CARLA ROS bridge launcher -->
    carla_ros_bridge_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            carla_ros_bridge_launch_path
        ),
        launch_arguments={
            'host': host,
            'port': port,
            'town': town,
            'timeout': timeout,
            'passive': passive,
            'synchronous_mode_wait_for_vehicle_control_command': synchronous_mode_wait_for_vehicle_control_command,
            'fixed_delta_seconds': fixed_delta_seconds
        }.items()
    )

    # <!-- Example ego vehicle launcher -->
    carla_example_ego_vehicle_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            carla_example_ego_vehicle_launch_path
        ),
        launch_arguments={
            'host': host,
            'port': port,
            'timeout': timeout,
            'vehicle_filter': vehicle_filter,
            'role_name': role_name,
            'objects_definition_file': objects_definition_file
        }.items()
    )

    # <!-- Manual control launcher -->
    carla_manual_control_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            carla_manual_control_launch_path
        ),
        launch_arguments={
            'role_name': role_name
        }.items()
    )
    ###########################################################################################################

    return LaunchDescription(
        [
            declare_host_cmd,
            declare_port_cmd,
            declare_timeout_cmd,
            declare_role_name_cmd,
            declare_vehicle_filter_cmd,
            declare_objects_definition_file_cmd,
            declare_town_cmd,
            declare_passive_cmd,
            declare_synchronous_mode_wait_for_vehicle_control_command_cmd,
            declare_fixed_delta_seconds_cmd,
            carla_ros_bridge_launch,
            carla_example_ego_vehicle_launch,
            carla_manual_control_launch
        ]
    )
