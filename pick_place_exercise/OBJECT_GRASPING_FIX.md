# Object Grasping Fix Guide

## 🔴 Problem

**Symptom**: Gripper closes mechanically but doesn't grip objects. Objects stay in place or deform while gripper moves empty to goal location.

**Root Cause**: Objects don't have the `ros2_objectpose` plugin, so the `/ObjectPose` topic is never published. Without this, the parallel gripper can't detect objects to attach them.

## 📊 How Object Grasping Works

The parallel gripper attachment system requires 3 components:

### 1. `/ATTACHLINK` Service ✅ (Working)
- Provided by `IFRA_LinkAttacher` package
- Creates a fixed joint between gripper and object in Gazebo
- **Status**: Running in your simulation

### 2. `/Robpose` Topic ✅ (Working)  
- Publishes end-effector position
- **Status**: Active

### 3. `/ObjectPose` Topic ❌ **(MISSING!)**
- Publishes object positions in world frame
- Required by `parallelGripper.py` to detect objects
- **Status**: **NOT RUNNING** - This is the problem!

## 🔍 What the Gripper Code Does

From `parallelGripper.py` (lines 311-350):

```python
if self.OLCheck:  # If object list provided
    # Get object and gripper poses
    Objects = self.objPoseClient.getOBJECTS()  # Needs /ObjectPose topic!
    EEPose = self.eePoseClient.getEEPose()
    
    # Check if any object is within 0.01m of gripper
    for x in Objects:
        Check = True
        if (EEPose.x - 0.01 > x.x) or (EEPose.x + 0.01 < x.x): 
            Check = False
        if (EEPose.y - 0.01 > x.y) or (EEPose.y + 0.01 < x.y): 
            Check = False
        if (EEPose.z - 0.01 > x.z) or (EEPose.z + 0.01 < x.z): 
            Check = False
        
        if Check == True:
            objNAME = x.objectname
            break
    
    # If object in range, attach it
    if Check:
        AttRES = self.LinkAttacher.ATTACH(objNAME)  # Calls /ATTACHLINK service
```

**Without `/ObjectPose`:**
- `getOBJECTS()` returns empty list or stale data
- `Check` always fails
- `/ATTACHLINK` never called
- Object never attaches!

## ✅ Solution Options

### Option 1: Use Machine Vision Solution (Recommended)

The `machine_vision_exercise` demonstrates a working pick-and-place with dynamic object detection using cameras and perception, not requiring pre-defined object poses.

**Files**:
- `machine_vision_exercise/machine_vision_exercise/MyAlgorithm_full_solution.py`
- Uses 3D point cloud processing
- Dynamically detects object positions
- More realistic approach

**To test**:
```bash
ros2 launch ros2srrc_launch machine_vision.launch.py package:=ros2srrc_ur5 config:=ur5_2
```

### Option 2: Add ObjectPose Plugin to Objects

Objects need the `ros2_objectpose` plugin in their URDF files.

**Required in each object URDF** (e.g., `green_cylinder.urdf`):
```xml
<?xml version="1.0"?>
<robot name="green_cylinder">
  
  <!-- Object geometry and properties -->
  <link name="green_cylinder">
    <visual>
      <geometry>
        <cylinder radius="0.05" length="0.1"/>
      </geometry>
      <material name="green">
        <color rgba="0 1 0 1"/>
      </material>
    </visual>
    <collision>
      <geometry>
        <cylinder radius="0.05" length="0.1"/>
      </geometry>
    </collision>
    <inertial>
      <mass value="0.1"/>
      <inertia ixx="0.001" ixy="0" ixz="0" iyy="0.001" iyz="0" izz="0.001"/>
    </inertial>
  </link>
  
  <!-- ObjectPose Plugin -->
  <gazebo>
    <plugin name="ros2_objectpose_plugin" filename="libros2_objectpose_plugin.so">
      <ros>
        <namespace>green_cylinder_small</namespace>
      </ros>
    </plugin>
  </gazebo>
  
</robot>
```

**Then spawn objects with pose tracking**:
```bash
ros2 run ros2_objectpose SpawnObject.py \
  --package "pick_place_exercise" \
  --urdf "green_cylinder.urdf" \
  --name "green_cylinder_small" \
  --x 0.5 --y 0.0 --z 0.1
```

**Verify object pose is published**:
```bash
ros2 topic echo /green_cylinder_small/ObjectPose
```

### Option 3: Use Pre-configured ros2srrc_ur5 World

The `ros2_SimRealRobotControl` package has worlds with objects already configured.

