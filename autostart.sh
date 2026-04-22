#!/bin/bash
set -e

TARGET_USER="${USERNAME:-carla}"
TARGET_HOME="$(getent passwd "$TARGET_USER" | cut -d: -f6)"
BASHRC="${TARGET_HOME}/.bashrc"
BASH_PROFILE="${TARGET_HOME}/.bash_profile"

if [[ -z "$TARGET_HOME" ]]; then
    echo "The user was not found: $TARGET_USER" >&2
    exit 1
fi

mkdir -p "$TARGET_HOME"
touch "$BASHRC" "$BASH_PROFILE"

append_if_missing() {
    local line="$1"
    local file="$2"
    grep -Fqx "$line" "$file" || echo "$line" >> "$file"
}

append_if_missing "source /opt/ros/${ROS_DISTRO}/setup.bash" "$BASHRC"
append_if_missing "alias carla='cd $CARLA_ROOT && ./CarlaUE4.sh -quality-level=Low -RenderOffScreen'" "$BASHRC"
append_if_missing "alias bros='cd ${WS} && colcon build'" "$BASHRC"
append_if_missing "alias dros='cd ${WS} && rosdep update && rosdep install --from-paths src --ignore-src -r -y'" "$BASHRC"
append_if_missing "alias sros='source /opt/ros/${ROS_DISTRO}/setup.bash && source ${WS}/install/setup.bash'" "$BASHRC"
append_if_missing "[[ -f ~/.bashrc ]] && source ~/.bashrc" "$BASH_PROFILE"

chown "${TARGET_USER}:${TARGET_USER}" "$BASHRC" "$BASH_PROFILE"
