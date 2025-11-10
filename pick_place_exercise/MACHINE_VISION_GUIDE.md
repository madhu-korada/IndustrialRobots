# Machine Vision Pick & Place Guide

## 🎯 What is Machine Vision Solution?

The machine vision approach uses **3D cameras** and **point cloud processing** to dynamically detect objects in real-time, instead of relying on pre-defined object poses. This is more realistic for industrial applications!

**Key Differences:**
- ✅ **No `/ObjectPose` topics needed** - Uses camera data instead
- ✅ **Dynamic object detection** - Works with any object in camera view
- ✅ **Real perception pipeline** - Processes point clouds, segments objects
- ✅ **Direct LinkAttacher** - Calls `/ATTACHLINK` directly after detection
- ✅ **Complete solution** - Includes HAL API for easier robot control

## 🚀 Quick Start

### Step 1: Stop Current Simulation
If you have a simulation running, stop it with `Ctrl+C`

### Step 2: Launch Machine Vision Environment
```bash
cd ~/yc_demo_folder/dev_ws
source install/setup.bash

# Option A: Using ros2srrc_launch (Recommended)
ros2 launch ros2srrc_launch machine_vision.launch.py

# Option B: Using machine_vision_exercise directly
ros2 launch machine_vision_exercise machine_vision_exercise.launch.py
```

Wait for:
- ✅ Gazebo window opens with robot + cameras
- ✅ RViz opens showing camera views
- ✅ Point cloud visualization appears
- ✅ Terminal shows "You can start planning now!"

### Step 3: Run the Pick & Place Algorithm

In a **new terminal**:
```bash
cd ~/yc_demo_folder/dev_ws
source install/setup.bash

# Run the full solution
ros2 run machine_vision_exercise MyAlgorithm_full_solution.py
```

Or open the Jupyter-style interface (if available):
```bash
# Check if GUI is available
ros2 run machine_vision_exercise MyAlgorithm.py
```

## 📊 What You'll See

### Gazebo View
- UR5 robot with Robotiq gripper
- 3D depth cameras mounted on the robot or workspace
- Colored objects (red cylinder, blue sphere, etc.)
- Robot performing autonomous pick and place

### RViz View
- Point cloud data from 3D cameras
- Detected object markers
- Planned trajectories
- Robot state visualization

### Terminal Output
```
=== MINIMAL PICK AND PLACE OPERATION ===
1. Setting up home position and moving there...
2. Skipping workspace scanning...
3. Moving to pre-pick position...
4. Moving to safe position above object...
5. Linear approach to object...
6. Final approach to object center...
7. Attaching object using link attacher...
✓ Object attached successfully!
8. Lifting object to safe height...
9. Moving to pre-place position...
10. Moving to safe position above target...
11. Linear approach to target...
12. Placing object at target...
13. Detaching object...
✓ Object detached successfully!
14. Retracting from target...
15. Returning to home position...
✓ Pick and place completed successfully!
```

## 🔧 How It Works

### 1. **HAL (Hardware Abstraction Layer)**
Provides high-level robot control functions:
```python
from HAL import (
    MoveAbsJ,        # Move to absolute joint positions
    MoveLinear,      # Linear Cartesian movement
    MoveJoint,       # Move to Cartesian pose
    attach,          # Attach object via LinkAttacher
    detach,          # Detach object
    get_TCP_pose,    # Get end-effector pose
    back_to_home     # Return to home position
)
```

### 2. **PERCEPTION**
Processes 3D camera data:
```python
from PERCEPTION import (
    get_point_cloud,      # Get raw point cloud
    detect_objects,       # Segment and identify objects
    get_object_pose,      # Calculate object position
)
```

### 3. **Direct Attachment**
Instead of checking `/ObjectPose` topics, it directly calls:
```python
# The HAL attach function calls LinkAttacher directly
attach('red_cylinder')  # Attach by object name
detach('red_cylinder')  # Detach by object name
```

This bypasses the need for pose detection - it assumes the robot is already at the object!

## 📁 Key Files

### Algorithm
- **`machine_vision_exercise/MyAlgorithm_full_solution.py`** - Complete working solution
- **`machine_vision_exercise/MyAlgorithm.py`** - Template for your own code
- **`machine_vision_exercise/HAL.py`** - Hardware abstraction layer
- **`machine_vision_exercise/PERCEPTION.py`** - Computer vision functions

