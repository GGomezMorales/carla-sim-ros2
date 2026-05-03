from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    """
    Create the launch description for starting RViz2.

    The generated launch description declares the RViz runtime arguments,
    resolves the default RViz configuration path from this package's share
    directory, and starts the ``rviz2`` executable with the selected
    configuration file.

    Launch arguments:
        use_sim_time (str): Whether RViz2 should use simulation time via the
            ``use_sim_time`` parameter. Defaults to ``"true"``.
        rviz_config (str): Path to the RViz2 configuration file passed to RViz
            with ``-d``. Defaults to ``rviz/carla_rviz2.rviz`` from this
            package.

    Started nodes:
        rviz_node: Runs package ``rviz2``, executable ``rviz2``, node name
            ``rviz2``, with ``arguments=['-d', rviz_config]`` and the
            ``use_sim_time`` parameter.

    Returns:
        LaunchDescription: Launch actions for argument declaration and RViz2
        startup.
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
