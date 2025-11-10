# Automated Color Sorting Guide

## Quick Start

### 1. Launch the Simulation with UR5

First, start the robot simulation with Gazebo and MoveIt:

```bash
cd /home/madhu/yc_demo_folder/dev_ws
source install/setup.bash

# Kill any existing Gazebo processes
killall -9 gzserver gzclient

# Set the Gazebo model path
export GAZEBO_MODEL_PATH=/home/madhu/yc_demo_folder/dev_ws/src/IndustrialRobots/ros2_SimRealRobotControl/packages/ur5/ros2srrc_ur5_gazebo/models

# Launch the robot (use ur5_2 for simpler configuration without linear axis)
ros2 launch ros2srrc_launch moveit2_robot.launch.py package:=ros2srrc_ur5 config:=ur5_2
```

Wait until you see:
- ✓ Gazebo opens with the robot
- ✓ RViz opens with MoveIt interface
- ✓ Controllers are loaded and active

### 2. Run the Automated Color Sorting

In a **new terminal**, run:

```bash
cd /home/madhu/yc_demo_folder/dev_ws
source install/setup.bash

# Run the automated sorting script
ros2 run pick_place_exercise automated_color_sorting
```

## What It Does

The script will automatically:
1. **Pick RED** object → Place in RED container
2. **Pick GREEN** object → Place in GREEN container  
3. **Pick BLUE** object → Place in BLUE container
4. **Pick YELLOW** object → Place in YELLOW container
5. Return robot to HOME position

## Expected Output

```
[color_sorting_node]: Waiting for Sequence action server...
[color_sorting_node]: ✓ Connected to Sequence action server

============================================================
Starting Automated Color Sorting
============================================================

--- Object 1/4: RED ---
[color_sorting_node]: Step 1/2: Picking red object...
[color_sorting_node]: Executing: ur5_robotiq85_grasp_red_pick.yaml
[color_sorting_node]: ✓ ur5_robotiq85_grasp_red_pick.yaml completed successfully
[color_sorting_node]: Step 2/2: Placing red object in red container...
[color_sorting_node]: Executing: ur5_robotiq85_grasp_red_place.yaml
[color_sorting_node]: ✓ ur5_robotiq85_grasp_red_place.yaml completed successfully

... (continues for all colors)

============================================================
✓ Color Sorting Complete! All objects sorted.
============================================================

🎉 Mission accomplished! All colored objects have been sorted.
```

## Troubleshooting

### Issue: Programs not executing
**Solution:** 
- Make sure the robot simulation is fully launched with all controllers active
- Ensure the `ros2srrc_execution` package is properly built and sourced
- Verify the YAML program files exist in the `ros2srrc_execution/programs/` directory

### Issue: "Failed to pick/place object"
**Solution:** 
- Check that objects are in their expected positions in Gazebo
- Verify the robot can reach the pick/place positions
- Check for collision warnings in the terminal

### Issue: Robot moves but doesn't grasp
**Solution:**
- The gripper controller may not be loaded
- Check controller status: `ros2 control list_controllers`
- Verify Gazebo link attacher plugin is loaded

## Advanced Usage

### Running Individual Pick/Place Operations

You can run individual programs manually using the ExecuteProgram.py script:

```bash
# Pick just the blue object
ros2 run ros2srrc_execution ExecuteProgram.py package:=ros2srrc_execution program:=ur5_robotiq85_grasp_blue_pick

# Place the blue object
ros2 run ros2srrc_execution ExecuteProgram.py package:=ros2srrc_execution program:=ur5_robotiq85_grasp_blue_place

# Return to home
ros2 run ros2srrc_execution ExecuteProgram.py package:=ros2srrc_execution program:=ur5_robotiq85_grasp_home
```

### Available Programs

Located in: `ros2_SimRealRobotControl/ros2srrc_execution/programs/`

- `ur5_robotiq85_grasp_red_pick.yaml` / `ur5_robotiq85_grasp_red_place.yaml`
- `ur5_robotiq85_grasp_green_pick.yaml` / `ur5_robotiq85_grasp_green_place.yaml`
- `ur5_robotiq85_grasp_blue_pick.yaml` / `ur5_robotiq85_grasp_blue_place.yaml`
- `ur5_robotiq85_grasp_yellow_pick.yaml` / `ur5_robotiq85_grasp_yellow_place.yaml`
- `ur5_robotiq85_grasp_home.yaml`

## Modifying the Script

The script is located at:
```
pick_place_exercise/pick_place_exercise/automated_color_sorting.py
```

You can customize:
- Order of colors to sort
- Add delays between operations
- Implement error recovery
- Add custom logging

After modifications, rebuild:
```bash
cd /home/madhu/yc_demo_folder/dev_ws
colcon build --packages-select pick_place_exercise
source install/setup.bash
```

## Next Steps: Machine Vision Solution

For a more advanced solution using computer vision to detect and sort objects dynamically, check out:
- `machine_vision_exercise/machine_vision_exercise/MyAlgorithm_full_solution.py`

This uses 3D cameras and real-time object detection instead of pre-programmed trajectories.

