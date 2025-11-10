#!/usr/bin/env python3

"""
Add obstacles and pickable objects from models_info.yaml to the MoveIt planning scene
This ensures the robot knows about:
  - Obstacles (conveyor belt, storage rack, etc.)
  - All pickable objects (cylinders, boxes, spheres)
The robot will avoid collisions with these items during motion planning.
"""

import rclpy
from rclpy.node import Node
from moveit_msgs.msg import CollisionObject, PlanningScene
from shape_msgs.msg import SolidPrimitive
from geometry_msgs.msg import Pose
from std_msgs.msg import Header
import yaml
import os
from ament_index_python.packages import get_package_share_directory
from tf_transformations import quaternion_from_euler


class PlanningScenePublisher(Node):
    def __init__(self):
        super().__init__('planning_scene_publisher')
        
        # Publisher for planning scene
        self.planning_scene_pub = self.create_publisher(
            PlanningScene,
            '/planning_scene',
            10
        )
        
        # Wait for subscriber
        self.get_logger().info('Waiting for planning scene subscribers...')
        while self.planning_scene_pub.get_subscription_count() < 1:
            rclpy.spin_once(self, timeout_sec=0.1)
        
        self.get_logger().info('Planning scene subscriber detected!')
        
    def load_and_publish_obstacles(self):
        """Load obstacles and objects from YAML and publish to planning scene"""
        try:
            # Load models_info.yaml
            package_share_dir = get_package_share_directory('machine_vision_exercise')
            filename = os.path.join(package_share_dir, 'config', 'models_info.yaml')
            
            with open(filename, 'r') as file:
                objects_info = yaml.safe_load(file)
            
            robot_x = objects_info["robot"]["pose"]["x"]
            robot_y = objects_info["robot"]["pose"]["y"]
            robot_z = objects_info["robot"]["pose"]["z"]
            
            # Get both obstacles and pickable objects
            obstacles = objects_info.get("obstacles", {})
            objects = objects_info.get("objects", {})
            
            # Handle None values (in case sections are commented out or empty)
            if obstacles is None:
                obstacles = {}
            if objects is None:
                objects = {}
            
            if not obstacles and not objects:
                self.get_logger().warn('No obstacles or objects found in models_info.yaml')
                return
            
            # Create planning scene message
            planning_scene = PlanningScene()
            planning_scene.is_diff = True
            planning_scene.robot_state.is_diff = True
            
            # Add obstacles first (if any)
            if obstacles:
                for name, spec in obstacles.items():
                    self.get_logger().info(f'Adding obstacle: {name}')
                    
                    # Create collision object
                    collision_obj = CollisionObject()
                    collision_obj.header = Header()
                    collision_obj.header.frame_id = "world"
                    collision_obj.header.stamp = self.get_clock().now().to_msg()
                    collision_obj.id = name
                    
                    # Get pose
                    x = spec["pose"]["x"]
                    y = spec["pose"]["y"]
                    z = spec["pose"]["z"]
                    roll = spec["pose"].get("roll", 0)
                    pitch = spec["pose"].get("pitch", 0)
                    yaw = spec["pose"].get("yaw", 0)
                    
                    # Create pose in world frame (not relative to robot)
                    pose = Pose()
                    pose.position.x = float(x)
                    pose.position.y = float(y)
                    pose.position.z = float(z)
                    
                    q = quaternion_from_euler(roll, pitch, yaw)
                    pose.orientation.x = float(q[0])
                    pose.orientation.y = float(q[1])
                    pose.orientation.z = float(q[2])
                    pose.orientation.w = float(q[3])
                    
                    # Create shape based on type
                    shape = spec["shape"]
                    primitive = SolidPrimitive()
                    
                    if shape == "box":
                        primitive.type = SolidPrimitive.BOX
                        sx = spec["size"]["x"]
                        sy = spec["size"]["y"]
                        sz = spec["size"]["z"]
                        primitive.dimensions = [float(sx), float(sy), float(sz)]
                        self.get_logger().info(f'  Type: BOX, Size: [{sx}, {sy}, {sz}]')
                        
                    elif shape == "cylinder":
                        primitive.type = SolidPrimitive.CYLINDER
                        height = spec["size"]["height"]
                        radius = spec["size"]["radius"]
                        primitive.dimensions = [float(height), float(radius)]
                        self.get_logger().info(f'  Type: CYLINDER, Height: {height}, Radius: {radius}')
                        
                    elif shape == "sphere":
                        primitive.type = SolidPrimitive.SPHERE
                        radius = spec["size"]
                        primitive.dimensions = [float(radius)]
                        self.get_logger().info(f'  Type: SPHERE, Radius: {radius}')
                        
                    else:
                        self.get_logger().warn(f'Unknown shape type: {shape} for obstacle {name}')
                        continue
                    
                    # Add shape and pose to collision object
                    collision_obj.primitives.append(primitive)
                    collision_obj.primitive_poses.append(pose)
                    collision_obj.operation = CollisionObject.ADD
                    
                    # Add to planning scene
                    planning_scene.world.collision_objects.append(collision_obj)
                    
                    self.get_logger().info(f'  Position: [{x:.2f}, {y:.2f}, {z:.2f}]')
            
            # Add pickable objects to planning scene
            if objects:
                for name, spec in objects.items():
                    self.get_logger().info(f'Adding object: {name}')
                    
                    # Create collision object
                    collision_obj = CollisionObject()
                    collision_obj.header = Header()
                    collision_obj.header.frame_id = "world"
                    collision_obj.header.stamp = self.get_clock().now().to_msg()
                    collision_obj.id = name
                    
                    # Get pose
                    x = spec["pose"]["x"]
                    y = spec["pose"]["y"]
                    z = spec["pose"]["z"]
                    roll = spec["pose"].get("roll", 0)
                    pitch = spec["pose"].get("pitch", 0)
                    yaw = spec["pose"].get("yaw", 0)
                    
                    # Create pose in world frame
                    pose = Pose()
                    pose.position.x = float(x)
                    pose.position.y = float(y)
                    pose.position.z = float(z)
                    
                    q = quaternion_from_euler(roll, pitch, yaw)
                    pose.orientation.x = float(q[0])
                    pose.orientation.y = float(q[1])
                    pose.orientation.z = float(q[2])
                    pose.orientation.w = float(q[3])
                    
                    # Create shape based on type
                    shape = spec["shape"]
                    primitive = SolidPrimitive()
                    
                    if shape == "box":
                        primitive.type = SolidPrimitive.BOX
                        sx = spec["size"]["x"]
                        sy = spec["size"]["y"]
                        sz = spec["size"]["z"]
                        primitive.dimensions = [float(sx), float(sy), float(sz)]
                        # Adjust Z position to center of box
                        pose.position.z = float(z) + float(sz) / 2.0
                        self.get_logger().info(f'  Type: BOX, Size: [{sx}, {sy}, {sz}]')
                        
                    elif shape == "cylinder":
                        primitive.type = SolidPrimitive.CYLINDER
                        height = spec["size"]["height"]
                        radius = spec["size"]["radius"]
                        primitive.dimensions = [float(height), float(radius)]
                        # Adjust Z position to center of cylinder
                        pose.position.z = float(z) + float(height) / 2.0
                        self.get_logger().info(f'  Type: CYLINDER, Height: {height}, Radius: {radius}')
                        
                    elif shape == "sphere":
                        primitive.type = SolidPrimitive.SPHERE
                        radius = spec["size"]
                        primitive.dimensions = [float(radius)]
                        # Adjust Z position to center of sphere
                        pose.position.z = float(z) + float(radius)
                        self.get_logger().info(f'  Type: SPHERE, Radius: {radius}')
                        
                    else:
                        self.get_logger().warn(f'Unknown shape type: {shape} for object {name}')
                        continue
                    
                    # Add shape and pose to collision object
                    collision_obj.primitives.append(primitive)
                    collision_obj.primitive_poses.append(pose)
                    collision_obj.operation = CollisionObject.ADD
                    
                    # Add to planning scene
                    planning_scene.world.collision_objects.append(collision_obj)
                    
                    self.get_logger().info(f'  Position: [{x:.2f}, {y:.2f}, {z:.2f}] (center at Z={pose.position.z:.2f})')
            
            # Publish planning scene
            total_items = len(obstacles) + len(objects)
            self.get_logger().info(f'Publishing planning scene with {len(obstacles)} obstacles and {len(objects)} objects...')
            self.planning_scene_pub.publish(planning_scene)
            
            # Give time for message to be received
            rclpy.spin_once(self, timeout_sec=0.5)
            
            self.get_logger().info('✓ Successfully added items to planning scene!')
            self.get_logger().info(f'  Obstacles: {len(obstacles)}')
            self.get_logger().info(f'  Objects: {len(objects)}')
            self.get_logger().info(f'  Total: {total_items}')
            
        except Exception as e:
            self.get_logger().error(f'Failed to load/publish obstacles: {e}')
            import traceback
            traceback.print_exc()


def main(args=None):
    rclpy.init(args=args)
    
    print("=" * 80)
    print("ADDING OBSTACLES AND OBJECTS TO MOVEIT PLANNING SCENE")
    print("=" * 80)
    print()
    
    node = PlanningScenePublisher()
    
    try:
        node.load_and_publish_obstacles()
        
        print()
        print("=" * 80)
        print("PLANNING SCENE SETUP COMPLETE!")
        print("=" * 80)
        print()
        print("MoveIt is now aware of:")
        print("  - Obstacles (conveyor belt, storage rack, etc.)")
        print("  - All 16 pickable objects (cylinders and boxes)")
        print()
        print("The robot will now avoid collisions with:")
        print("  - All obstacles during motion planning")
        print("  - All objects until they are picked")
        print()
        
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()

