#!/usr/bin/env python3

"""
Visualize target positions as markers in RViz
This publishes markers for all target positions so you can see them in RViz
"""

import rclpy
from rclpy.node import Node
from visualization_msgs.msg import Marker, MarkerArray
from std_msgs.msg import Header, ColorRGBA
import yaml
import os
from ament_index_python.packages import get_package_share_directory


class TargetVisualizer(Node):
    def __init__(self):
        super().__init__('target_visualizer')
        
        # Publisher for markers
        self.marker_pub = self.create_publisher(
            MarkerArray,
            '/target_markers',
            10
        )
        
        self.get_logger().info('Target visualizer node started')
        self.get_logger().info('Publishing markers to /target_markers')
        self.get_logger().info('Add this topic in RViz: MarkerArray -> /target_markers')
        
    def load_and_publish_targets(self):
        """Load target positions from YAML and publish as markers"""
        try:
            # Load models_info.yaml
            package_share_dir = get_package_share_directory('machine_vision_exercise')
            filename = os.path.join(package_share_dir, 'config', 'models_info.yaml')
            
            with open(filename, 'r') as file:
                objects_info = yaml.safe_load(file)
            
            targets = objects_info.get("targets", {})
            
            if not targets:
                self.get_logger().warn('No targets found in models_info.yaml')
                return
            
            # Create marker array
            marker_array = MarkerArray()
            marker_id = 0
            
            # Create a marker for each target
            for target_name, target_pos in targets.items():
                # Sphere marker for target position
                marker = Marker()
                marker.header = Header()
                marker.header.frame_id = "world"
                marker.header.stamp = self.get_clock().now().to_msg()
                marker.ns = "targets"
                marker.id = marker_id
                marker.type = Marker.SPHERE
                marker.action = Marker.ADD
                
                # Position
                marker.pose.position.x = float(target_pos["x"])
                marker.pose.position.y = float(target_pos["y"])
                marker.pose.position.z = float(target_pos["z"])
                marker.pose.orientation.w = 1.0
                
                # Size (sphere radius)
                marker.scale.x = 0.05  # 5cm radius
                marker.scale.y = 0.05
                marker.scale.z = 0.05
                
                # Color (green with some transparency)
                marker.color = ColorRGBA()
                marker.color.r = 0.0
                marker.color.g = 1.0
                marker.color.b = 0.0
                marker.color.a = 0.7  # Slightly transparent
                
                marker_array.markers.append(marker)
                marker_id += 1
                
                # Text marker for target name
                text_marker = Marker()
                text_marker.header = Header()
                text_marker.header.frame_id = "world"
                text_marker.header.stamp = self.get_clock().now().to_msg()
                text_marker.ns = "target_labels"
                text_marker.id = marker_id
                text_marker.type = Marker.TEXT_VIEW_FACING
                text_marker.action = Marker.ADD
                
                text_marker.pose.position.x = float(target_pos["x"])
                text_marker.pose.position.y = float(target_pos["y"])
                text_marker.pose.position.z = float(target_pos["z"]) + 0.08  # Above sphere
                text_marker.pose.orientation.w = 1.0
                
                text_marker.scale.z = 0.05  # Text height
                
                text_marker.color = ColorRGBA()
                text_marker.color.r = 1.0
                text_marker.color.g = 1.0
                text_marker.color.b = 1.0
                text_marker.color.a = 1.0
                
                text_marker.text = target_name
                
                marker_array.markers.append(text_marker)
                marker_id += 1
                
                self.get_logger().info(f'Added marker for {target_name} at ({target_pos["x"]:.3f}, {target_pos["y"]:.3f}, {target_pos["z"]:.3f})')
            
            # Publish markers
            self.marker_pub.publish(marker_array)
            self.get_logger().info(f'Published {len(targets)} target markers')
            
            # Keep publishing periodically
            self.create_timer(1.0, lambda: self.marker_pub.publish(marker_array))
            
        except Exception as e:
            self.get_logger().error(f'Failed to load/publish targets: {e}')
            import traceback
            traceback.print_exc()


def main(args=None):
    rclpy.init(args=args)
    
    print("=" * 80)
    print("TARGET POSITION VISUALIZER")
    print("=" * 80)
    print()
    print("This node publishes target positions as markers for RViz visualization.")
    print()
    print("To view in RViz:")
    print("  1. Open RViz")
    print("  2. Click 'Add' -> 'By topic'")
    print("  3. Select '/target_markers' -> MarkerArray")
    print("  4. You should see green spheres at each target position")
    print()
    print("Press Ctrl+C to stop.")
    print()
    
    node = TargetVisualizer()
    
    try:
        node.load_and_publish_targets()
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()

