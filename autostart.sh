#!/bin/bash

CARLA_USER_HOME="/home/${USERNAME:-carla}"
CARLA_BASHRC="${CARLA_USER_HOME}/.bashrc"

setup_aliases() {
    local target="$1"
    echo "source /opt/ros/${ROS_DISTRO}/setup.bash" >> "$target"
    echo "alias carla='cd \$CARLA_ROOT && ./CarlaUE4.sh -quality-level=Low -RenderOffScreen'" >> "$target"
    echo "alias bros='cd \${WS} && colcon build'" >> "$target"
    echo "alias dros='cd \${WS} && rosdep update && rosdep install --from-paths src --ignore-src -r -y'" >> "$target"
    echo "alias sros='source /opt/ros/\${ROS_DISTRO}/setup.bash && source \${WS}/install/setup.bash'" >> "$target"
    echo "alias apt='sudo apt'" >> "$target"
}

setup_aliases "${CARLA_BASHRC}"
setup_aliases /root/.bashrc

echo "source ~/.bashrc" >> "${CARLA_USER_HOME}/.bash_profile"
echo "source ~/.bashrc" >> /root/.bash_profile

exec "$@"
