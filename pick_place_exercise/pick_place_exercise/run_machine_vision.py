#!/usr/bin/env python3

"""
Wrapper script to run the FULL machine vision pick and place algorithm
This runs the main() function from MyAlgorithm_full_solution.py
"""

import sys
import os

def main():
    """Entry point for ros2 run - calls main() from MyAlgorithm_full_solution.py"""
    
    # Add the machine_vision_exercise module to the path
    machine_vision_path = os.path.join(
        os.path.expanduser('~'),
        'yc_demo_folder/dev_ws/src/IndustrialRobots/machine_vision_exercise/machine_vision_exercise'
    )
    sys.path.insert(0, machine_vision_path)
    
    try:
        # Import the main function from MyAlgorithm_full_solution
        from MyAlgorithm_full_solution import main as algorithm_main
        
        print("=" * 80)
        print("MACHINE VISION PICK & PLACE - FULL ALGORITHM")
        print("Running main() from MyAlgorithm_full_solution.py")
        print("=" * 80)
        print()
        
        # Call the main function from the algorithm
        algorithm_main()
        
        print()
        print("=" * 80)
        print("ALGORITHM COMPLETED SUCCESSFULLY!")
        print("=" * 80)
        
    except ImportError as e:
        print(f"Error importing algorithm: {e}")
        print("\nMake sure the machine vision environment is launched first:")
        print("  ros2 launch machine_vision_exercise machine_vision_exercise.launch.py")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    except Exception as e:
        print(f"Error running algorithm: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()

