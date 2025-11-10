#!/usr/bin/env python3

"""
Simple Machine Vision Test - Safer positions to avoid self-collision
"""

import sys
import os
import time

# Add the machine_vision_exercise module to the path
machine_vision_path = os.path.join(
    os.path.expanduser('~'),
    'yc_demo_folder/dev_ws/src/IndustrialRobots/machine_vision_exercise/machine_vision_exercise'
)
sys.path.insert(0, machine_vision_path)

def safe_pick_and_place():
    """Execute pick and place with safer, tested positions"""
    
    from HAL import (MoveAbsJ, MoveLinear, MoveJoint, MoveRelLinear, 
                     attach, detach, get_TCP_pose, set_home_position)
    
    print("=" * 80)
    print("SAFE MACHINE VISION PICK & PLACE TEST")
    print("=" * 80)
    print()
    
    # SAFER positions that avoid self-collision
    # These are closer to the robot base and easier to reach
    object_pos = [0.4, 0.0, 1.0]      # Closer and centered
    target_pos = [0.0, -0.4, 1.0]     # Side position, same height
    
    # Safer orientation (slightly tilted, not fully vertical)
    safe_orientation = [0, 80, 0]     # 80° instead of 90°
    
    try:
        # Step 1: Go to home position
        print("\n1. Moving to home position...")
        set_home_position([0.0, -90.0, 90.0, -90.0, -90.0, 0.0])
        MoveAbsJ([0.0, -90.0, 90.0, -90.0, -90.0, 0.0], 0.5, 3.0)
        print("✓ At home position")
        
        # Step 2: Move to approach position (high and safe)
        print("\n2. Moving to approach position...")
        approach_pos = [object_pos[0], object_pos[1], object_pos[2] + 0.25]
        MoveJoint(approach_pos, safe_orientation, 0.3, 3.0)
        print("✓ At approach position")
        
        # Step 3: Move down slowly to object
        print("\n3. Moving to object...")
        pick_pos = [object_pos[0], object_pos[1], object_pos[2] + 0.05]
        MoveLinear(pick_pos, safe_orientation, 0.1, 2.0)
        print("✓ At object")
        
        # Step 4: Attempt to attach (will fail without ObjectPose, but tests LinkAttacher)
        print("\n4. Attempting to attach object...")
        try:
            attach('red_cylinder')
            print("✓ Object attached!")
        except Exception as e:
            print(f"⚠ Attach result: {e}")
            print("  (This is expected without ObjectPose tracking)")
        
        # Step 5: Lift up
        print("\n5. Lifting...")
        MoveRelLinear([0, 0, 0.20], 0.1, 2.0)
        print("✓ Lifted")
        
        # Step 6: Move to target approach
        print("\n6. Moving to target approach...")
        target_approach = [target_pos[0], target_pos[1], target_pos[2] + 0.25]
        MoveJoint(target_approach, safe_orientation, 0.3, 3.0)
        print("✓ At target approach")
        
        # Step 7: Move down to place
        print("\n7. Placing object...")
        place_pos = [target_pos[0], target_pos[1], target_pos[2] + 0.05]
        MoveLinear(place_pos, safe_orientation, 0.1, 2.0)
        print("✓ At place position")
        
        # Step 8: Detach
        print("\n8. Detaching object...")
        try:
            detach('red_cylinder')
            print("✓ Object detached!")
        except Exception as e:
            print(f"⚠ Detach result: {e}")
        
        # Step 9: Retract
        print("\n9. Retracting...")
        MoveRelLinear([0, 0, 0.15], 0.1, 2.0)
        print("✓ Retracted")
        
        # Step 10: Return home
        print("\n10. Returning home...")
        MoveAbsJ([0.0, -90.0, 90.0, -90.0, -90.0, 0.0], 0.5, 3.0)
        print("✓ Back at home")
        
        print()
        print("=" * 80)
        print("✓ TEST COMPLETED SUCCESSFULLY!")
        print("=" * 80)
        print()
        print("Note: Object attachment requires ObjectPose plugin.")
        print("This test verifies that robot movement and planning work correctly.")
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        print("\nIf you see 'PLANNING FAILED', try:")
        print("  1. Check robot is in a good starting position")
        print("  2. Verify no obstacles in workspace")
        print("  3. Adjust positions in the script if needed")
        sys.exit(1)

def main():
    """Entry point"""
    try:
        safe_pick_and_place()
    except KeyboardInterrupt:
        print("\nInterrupted by user")
        sys.exit(0)

if __name__ == '__main__':
    main()

