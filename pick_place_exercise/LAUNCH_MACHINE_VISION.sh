#!/bin/bash

###############################################################################
# Machine Vision Pick & Place Launch Script
# This launches the complete machine vision environment
###############################################################################

echo "================================================================================"
echo "   LAUNCHING MACHINE VISION PICK & PLACE ENVIRONMENT"
echo "================================================================================"
echo ""

# Source the workspace
cd ~/yc_demo_folder/dev_ws
source install/setup.bash

# Set Gazebo model path
export GAZEBO_MODEL_PATH=~/yc_demo_folder/dev_ws/src/IndustrialRobots/ros2_SimRealRobotControl/packages/ur5/ros2srrc_ur5_gazebo/models:$GAZEBO_MODEL_PATH

echo "Configuration:"
echo "  - Robot: UR5"
echo "  - End-Effector: Robotiq 2F-85"
echo "  - Cameras: 3D Depth Cameras"
echo "  - World: Machine Vision World"
echo ""

echo "Launching environment..."
echo "Please wait for Gazebo and RViz to fully load (30-60 seconds)"
echo ""

# Launch the machine vision environment
ros2 launch machine_vision_exercise machine_vision_exercise.launch.py

echo ""
echo "================================================================================"
echo "   LAUNCH COMPLETE"
echo "================================================================================"

