#!/usr/bin/env python3
"""
Automated Color Sorting Script for UR5 + Robotiq 2f-85
Picks colored objects and places them in matching colored containers
"""

import subprocess
import time


def execute_program(package_name, program_name):
    """Execute a YAML program using ExecuteProgram.py script"""
    print(f'Executing: {program_name}.yaml')
    
    # Build the command
    cmd = [
        'ros2', 'run', 'ros2srrc_execution', 'ExecuteProgram.py',
        f'package:={package_name}',
        f'program:={program_name}'
    ]
    
    try:
        # Execute the program and wait for completion
        result = subprocess.run(
            cmd,
            check=True,
            capture_output=False,
            text=True
        )
        
        print(f'✓ {program_name} completed successfully\n')
        return True
        
    except subprocess.CalledProcessError as e:
        print(f'✗ {program_name} failed with error code {e.returncode}\n')
        return False
    except Exception as e:
        print(f'✗ Error executing {program_name}: {e}\n')
        return False


def sort_all_colors():
    """Sort all colored objects into their matching containers"""
    colors = ['green']#, 'green', 'blue', 'yellow']
    package_name = 'ros2srrc_execution'
    
    print('\n' + '='*60)
    print('Starting Automated Color Sorting')
    print('='*60 + '\n')
    
    for i, color in enumerate(colors, 1):
        print(f'\n--- Object {i}/4: {color.upper()} ---')
        
        # Pick the colored object
        pick_program = f'ur5_robotiq85_grasp_{color}_pick'
        print(f'Step 1/2: Picking {color} object...')
        
        if not execute_program(package_name, pick_program):
            print(f'Failed to pick {color} object, aborting!')
            return False
        
        time.sleep(1.0)  # Brief pause between pick and place
        
        # Place the colored object in matching container
        place_program = f'ur5_robotiq85_grasp_{color}_place'
        print(f'Step 2/2: Placing {color} object in {color} container...')
        
        if not execute_program(package_name, place_program):
            print(f'Failed to place {color} object, aborting!')
            return False
        
        time.sleep(1.0)  # Brief pause between objects
        
    print('\n' + '='*60)
    print('✓ Color Sorting Complete! All objects sorted.')
    print('='*60 + '\n')
    
    return True

def go_home():
    """Move robot to home position"""
    print('Returning to home position...')
    package_name = 'ros2srrc_execution'
    home_program = 'ur5_robotiq85_grasp_home'
    
    if execute_program(package_name, home_program):
        print('✓ Robot at home position')
    else:
        print('Could not execute home program (may not exist)')


def main(args=None):
    try:
        # Execute the sorting sequence
        success = sort_all_colors()
        
        if success:
            # Return to home position
            go_home()
            print("\n🎉 Mission accomplished! All colored objects have been sorted.")
        else:
            print("\n❌ Sorting failed. Please check the robot and try again.")
        
    except KeyboardInterrupt:
        print("\n⚠️  Interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")


if __name__ == '__main__':
    main()

