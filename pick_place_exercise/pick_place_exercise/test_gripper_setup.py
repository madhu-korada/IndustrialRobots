#!/usr/bin/env python3

"""
Gripper Setup and Test Script

This script:
1. Loads all Robotiq 2f-85 gripper controllers
2. Configures and activates them
3. Tests gripper open/close functionality
"""

import subprocess
import time

def run_command(cmd, description):
    """Run a shell command and print result"""
    print(f"\n{'='*60}")
    print(f"{description}")
    print(f"{'='*60}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    print(result.stdout)
    if result.returncode != 0:
        print(f"ERROR: {result.stderr}")
        return False
    return True

def main():
    print("\n" + "="*80)
    print("ROBOTIQ 2F-85 GRIPPER SETUP AND TEST")
    print("="*80)
    
    # Define all gripper controllers
    controllers = [
        "robotiq_controller_LKJ",    # Left Knuckle Joint
        "robotiq_controller_RKJ",    # Right Knuckle Joint
        "robotiq_controller_LIKJ",   # Left Inner Knuckle Joint
        "robotiq_controller_RIKJ",   # Right Inner Knuckle Joint
        "robotiq_controller_LFTJ",   # Left Finger Tip Joint
        "robotiq_controller_RFTJ"    # Right Finger Tip Joint
    ]
    
    # Step 1: Check current controller status
    print("\n" + "="*80)
    print("STEP 1: Checking current controller status")
    print("="*80)
    run_command("ros2 control list_controllers", "Current controllers:")
    
    # Step 2: Load all gripper controllers
    print("\n" + "="*80)
    print("STEP 2: Loading gripper controllers")
    print("="*80)
    for controller in controllers:
        if not run_command(f"ros2 control load_controller {controller}", 
                          f"Loading {controller}..."):
            print(f"WARNING: Failed to load {controller}")
    
    time.sleep(1)
    
    # Step 3: Activate all gripper controllers (combines configure + start)
    print("\n" + "="*80)
    print("STEP 3: Activating gripper controllers")
    print("="*80)
    for controller in controllers:
        if not run_command(f"ros2 control set_controller_state {controller} active",
                          f"Activating {controller}..."):
            print(f"WARNING: Failed to activate {controller}")
    
    time.sleep(1)
    
    # Step 4: Verify all controllers are active
    print("\n" + "="*80)
    print("STEP 4: Verifying controller status")
    print("="*80)
    run_command("ros2 control list_controllers", "Updated controller list:")
    
    # Step 5: Check hardware interfaces
    print("\n" + "="*80)
    print("STEP 5: Checking hardware interface claims")
    print("="*80)
    run_command("ros2 control list_hardware_interfaces | grep robotiq", 
                "Robotiq interface status:")
    
    # Step 6: Test gripper with Move action
    print("\n" + "="*80)
    print("STEP 6: Testing gripper via /Move action")
    print("="*80)
    
    print("\nTest 1: Opening gripper (MoveG with value 0.0)...")
    time.sleep(2)
    subprocess.run([
        "timeout", "10",
        "ros2", "action", "send_goal", "/Move", 
        "ros2srrc_data/action/Move",
        "{action: 'MoveG', speed: 1.0, moveg: 0.0}"
    ])
    
    print("\nTest 2: Closing gripper partially (MoveG with value 50.0)...")
    time.sleep(2)
    subprocess.run([
        "timeout", "10",
        "ros2", "action", "send_goal", "/Move",
        "ros2srrc_data/action/Move", 
        "{action: 'MoveG', speed: 1.0, moveg: 50.0}"
    ])
    
    print("\n" + "="*80)
    print("GRIPPER SETUP AND TEST COMPLETE!")
    print("="*80)
    print("\nIf the gripper controllers are all 'active', the setup is correct.")
    print("If the Move actions completed successfully, the gripper is working!")
    print("="*80 + "\n")

if __name__ == '__main__':
    main()