**Check if objects exist in world**:
```bash
# List models in current world
gz model list

# Or check what's in the ur5 world file
cat ~/yc_demo_folder/dev_ws/src/IndustrialRobots/ros2_SimRealRobotControl/packages/ur5/ros2srrc_ur5_gazebo/worlds/ros2srrc_ur5.world
```

## 🧪 Quick Test - Verify Object Pose Publishing

After spawning objects properly:

```bash
# Terminal 1: Check what ObjectPose topics exist
ros2 topic list | grep ObjectPose

# Should see (for example):
# /green_cylinder_small/ObjectPose
# /blue_sphere_small/ObjectPose
# /red_box_small/ObjectPose
# /yellow_box_small/ObjectPose

# Terminal 2: Echo one object's pose
ros2 topic echo /green_cylinder_small/ObjectPose

# Should output:
# objectname: green_cylinder_small
# x: 0.5
# y: 0.0
# z: 0.1
# qx: 0.0
# ...
```

## 📋 Current Setup Analysis

**Your simulation has**:
- ✅ `/ATTACHLINK` service
- ✅ `/DETACHLINK` service  
- ✅ `/Robpose` topic
- ✅ `gazebo_link_attacher` node
- ✅ Gripper controllers (after our fix)
- ❌ `/ObjectPose` topics for objects
- ❌ Objects with pose tracking plugin

## 🎯 Recommended Action Plan

### Short Term (Quick Test)
1. Use the `machine_vision_exercise` solution which doesn't rely on `/ObjectPose`
2. Or manually test attachment service:
   ```bash
   # Manually attach green_cylinder to gripper
   ros2 service call /ATTACHLINK linkattacher_msgs/srv/AttachLink \
     "{model1_name: 'ur5', link1_name: 'EE_robotiq_2f85', \
       model2_name: 'green_cylinder_small', link2_name: 'green_cylinder_small'}"
   ```

### Long Term (Proper Solution)
1. **Create object URDFs with ObjectPose plugin** for:
   - `green_cylinder_small.urdf`
   - `blue_sphere_small.urdf`
   - `red_box_small.urdf`  
   - `yellow_box_small.urdf`

2. **Spawn objects programmatically** in launch file or separate node

3. **Update YAML programs** to list exact object names:
   ```yaml
   Specifications:
     Robot: "ur5"
     EndEffector: "ParallelGripper"
     EELink: "EE_robotiq_2f85"
     Objects: ["blue_sphere_small", "red_box_small", "yellow_box_small", "green_cylinder_small"]
   ```

4. **Verify all objects publish poses** before running pick/place

## 🐛 Debugging Commands

```bash
# Check if ObjectPose messages are being received
ros2 topic hz /green_cylinder_small/ObjectPose

# Check LinkAttacher plugin status
ros2 node info /gazebo_link_attacher

# Test manual attachment
ros2 service call /ATTACHLINK linkattacher_msgs/srv/AttachLink \
  "{model1_name: 'ur5', link1_name: 'EE_robotiq_2f85', \
    model2_name: 'green_cylinder_small', link2_name: 'green_cylinder_small'}"

# Test manual detachment
ros2 service call /DETACHLINK linkattacher_msgs/srv/DetachLink \
  "{model1_name: 'ur5', link1_name: 'EE_robotiq_2f85', \
    model2_name: 'green_cylinder_small', link2_name: 'green_cylinder_small'}"
```

## 📚 References

- **IFRA_ObjectPose**: `/home/madhu/yc_demo_folder/dev_ws/src/IndustrialRobots/IFRA_ObjectPose/README.md`
- **IFRA_LinkAttacher**: `/home/madhu/yc_demo_folder/dev_ws/src/IndustrialRobots/IFRA_LinkAttacher/README.md`
- **parallelGripper.py**: `ros2_SimRealRobotControl/ros2srrc_execution/python/endeffector_gz/parallelGripper.py`
- **Machine Vision Example**: `machine_vision_exercise/machine_vision_exercise/MyAlgorithm_full_solution.py`

## ⚠️ Why Simple Gripper Closing Isn't Enough

Gazebo uses **physics simulation**, not collision-based gripping. Simply closing gripper fingers around an object doesn't automatically make it stick. You need either:

1. **LinkAttacher** (creates virtual fixed joint) - requires object pose detection
2. **Vacuum gripper physics** (uses suction forces)
3. **Contact sensors + grasping logic** (complex)

The `ros2_SimRealRobotControl` framework uses LinkAttacher for reliability and simplicity, but it requires object pose tracking.

---

**Status**: Object grasping requires `/ObjectPose` topic  
**Current**: Topic not available, objects not tracked  
**Solution**: Add ObjectPose plugin to objects OR use machine vision approach  
**Priority**: High - Core functionality blocked

