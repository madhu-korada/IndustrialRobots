#!/bin/bash

# Run just the algorithm (assumes environment is already launched)

echo "================================================================================"
echo "Running Machine Vision Pick & Place Algorithm"
echo "================================================================================"
echo ""
echo "Prerequisites:"
echo "  - Machine vision environment must already be running"
echo "  - Launch it first with: ros2 launch machine_vision_exercise machine_vision_exercise.launch.py"
echo ""
echo "================================================================================"
echo ""

cd ~/yc_demo_folder/dev_ws
source install/setup.bash

# Run the FULL algorithm with main() from MyAlgorithm_full_solution.py
ros2 run pick_place_exercise run_machine_vision

if [ $? -eq 0 ]; then
    echo ""
    echo "================================================================================"
    echo "✓ Algorithm completed successfully!"
    echo "================================================================================"
else
    echo ""
    echo "================================================================================"
    echo "✗ Algorithm failed - check logs above"
    echo "================================================================================"
fi

