# Robotiq 2F-85 Gripper Controller Fix Guide

## Problem Summary

The `moveit2_robot.launch.py` launch file was **NOT loading the gripper controllers** automatically, causing all gripper commands (OPEN/CLOSE) to fail silently. This meant:
- ✗ Step 1 (MoveJ home) worked
- ✗ Step 2+ (gripper open, MoveL, MoveROT) all failed/timed out

## Root Cause

The gripper controllers were defined in the URDF and configuration files, but the launch file's controller spawning logic had an issue that prevented them from being loaded during startup.

**Expected Controllers** (6 total for Robotiq 2F-85):
1. `robotiq_controller_LKJ` - Left Knuckle Joint
2. `robotiq_controller_RKJ` - Right Knuckle Joint  
3. `robotiq_controller_LIKJ` - Left Inner Knuckle Joint
4. `robotiq_controller_RIKJ` - Right Inner Knuckle Joint
5. `robotiq_controller_LFTJ` - Left Finger Tip Joint
6. `robotiq_controller_RFTJ` - Right Finger Tip Joint

## Quick Fix (Current Session)

Run this command in a terminal **while your simulation is running**:

```bash
cd ~/yc_demo_folder/dev_ws
source install/setup.bash
ros2 run controller_manager spawner \
    robotiq_controller_LKJ \
    robotiq_controller_RKJ \
    robotiq_controller_LIKJ \
    robotiq_controller_RIKJ \
    robotiq_controller_LFTJ \
    robotiq_controller_RFTJ \
    -c /controller_manager
```

Or use the provided script:

```bash
bash ~/yc_demo_folder/dev_ws/src/IndustrialRobots/pick_place_exercise/pick_place_exercise/fix_gripper_controllers.sh
```

## Verify Fix Worked

Check that all controllers are active:

```bash
ros2 control list_controllers
```

You should see all 8 controllers as `[active]`:
- joint_state_broadcaster
- joint_trajectory_controller
- robotiq_controller_LKJ
- robotiq_controller_RKJ
- robotiq_controller_LIKJ
- robotiq_controller_RIKJ
- robotiq_controller_LFTJ
- robotiq_controller_RFTJ

## Test Gripper Operation

Test gripper open:
```bash
ros2 action send_goal /Move ros2srrc_data/action/Move \
  "{action: 'MoveG', speed: 1.0, moveg: 0.0}" --feedback
```

Test gripper close (50%):
```bash
ros2 action send_goal /Move ros2srrc_data/action/Move \
  "{action: 'MoveG', speed: 1.0, moveg: 50.0}" --feedback
```

## Now Run Your Pick and Place Programs

Once the gripper controllers are active, you can run the automated sorting:

```bash
cd ~/yc_demo_folder/dev_ws
source install/setup.bash
ros2 run ros2srrc_execution ExecuteProgram.py ur5_robotiq85_grasp_green_pick.yaml
```

Or the automated color sorting script:

```bash
ros2 run pick_place_exercise automated_color_sorting
```

## Permanent Fix (TODO)

The launch file needs to be modified to automatically spawn these controllers. The issue is in:
- `/home/madhu/yc_demo_folder/dev_ws/src/IndustrialRobots/ros2_SimRealRobotControl/ros2srrc_launch/moveit2/moveit2_robot.launch.py`

Specifically around lines 259-271 where the `EE` controllers should be spawned. The logic that determines whether to load them appears to have an issue.

### Reference Working Implementation

Other launch files in the `ros2srrc_launch` package (like `simulation.launch.py`, `moveit2.launch.py`) correctly implement gripper controller loading using:

```python
# EE CONTROLLERS:
if EE == "true":
    CONTROLLERS = GetEEctr(CONFIGURATION["ee"])
    CONTROLLER_NODES = []

    for x in CONTROLLERS:
        CONTROLLER_NODES.append(
            Node(
                package="controller_manager",
                executable="spawner",
                arguments=[x, "-c", "/controller_manager"],
            )
        )
```

Then these nodes are added to the launch description with proper event sequencing.

## Files Created for Diagnosis/Fix

1. **`test_gripper_setup.py`** - Python diagnostic script
2. **`fix_gripper_controllers.sh`** - Bash script to quickly load controllers
3. **`GRIPPER_FIX_GUIDE.md`** - This guide

## Additional Notes

- The gripper hardware interfaces exist in Gazebo and are functional
- The controller configuration files (`controller.yaml`, `controller_moveit2.yaml`) are correct
- The URDF properly defines all 6 gripper joints
- The issue is **only** in the launch file's controller spawning logic

---

**Author**: AI Assistant  
**Date**: November 10, 2025  
**Status**: ✅ Workaround available, permanent fix pending

