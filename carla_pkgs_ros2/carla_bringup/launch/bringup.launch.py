from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, ExecuteProcess, IncludeLaunchDescription, TimerAction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    """
    Create the complete CARLA bringup launch description.

    The generated launch description declares the public arguments for the
    top-level bringup entry point, resolves package-share paths, includes the
    RViz2 and CARLA bridge/ego-vehicle launch files, delays the waypoint
    publisher to allow the simulation stack to initialize, and starts two
    repeating ``ros2 topic pub`` processes for target commands.

    Launch arguments:
        use_sim_time (str): Whether RViz2 should use simulated ROS time.
            Defaults to ``"true"``.
        rviz_config (str): RViz2 configuration file to load. Defaults to
            ``rviz/carla_rviz2.rviz`` from the ``carla_bringup`` package.
        town (str): CARLA town/map name forwarded to the bridge launcher.
            Defaults to ``"Town01"``.

    Included launch files:
        carla_ros_bridge_with_example_ego_vehicle.launch.py: Starts the CARLA
            ROS bridge, spawns the exampe ego vehicle, and starts manual
            control through the local intermediate launcher.
        rviz2.launch.py: Starts RViz2 from the ``carla_rviz2`` package.
        carla_waypoint_publisher.launch.py: Starts waypoint publishing after
            the configured timer delay.

    Started processes:
        target_speed_pub: Publishes ``std_msgs/msg/Float64`` commands to
            ``/carla/ego_vehicle/target_speed`` at 1 Hz.
        target_point_pub: Publishes ``geometry_msgs/msg/PoseStamped`` goals to
            ``/carla/ego_vehicle/goal`` at 0.05 Hz.

    Returns:
        LaunchDescription: Ordered launch actions for the complete CARLA
        visualization and ego-vehicle bringup stack.
    """

    ###########################################################################################################

    # <!-- Shared packages -->
    carla_bringup_pkg = FindPackageShare('carla_bringup')
    carla_rviz2_pkg = FindPackageShare('carla_rviz2')
    carla_waypoint_publisher_pkg = FindPackageShare('carla_waypoint_publisher')
    ###########################################################################################################

    # <!-- Config arguments -->
    use_sim_time = LaunchConfiguration('use_sim_time')
    rviz_config = LaunchConfiguration('rviz_config')
    town = LaunchConfiguration('town')
    ###########################################################################################################

    # <!-- Paths -->
    rviz_config_path = PathJoinSubstitution(
        [
            carla_bringup_pkg,
            'rviz',
            'carla_rviz2.rviz'
        ]
    )

    rviz_launch_path = PathJoinSubstitution(
        [
            carla_rviz2_pkg,
            'launch',
            'rviz2.launch.py'
        ]
    )

    carla_ros_bridge_with_example_ego_vehicle_launch_path = PathJoinSubstitution(
        [
            carla_bringup_pkg,
            'launch',
            'carla_ros_bridge_with_example_ego_vehicle.launch.py'
        ]
    )

    waypoint_publisher_launch_path = PathJoinSubstitution(
        [
            carla_waypoint_publisher_pkg,
            'carla_waypoint_publisher.launch.py'
        ]
    )
    ###########################################################################################################

    # <!-- Declare arguments -->
    declare_use_sim_time_cmd = DeclareLaunchArgument(
        'use_sim_time',
        default_value='true'
    )

    declare_rviz_config_cmd = DeclareLaunchArgument(
        'rviz_config',
        default_value=rviz_config_path
    )

    declare_town_cmd = DeclareLaunchArgument(
        'town',
        default_value="Town01"
    )
    ###########################################################################################################

    # <!-- carla_ros_bridge_with_example_ego_vehicle launcher -->
    carla_ros_bridge_with_example_ego_vehicle_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            carla_ros_bridge_with_example_ego_vehicle_launch_path
        ),
        launch_arguments={
            'town': town,
        }.items()
    )

    # <!-- Waypoint publisher launcher -->
    waypoint_publisher_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            waypoint_publisher_launch_path
        )
    )

    # <!-- Delayed waypoint publisher launcher -->
    delayed_waypoint_publisher_launch = TimerAction(
        period=8.0,
        actions=[
            waypoint_publisher_launch
        ]
    )

    # <!-- Target speed publisher -->
    target_speed_pub = ExecuteProcess(
        cmd=[
            'ros2', 'topic', 'pub',
            '/carla/ego_vehicle/target_speed',
            'std_msgs/msg/Float64',
            '{data: 10.0}',
            '-r', '1'
        ],
        output='screen'
    )

    # <!-- Target point publisher -->
    target_point_pub = ExecuteProcess(
        cmd=[
            'ros2', 'topic', 'pub',
            '/carla/ego_vehicle/goal',
            'geometry_msgs/msg/PoseStamped',
            "{header: {frame_id: 'map'}, pose: {position: {x: 50.0, y: 0.0, z: 0.0}, orientation: {w: 1.0}}}",
            '-r', '0.05'
        ],
        output='screen'
    )

    # <!-- RViz2 launcher -->
    rviz_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            rviz_launch_path
        ),
        launch_arguments={
            'use_sim_time': use_sim_time,
            'rviz_config': rviz_config
        }.items()
    )
    ###########################################################################################################

    return LaunchDescription(
        [
            declare_use_sim_time_cmd,
            declare_rviz_config_cmd,
            declare_town_cmd,
            rviz_launch,
            carla_ros_bridge_with_example_ego_vehicle_launch,
            delayed_waypoint_publisher_launch,
            target_speed_pub,
            target_point_pub
        ]
    )