### Configuration  
- **`config/sensors_3d.yaml`** - Camera configuration
- **`config/models_info.yaml`** - Object information
- **`config/joints_setup.yaml`** - Joint configuration

### Launch
- **`launch/machine_vision_exercise.launch.py`** - Standalone launch
- **`ros2srrc_launch/moveit2/machine_vision.launch.py`** - Full framework launch

## 🎓 Learning Path

### For Beginners
1. Run `MyAlgorithm_full_solution.py` to see it work
2. Read the code to understand the sequence
3. Try modifying object positions in the code
4. Experiment with different speeds and trajectories

### For Advanced Users
1. Study `PERCEPTION.py` to understand object detection
2. Modify `HAL.py` to add custom robot behaviors
3. Create your own `MyAlgorithm.py` implementation
4. Integrate real camera hardware (when moving to real robot)

## 🆚 Comparison: Machine Vision vs Pre-recorded Programs

| Feature | Machine Vision | Pre-recorded YAML |
|---------|---------------|-------------------|
| **Object Detection** | Dynamic (cameras) | Static (pre-defined) |
| **Flexibility** | High (any object) | Low (specific positions) |
| **Setup Complexity** | High (cameras, PCL) | Low (just world file) |
| **ObjectPose Topics** | Not needed ✅ | Required ❌ |
| **Real-world Ready** | Yes ✅ | No (needs pose system) |
| **Learning Curve** | Steep | Easy |

## 🐛 Troubleshooting

### No camera data in RViz
```bash
# Check if depth camera is publishing
ros2 topic list | grep depth

# Echo camera topic
ros2 topic echo /camera/depth/points --once
```

### LinkAttacher fails
```bash
# Check service is available
ros2 service list | grep ATTACH

# Test manual attachment
ros2 service call /ATTACHLINK linkattacher_msgs/srv/AttachLink \
  "{model1_name: 'ur5', link1_name: 'EE_robotiq_2f85', \
    model2_name: 'red_cylinder', link2_name: 'red_cylinder'}"
```

### Robot doesn't move
```bash
# Check if MoveIt is ready
ros2 topic echo /move_group/status --once

# Verify joint states
ros2 topic echo /joint_states --once
```

### Objects not in scene
```bash
# List Gazebo models
gz model -l

# Check world file has objects
cat ~/yc_demo_folder/dev_ws/src/IndustrialRobots/ros2_SimRealRobotControl/packages/ur5/ros2srrc_ur5_gazebo/worlds/ros2srrc_ur5_machine_vision.world | grep -i "red_cylinder\|blue_sphere"
```

## 💡 Advantages of Machine Vision Approach

1. **Realistic Industrial Application**
   - Real factories use vision systems
   - No assumptions about fixed object positions
   - Can handle object variations

2. **Flexible and Adaptive**
   - Objects can move or be placed anywhere
   - Multiple object types can be handled
   - Lighting and occlusion can be handled (with good algorithms)

3. **No Dependency on ObjectPose Plugin**
   - Doesn't need special URDF plugins
   - Works with any Gazebo objects
   - Camera data is self-contained

4. **Educational Value**
   - Learn computer vision concepts
   - Understand perception pipelines
   - Practice with real ROS 2 tools (PCL, tf2, etc.)

## 📚 Next Steps

After mastering the machine vision solution:

1. **Modify the algorithm** to handle multiple objects
2. **Add object classification** based on color or shape
3. **Implement sorting** - different objects to different locations
4. **Add error recovery** - retry if grasp fails
5. **Optimize trajectories** for faster operation

## 🔗 Related Documentation

- **HAL API**: See `machine_vision_exercise/HAL.py` for available functions
- **Perception**: See `machine_vision_exercise/PERCEPTION.py` for vision functions
- **LinkAttacher**: `/home/madhu/yc_demo_folder/dev_ws/src/IndustrialRobots/IFRA_LinkAttacher/README.md`

---

**Status**: ✅ Ready to use  
**Advantages**: No ObjectPose needed, real-world applicable  
**Best for**: Learning perception-based robotics  
**Difficulty**: Moderate to Advanced

