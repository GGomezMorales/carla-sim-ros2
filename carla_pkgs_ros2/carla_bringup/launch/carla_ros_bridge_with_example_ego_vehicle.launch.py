from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    """
    Create the CARLA bridge and example ego vehicle launch description.

    The launch description declares connection, vehicle, map, and simulation
    timing arguments. It then includes launch files from the CARLA ROS bridge
    ecosystem to connect to a running CARLA simulator, spawn the example ego
    vehicle described by ``config/objects.json``, and start manual control for
    the configured ego vehicle role name.

    Launch arguments:
        host (str): Hostname or IP address of the CARLA simulator. Defaults to
            ``"localhost"``.
        port (str): TCP port of the CARLA simulator. Defaults to ``"2000"``.
        timeout (str): Connection timeout in seconds. Defaults to ``"10"``.
        role_name (str): Role name assigned to the ego vehicle and used in
            topic namespaces. Defaults to ``"ego_vehicle"``.
        vehicle_filter (str): CARLA blueprint filter used by the spawn package
            to select a vehicle blueprint. Defaults to ``"vehicle.*"``.
        objects_definition_file (str): JSON object/sensor definition file used
            by ``carla_spawn_objects``. Defaults to
            ``config/objects.json`` from this package.
        town (str): CARLA town/map loaded by the bridge. Defaults to
            ``"Town01"``.
        passive (str): Whether the bridge should run in passive mode. Defaults
            to ``"False"``.
        synchronous_mode_wait_for_vehicle_control_command (str): Whether the
            bridge waits for vehicle control commands while in synchronous
            operation. Defaults to ``"False"``.
        fixed_delta_seconds (str): Fixed simulation step in seconds used by
            the bridge timing configuration. Defaults to ``"0.05"``.

    Included launch files:
        carla_ros_bridge.launch.py: Starts the ROS bridge connection to CARLA.
        carla_example_ego_vehicle.launch.py: Spawns the ego vehicle and sensors
            from the selected objects definition file.
        carla_manual_control.launch.py: Starts manual control for the selected
            role name.

    Returns:
        LaunchDescription: Ordered launch actions for bridge startup, ego
        vehicle spawning, and manual control.
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
