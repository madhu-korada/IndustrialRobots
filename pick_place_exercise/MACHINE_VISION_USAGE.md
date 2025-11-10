# Machine Vision Pick & Place - Usage Guide

## Overview

This guide explains how to run the machine vision-based pick and place algorithm using the provided scripts.

## Available Scripts

### 1. `run_full_machine_vision.sh` - Complete Automation
**What it does:**
- Launches the machine vision environment (Gazebo + MoveIt + Controllers)
- Waits for everything to initialize
- Automatically runs the pick & place algorithm
- Keeps the environment running after completion

**When to use:**
- First time running the system
- When starting from scratch
- When you want everything automated

**How to run:**
```bash
cd ~/yc_demo_folder/dev_ws/src/IndustrialRobots/pick_place_exercise
./run_full_machine_vision.sh
```

**Expected behavior:**
1. Opens a new terminal window with the launch output
2. Waits 30 seconds for initialization
3. Runs the algorithm in your current terminal
4. Launch window stays open for inspection/debugging

**To stop:**
- Switch to the "Machine Vision Environment" terminal window
- Press `Ctrl+C` to stop all nodes

---

### 2. `run_algorithm_only.sh` - Algorithm Only
**What it does:**
- Runs just the pick & place algorithm
- Assumes environment is already launched

**When to use:**
- When environment is already running
- For testing algorithm changes
- For running multiple pick & place cycles

**Prerequisites:**
Launch the environment first:
```bash
ros2 launch machine_vision_exercise machine_vision_exercise.launch.py
```

**How to run:**
```bash
cd ~/yc_demo_folder/dev_ws/src/IndustrialRobots/pick_place_exercise
./run_algorithm_only.sh
```

---

### 3. Manual ROS 2 Commands

#### Launch Environment:
```bash
cd ~/yc_demo_folder/dev_ws
source install/setup.bash
ros2 launch machine_vision_exercise machine_vision_exercise.launch.py
```

#### Run Algorithm (in a separate terminal):
```bash
cd ~/yc_demo_folder/dev_ws
source install/setup.bash
ros2 run pick_place_exercise test_machine_vision_safe
```

---

## Algorithm Details

The algorithm uses **vision-based detection** to:
1. Detect object position using camera and point cloud
2. Calculate safe pick and place trajectories
3. Execute motion using MoveIt 2
4. Attach/detach objects using the LinkAttacher service

### Current Configuration (Safe Mode)
- **Object**: Red cylinder
- **Object Position**: `[0.4, 0.0, 1.0]` (safe, centered)
- **Target Position**: `[-0.4, 0.0, 1.0]`
- **Gripper Orientation**: `[0, 80, 0]` (slightly tilted to avoid self-collision)

### Motion Sequence
1. **Home Position** - Start at safe joint configuration
2. **Pre-Pick** - Approach from side
3. **Above Object** - Position gripper above object
4. **Pick** - Lower and attach object
5. **Lift** - Raise object to safe height
6. **Transit** - Move to target area
7. **Above Target** - Position above target
8. **Place** - Lower and release object
9. **Retreat** - Move up from target
10. **Home** - Return to start position

---

## Troubleshooting

### "No executable found"
**Solution:** Rebuild the package
```bash
cd ~/yc_demo_folder/dev_ws
colcon build --packages-select pick_place_exercise
source install/setup.bash
```

### "module 'numpy' has no attribute 'float'"
**Solution:** Upgrade transforms3d
```bash
pip install --upgrade transforms3d
```

### "PLANNING FAILED" - Self-collision
**Solution:** The safe version (`test_machine_vision_safe`) is already configured to avoid this. If still happening:
1. Check object positions in the script
2. Verify robot is at home position before starting
3. Check for obstacles in the workspace

### Robot not moving
**Check these:**
1. Is MoveIt running? Look for `[move_group]` in logs
2. Are controllers loaded? Run: `ros2 control list_controllers`
3. Is robot in a valid state? Check RViz

### Gazebo crash
**Common causes:**
1. Another Gazebo instance running: `killall -9 gzserver gzclient`
2. Models not found: Verify `GAZEBO_MODEL_PATH` is set in launch file

---

## Customizing the Algorithm

### Change Object/Target Positions
Edit: `pick_place_exercise/pick_place_exercise/simple_machine_vision_test.py`

```python
# Object and target positions
object_pos = [0.4, 0.0, 1.0]       # Adjust X, Y, Z
target_pos = [-0.4, 0.0, 1.0]      # Adjust X, Y, Z

# Gripper orientation
safe_orientation = [0, 80, 0]      # Yaw, Pitch, Roll (degrees)
```

### Change Motion Speeds
Edit the speed parameters in motion commands:
```python
MoveJoint(position, orientation, speed=0.3, timeout=2.0)
MoveLinear(position, orientation, speed=0.1, timeout=1.5)
```

### Add More Objects
1. Detect object using color/shape filters
2. Get position using `perception.get_object_position()`
3. Add to motion sequence

---

## Advanced Usage

### Run Full Solution (with dynamic detection)
This version uses actual camera-based detection:
```bash
ros2 run pick_place_exercise run_machine_vision
```

**Note:** This requires:
- Camera topics to be publishing
- Point cloud processing to be working
- Object models to be properly configured

### Debug Mode
Add verbose output to see detailed motion planning:
```bash
ros2 launch machine_vision_exercise machine_vision_exercise.launch.py log_level:=debug
```

---

## Quick Reference

### One-Command Full Run
```bash
cd ~/yc_demo_folder/dev_ws/src/IndustrialRobots/pick_place_exercise && ./run_full_machine_vision.sh
```

### Stop Everything
```bash
killall -9 gzserver gzclient ros2
```

### Check System Status
```bash
# List active nodes
ros2 node list

# List controllers
ros2 control list_controllers

# Check topics
ros2 topic list

# Monitor joint states
ros2 topic echo /joint_states
```

---

## Performance Tips

1. **First run is slow** - Gazebo loads models, MoveIt builds planning scene
2. **Subsequent runs are faster** - Keep environment running, only run algorithm
3. **Planning failures** - Increase timeout values in motion commands
4. **Smoother motion** - Reduce speed parameters (slower = more reliable)

---

## Getting Help

If you encounter issues:

1. **Check the logs** - Error messages usually indicate the problem
2. **Verify prerequisites** - Make sure all controllers are loaded
3. **Test incrementally** - Use `run_algorithm_only.sh` for quick iterations
4. **Reset if stuck** - Kill all processes and start fresh with `run_full_machine_vision.sh`

---

## Summary

**Quickest way to see it work:**
```bash
./run_full_machine_vision.sh
```

**For iterative testing:**
```bash
# Terminal 1 (keep running):
ros2 launch machine_vision_exercise machine_vision_exercise.launch.py

# Terminal 2 (run repeatedly):
./run_algorithm_only.sh
```

Good luck with your pick and place operations! 🤖

