from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    """
    Create the launch description for the CARLA scenario manager node.

    The generated launch description declares runtime arguments for CARLA
    connection and parameter-file override, resolves a default parameter file
    path from this package's share directory, and starts the
    ``scenario_manager_node.py`` process.

    Launch arguments:
        host (str): Hostname or IP of the CARLA simulator. Defaults to
            ``"localhost"``.
        port (str): TCP port of the CARLA simulator. Defaults to ``"2000"``.
        timeout (str): CARLA client timeout in seconds. Defaults to ``"5.0"``.
        params_file (str): YAML parameter file path. Defaults to
            ``config/scenario_manager.yaml`` from this package.

    Started nodes:
        scenario_manager_node: Runs package ``carla_scenario_manager``,
            executable ``scenario_manager_node.py``, with parameters loaded from
            ``params_file`` and CLI overrides for host/port/timeout.

    Returns:
        LaunchDescription: Launch actions for argument declaration and scenario
        manager node startup.
    """

    ###########################################################################################################

    # <!-- Shared packages -->
    carla_scenario_manager_pkg = FindPackageShare('carla_scenario_manager')
    ###########################################################################################################

    # <!-- Config arguments -->
    host = LaunchConfiguration('host')
    port = LaunchConfiguration('port')
    timeout = LaunchConfiguration('timeout')
    params_file = LaunchConfiguration('params_file')
    ###########################################################################################################

    # <!-- Paths -->
    params_file_path = PathJoinSubstitution(
        [
            carla_scenario_manager_pkg,
            'config',
            'scenario_manager.yaml'
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
        default_value='5.0'
    )

    declare_params_file_cmd = DeclareLaunchArgument(
        'params_file',
        default_value=params_file_path
    )

    # <!-- Scenario manager node -->
    scenario_manager_node = Node(
        package='carla_scenario_manager',
        executable='scenario_manager_node.py',
        name='carla_scenario_manager',
        output='screen',
        parameters=[
            params_file,
            {
                'carla.host': host,
                'carla.port': port,
                'carla.timeout': timeout
            }
        ]
    )
    ###########################################################################################################

    return LaunchDescription(
        [
            declare_host_cmd,
            declare_port_cmd,
            declare_timeout_cmd,
            declare_params_file_cmd,
            scenario_manager_node
        ]
    )
