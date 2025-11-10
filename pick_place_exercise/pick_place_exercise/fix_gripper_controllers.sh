#!/bin/bash

###############################################################################
# Robotiq 2F-85 Gripper Controller Fix Script
# This script loads and activates all 6 gripper controllers
###############################################################################

echo "================================================================================"
echo "   ROBOTIQ 2F-85 GRIPPER CONTROLLER LOADER"
echo "================================================================================"
echo ""

# Define all gripper controllers
CONTROLLERS=(
    "robotiq_controller_LKJ"
    "robotiq_controller_RKJ"
    "robotiq_controller_LIKJ"
    "robotiq_controller_RIKJ"
    "robotiq_controller_LFTJ"
    "robotiq_controller_RFTJ"
)

echo "Step 1: Checking current controller status..."
echo "--------------------------------------------------------------------------------"
ros2 control list_controllers
echo ""

echo "Step 2: Loading and activating gripper controllers..."
echo "--------------------------------------------------------------------------------"

# Use the spawner command to load and activate all controllers at once
ros2 run controller_manager spawner \
    robotiq_controller_LKJ \
    robotiq_controller_RKJ \
    robotiq_controller_LIKJ \
    robotiq_controller_RIKJ \
    robotiq_controller_LFTJ \
    robotiq_controller_RFTJ \
    -c /controller_manager

echo ""
echo "Step 3: Verifying all controllers are active..."
echo "--------------------------------------------------------------------------------"
ros2 control list_controllers

echo ""
echo "Step 4: Checking hardware interface claims..."
echo "--------------------------------------------------------------------------------"
ros2 control list_hardware_interfaces | grep robotiq | grep claimed

echo ""
echo "================================================================================"
echo "   GRIPPER SETUP COMPLETE!"
echo "================================================================================"
echo ""
echo "✓ All gripper controllers should now be active"
echo "✓ You can now run: ros2 run ros2srrc_execution ExecuteProgram.py <program.yaml>"
echo ""

