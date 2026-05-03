from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    """Create the launch description for starting RViz2 with carla_rviz2 settings.

    This launch file declares configurable arguments for simulation time and
    the RViz configuration file, then starts an ``rviz2`` node using the
    selected configuration. By default, it loads ``carla_rviz2` from the
    ``carla_rviz2`` package and enables simulated time.

    Launch arguments:
        use_sim_time: Whether RViz2 should use simulated time. Defaults to
            ``true``.
        rviz_config: Path to the RViz configuration file. Defaults to
            ``rviz/carla_rviz2` in the ``carla_rviz2`` package.

    Returns:
        LaunchDescription: A ROS 2 launch description containing the declared
        launch arguments and the RViz2 node action.

    """
    # <!-- Packages shared -->
    carla_rviz2_pkg = FindPackageShare('carla_rviz2')

    # <!-- Config arguments -->
    use_sim_time = LaunchConfiguration('use_sim_time')
    rviz_config = LaunchConfiguration('rviz_config')

    rviz_config_path = PathJoinSubstitution(
        [
            carla_rviz2_pkg,
            'rviz',
            'carla_rviz2.rviz'
        ]
    )

    # <!-- Declare arguments -->
    declare_use_sim_time_cmd = DeclareLaunchArgument(
        'use_sim_time',
        default_value='true'
    )

    declare_rviz_config_cmd = DeclareLaunchArgument(
        'rviz_config',
        default_value=rviz_config_path
    )

    # <!-- RViz2 node -->
    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='screen',
        arguments=['-d', rviz_config],
        parameters=[
            {'use_sim_time': use_sim_time}
        ]
    )

    return LaunchDescription(
        [
            declare_use_sim_time_cmd,
            declare_rviz_config_cmd,
            rviz_node
        ]
    )
