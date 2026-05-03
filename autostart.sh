#!/bin/bash
set -e

USERNAME=${USERNAME:-carla}
ROS_DISTRO=${ROS_DISTRO:-humble}
CARLA_ROOT=${CARLA_ROOT:-/home/carla}
WS=${WS:-/carla_ws}

CARLA_USER_HOME="/home/${USERNAME}"
CARLA_BASHRC="${CARLA_USER_HOME}/.bashrc"

append_once() {
    local line="$1"
    local file="$2"
    touch "$file"
    grep -qxF "$line" "$file" || echo "$line" >> "$file"
}

append_block_once() {
    local marker="$1"
    local file="$2"

    mkdir -p "$(dirname "$file")"
    touch "$file"

    if ! grep -qF "$marker" "$file"; then
        cat >> "$file"
    fi
}

setup_aliases() {
    local target="$1"

    append_once 'source /opt/ros/${ROS_DISTRO}/setup.bash' "$target"
    append_once 'export CARLA_ROOT=${CARLA_ROOT:-/home/carla}' "$target"
    append_once 'export WS=${WS:-/carla_ws}' "$target"
    append_once 'export PYTHONPATH=${CARLA_ROOT}/PythonAPI/carla:${PYTHONPATH}' "$target"
    append_once "alias carla='cd \${CARLA_ROOT} && ./CarlaUE4.sh -quality-level=Low -RenderOffScreen'" "$target"
    append_once "alias bros='cd \${WS} && colcon build'" "$target"
    append_once "alias dros='cd \${WS} && rosdep update && rosdep install --from-paths src --ignore-src -r -y'" "$target"
    append_once "alias sros='source /opt/ros/\${ROS_DISTRO}/setup.bash && source \${WS}/install/setup.bash'" "$target"
}

setup_carla_ros2() {
    local target="$1"

    append_block_once '# >>> carla_ros2 helpers >>>' "$target" <<'EOF_BLOCK'

# >>> carla_ros2 helpers >>>
carla_ros2() {
    if [[ "$1" == "rviz2" && -z "$2" ]]; then
        bros && sros && ros2 launch carla_rviz2 rviz2.launch.py
    else
        echo "Use: carla_ros2 [rviz2]"
    fi
}

_carla_ros2() {
    local cur="${COMP_WORDS[COMP_CWORD]}"
    local prev="${COMP_WORDS[COMP_CWORD-1]}"

    if [[ $COMP_CWORD -eq 1 ]]; then
        COMPREPLY=( $(compgen -W "rviz2" -- "$cur") )
    fi
}
complete -F _carla_ros2 carla_ros2
# <<< carla_ros2 helpers <<<
EOF_BLOCK
}

patch_nodes() {
    local waypoint_file="${WS}/src/ros-bridge/carla_waypoint_publisher/src/carla_waypoint_publisher/carla_waypoint_publisher.py"
    local waypoint_url="https://raw.githubusercontent.com/carla-simulator/ros-bridge/master/carla_waypoint_publisher/src/carla_waypoint_publisher/carla_waypoint_publisher.py"
    local planner_file="${WS}/src/ros-bridge/carla_ad_agent/src/carla_ad_agent/local_planner.py"
    local planner_url="https://raw.githubusercontent.com/carla-simulator/ros-bridge/master/carla_ad_agent/src/carla_ad_agent/local_planner.py"

    if [ -f "$waypoint_file" ] && { grep -q 'global_route_planner_dao' "$waypoint_file" || ! grep -q 'from nav_msgs.msg import Path' "$waypoint_file"; }; then
        curl -fsSL "$waypoint_url" -o "$waypoint_file"
    fi

    if [ -f "$planner_file" ] && grep -q 'create_service_client' "$planner_file"; then
        curl -fsSL "$planner_url" -o "$planner_file"
    fi
}

patch_737() {
    local cmake_file="${WS}/src/ros-bridge/pcl_recorder/CMakeLists.txt"
    local header_file="${WS}/src/ros-bridge/pcl_recorder/include/PclRecorderROS2.h"

    if [ -f "$cmake_file" ] && grep -q 'pcl_conversions tf2 tf2_ros)' "$cmake_file"; then
        sed -i 's/pcl_conversions tf2 tf2_ros)/pcl_conversions tf2 tf2_ros tf2_eigen)/g' "$cmake_file"
    fi

    if [ -f "$header_file" ] && grep -q 'tf2_eigen/tf2_eigen.h' "$header_file"; then
        sed -i 's|tf2_eigen/tf2_eigen.h|tf2_eigen/tf2_eigen.hpp|g' "$header_file"
    fi
}

setup_aliases "$CARLA_BASHRC"
setup_aliases /root/.bashrc

setup_carla_ros2 "$CARLA_BASHRC"
setup_carla_ros2 /root/.bashrc

append_once 'source ~/.bashrc' "${CARLA_USER_HOME}/.bash_profile"
append_once 'source ~/.bashrc' /root/.bash_profile

patch_nodes
patch_737

exec "$@"