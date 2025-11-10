# 🚀 Quick Start Guide - UR5 + Robotiq Pick & Place

## 📋 Prerequisites
- ROS 2 Humble installed
- Workspace built: `colcon build`

## ⚡ Launch in 3 Steps

### 1️⃣ Terminal 1: Launch Simulation
```bash
cd ~/yc_demo_folder/dev_ws
source install/setup.bash
ros2 launch pick_place_exercise ur5_robotiq_moveit.launch.py
```

Wait for:
- ✅ Gazebo window opens
- ✅ RViz window opens  
- ✅ Robot appears in both
- ✅ Terminal shows "You can start planning now!"

### 2️⃣ Terminal 2: Verify Setup (Optional but Recommended)
```bash
cd ~/yc_demo_folder/dev_ws
source install/setup.bash

# Should show 8 controllers as [active]
ros2 control list_controllers

# Should output: robotiq_2f85
ros2 param get /move EE_PARAM
```

### 3️⃣ Terminal 2 or 3: Run Pick & Place

**Option A: Single Color Test**
```bash
# Pick green object
ros2 run ros2srrc_execution ExecuteProgram.py ur5_robotiq85_grasp_green_pick.yaml

# Place green object (after pick completes)
ros2 run ros2srrc_execution ExecuteProgram.py ur5_robotiq85_grasp_green_place.yaml
```

**Option B: Automated All Colors**
```bash
ros2 run pick_place_exercise automated_color_sorting
```

## 🎯 What You Should See

### ✅ Success Indicators
- Robot moves through all 5+ steps smoothly
- Gripper opens and closes visibly
- No timeout errors
- Terminal shows each step executing

### ❌ If Something Goes Wrong

**Problem: Controllers not active**
```bash
# Run the fix script
bash ~/yc_demo_folder/dev_ws/src/IndustrialRobots/pick_place_exercise/pick_place_exercise/fix_gripper_controllers.sh
```

**Problem: Gripper commands fail**
```bash
# Check EE_PARAM
ros2 param get /move EE_PARAM
# If "none", restart simulation
```

**Problem: "no ros2_control tag" error**
```bash
# Use the new launch file, not the old one
ros2 launch pick_place_exercise ur5_robotiq_moveit.launch.py
```

## 📊 Program Sequence

When you run a pick program, you'll see:

```
Step 1: [Grasp-Demo]: MoveJ - Go to HomePosition ✅
Step 2: [Grasp-Demo]: Open gripper ✅
Step 3: [Grasp-Demo]: MoveL to green cylinder APROX point ✅
Step 4: [Grasp-Demo]: MoveROT 90º in roll and 90º in yaw ✅
Step 5: [Grasp-Demo]: MoveL to green cylinder PICK point ✅
Step 6: [Grasp-Demo]: Close gripper ✅
```

## 🔧 Available Programs

Located in: `ros2srrc_execution/programs/`

**Pick Programs:**
- `ur5_robotiq85_grasp_green_pick.yaml`
- `ur5_robotiq85_grasp_blue_pick.yaml`
- `ur5_robotiq85_grasp_red_pick.yaml`
- `ur5_robotiq85_grasp_yellow_pick.yaml`

**Place Programs:**
- `ur5_robotiq85_grasp_green_place.yaml`
- `ur5_robotiq85_grasp_blue_place.yaml`
- `ur5_robotiq85_grasp_red_place.yaml`
- `ur5_robotiq85_grasp_yellow_place.yaml`

## 💡 Tips

1. **Always source your workspace** before running commands
2. **Wait for MoveIt to fully load** before sending commands (5-10 seconds)
3. **Check RViz** to see the robot's planning visualization
4. **Watch Gazebo** to see actual execution
5. **Terminal output** shows detailed step-by-step progress

## 📚 More Information

- **Full details**: `LAUNCH_GUIDE.md`
- **Gripper troubleshooting**: `GRIPPER_FIX_GUIDE.md`
- **Complete investigation**: `COMPLETE_SUMMARY.md`
- **Automated sorting**: `AUTOMATED_SORTING_GUIDE.md`

## 🎉 That's It!

Your UR5 + Robotiq 2F-85 pick and place system is ready to go!

---
**Last Updated**: November 10, 2025  
**Status**: ✅ Fully Functional

