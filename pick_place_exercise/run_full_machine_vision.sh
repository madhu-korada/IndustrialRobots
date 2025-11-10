#!/bin/bash

# Full Machine Vision Pick & Place Script
# This script launches the environment and runs the algorithm

set -e  # Exit on error

echo "================================================================================"
echo "MACHINE VISION PICK & PLACE - FULL AUTOMATION"
echo "================================================================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Source ROS 2 workspace
echo -e "${YELLOW}Step 1: Sourcing ROS 2 workspace...${NC}"
cd ~/yc_demo_folder/dev_ws
source install/setup.bash
echo -e "${GREEN}✓ Workspace sourced${NC}"
echo ""

# Launch the machine vision environment in background
echo -e "${YELLOW}Step 2: Launching machine vision environment...${NC}"
echo "This will start Gazebo, MoveIt, and all necessary nodes"
echo ""

# Use gnome-terminal to launch in a separate window (so logs are visible)
gnome-terminal --title="Machine Vision Environment" -- bash -c "
cd ~/yc_demo_folder/dev_ws
source install/setup.bash
ros2 launch machine_vision_exercise machine_vision_exercise.launch.py
" &

LAUNCH_PID=$!
echo -e "${GREEN}✓ Launch started (PID: $LAUNCH_PID)${NC}"
echo ""

# Wait for the system to be ready
echo -e "${YELLOW}Step 3: Waiting for system to be ready...${NC}"
echo "Waiting 30 seconds for Gazebo, MoveIt, and controllers to initialize..."
echo ""

for i in {30..1}; do
    echo -ne "Time remaining: $i seconds...\r"
    sleep 1
done
echo -e "\n${GREEN}✓ System should be ready${NC}"
echo ""

# Add obstacles to planning scene
echo "================================================================================"
echo -e "${YELLOW}Step 4: Adding obstacles to MoveIt planning scene...${NC}"
echo "================================================================================"
echo ""
echo "Adding conveyor and storage rack to planning scene..."
ros2 run pick_place_exercise add_planning_scene_objects
echo ""
echo -e "${GREEN}✓ Planning scene updated${NC}"
echo "Waiting 3 seconds for changes to propagate..."
sleep 3
echo ""

# Start target visualizer in background
echo "================================================================================"
echo -e "${YELLOW}Step 5: Starting target position visualizer...${NC}"
echo "================================================================================"
echo ""
echo "Publishing target markers to /target_markers for RViz visualization..."
ros2 run pick_place_exercise visualize_targets &
VISUALIZER_PID=$!
echo -e "${GREEN}✓ Target visualizer started (PID: $VISUALIZER_PID)${NC}"
echo ""
echo "To view targets in RViz:"
echo "  1. Open RViz (if not already open)"
echo "  2. Click 'Add' -> 'By topic'"
echo "  3. Select '/target_markers' -> MarkerArray"
echo "  4. You should see green spheres at each target position"
echo ""
sleep 2
echo ""

# Run the algorithm
echo "================================================================================"
echo -e "${YELLOW}Step 6: Running the pick & place algorithm...${NC}"
echo "================================================================================"
echo ""

# Run the FULL algorithm with main() from MyAlgorithm_full_solution.py
ros2 run pick_place_exercise run_machine_vision

# Check if successful
if [ $? -eq 0 ]; then
    echo ""
    echo "================================================================================"
    echo -e "${GREEN}✓ ALGORITHM COMPLETED SUCCESSFULLY!${NC}"
    echo "================================================================================"
    echo ""
    echo "Check Gazebo to verify the object was picked and placed correctly."
    echo ""
    echo "To run again, press Ctrl+C in the launch window, then re-run this script."
else
    echo ""
    echo "================================================================================"
    echo -e "${RED}✗ ALGORITHM FAILED${NC}"
    echo "================================================================================"
    echo ""
    echo "Check the logs above for error details."
    echo "The launch window is still running - press Ctrl+C there to stop it."
fi

echo ""
echo "Launch window is still running. To stop it:"
echo "  1. Switch to the 'Machine Vision Environment' terminal window"
echo "  2. Press Ctrl+C to stop all nodes"
echo ""

