#!/usr/bin/python3

# ===================================== COPYRIGHT ===================================== #
#                                                                                       #
#  CORRECTED LAUNCH FILE FOR UR5 + ROBOTIQ 2F-85                                      #
#  Fixed version that properly loads gripper controllers and sets EE_PARAM            #
#                                                                                       #
#  Based on ros2srrc_launch/moveit2/moveit2_robot.launch.py                          #
#  Fixed by: AI Assistant                                                              #
#  Date: November 10, 2025                                                             #
#                                                                                       #
# ===================================== COPYRIGHT ===================================== #

# Import libraries:
import os, sys, xacro, yaml
from ament_index_python.packages import get_package_share_directory, PackageNotFoundError
from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import IncludeLaunchDescription, RegisterEventHandler, TimerAction, ExecuteProcess
from launch.event_handlers import OnProcessExit
from launch.launch_description_sources import PythonLaunchDescriptionSource

# LOAD FILE:
def load_file(package_name, file_path):
    package_path = get_package_share_directory(package_name)
    absolute_file_path = os.path.join(package_path, file_path)
    try:
        with open(absolute_file_path, 'r') as file:
            return file.read()
    except EnvironmentError:
        return None

# LOAD YAML:
def load_yaml(package_name, file_path):
    package_path = get_package_share_directory(package_name)
    absolute_file_path = os.path.join(package_path, file_path)
    try:
        with open(absolute_file_path, 'r') as file:
            return yaml.safe_load(file)
    except EnvironmentError:
        return None

# ========== **GENERATE LAUNCH DESCRIPTION** ========== #
def generate_launch_description():

    LD = LaunchDescription()
    
    # === FIXED CONFIGURATION === #
    PACKAGE_NAME = "ros2srrc_ur5"
    CONFIG_NAME = "ur5_2"  # UR5 + Robotiq 2F-85 gripper
    
    # Get package paths
    PKG_PATH_GAZEBO = get_package_share_directory(PACKAGE_NAME + "_gazebo")
    PKG_PATH_MOVEIT = get_package_share_directory(PACKAGE_NAME + "_moveit2")
    
    # === LOAD CONFIGURATION === #
    config_file = os.path.join(PKG_PATH_GAZEBO, "config", "configurations.yaml")
    with open(config_file, 'r') as f:
        configs = yaml.safe_load(f)
    
    # Find ur5_2 configuration
    CONFIGURATION = None
    for config in configs["Configurations"]:
        if config["ID"] == CONFIG_NAME:
            CONFIGURATION = config
            break
    
    if CONFIGURATION is None:
        print(f"ERROR: Configuration {CONFIG_NAME} not found!")
        exit(1)
    
    print(f"\n{'='*80}")
    print(f"LAUNCHING: {CONFIGURATION['Name']}")
    print(f"  Robot: {CONFIGURATION['rob']}")
    print(f"  End-Effector: {CONFIGURATION['ee']}")
    print(f"  URDF: {CONFIGURATION['urdf']}")
    print(f"{'='*80}\n")
    
    # === ROBOT DESCRIPTION === #
    xacro_file = os.path.join(PKG_PATH_GAZEBO, 'urdf', CONFIGURATION["urdf"])
    doc = xacro.parse(open(xacro_file))
    
    # CRITICAL FIX: Properly set EE flag
    EE = "true" if CONFIGURATION["ee"] != "none" else "false"
    
    print(f"[LAUNCH] EE flag set to: {EE}")
    print(f"[LAUNCH] End-effector name: {CONFIGURATION['ee']}")
    
    xacro.process_doc(doc, mappings={
        "EE": EE,
        "EE_name": CONFIGURATION["ee"],
        "hmi": "false",
    })
    
    robot_description_config = doc.toxml()
    robot_description = {'robot_description': robot_description_config}

    # === ROBOT STATE PUBLISHER === #
    node_robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='both',
        parameters=[
            robot_description,
            {"use_sim_time": True}
        ]
    )

    # === STATIC TRANSFORM === #
    static_tf = Node(
        package="tf2_ros",
        executable="static_transform_publisher",
        name="static_transform_publisher",
        output="log",
        arguments=["0.0", "0.0", "0.0", "0.0", "0.0", "0.0", "world", "base_link"],
    )

    # === GAZEBO === #
    gazebo_launch = os.path.join(
        get_package_share_directory('gazebo_ros'),
        'launch',
        'gazebo.launch.py'
    )
    
    world_file = os.path.join(PKG_PATH_GAZEBO, 'worlds', 'ros2srrc_' + CONFIGURATION["rob"] + '.world')
    
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(gazebo_launch),
        launch_arguments={
            'world': world_file,
            'pause': 'false'
        }.items()
    )

    # === SPAWN ENTITY === #
    spawn_entity = Node(
        package='gazebo_ros',
        executable='spawn_entity.py',
        arguments=['-topic', 'robot_description', '-entity', CONFIGURATION["rob"]],
        output='both'
    )

    # === CONTROLLERS === #
    # Joint state broadcaster
    joint_state_broadcaster_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["joint_state_broadcaster", "--controller-manager", "/controller_manager"],
    )
    
    # Joint trajectory controller
    joint_trajectory_controller_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["joint_trajectory_controller", "-c", "/controller_manager"],
    )

    # === GRIPPER CONTROLLERS (CRITICAL FIX) === #
    # Load all 6 Robotiq 2F-85 controllers
    gripper_controllers = [
        "robotiq_controller_LKJ",
        "robotiq_controller_RKJ",
        "robotiq_controller_LIKJ",
        "robotiq_controller_RIKJ",
        "robotiq_controller_LFTJ",
        "robotiq_controller_RFTJ"
    ]
    
    gripper_controller_spawners = []
    if EE == "true":
        print(f"[LAUNCH] Creating spawners for {len(gripper_controllers)} gripper controllers")
        for controller_name in gripper_controllers:
            gripper_controller_spawners.append(
                Node(
                    package="controller_manager",
                    executable="spawner",
                    arguments=[controller_name, "-c", "/controller_manager"],
                )
            )

    # === MOVEIT2 CONFIGURATION === #
    
    # Robot description semantic (SRDF)
    srdf_file = "config/" + CONFIGURATION["rob"] + CONFIGURATION["ee"] + ".srdf"
    robot_description_semantic_config = load_file(PACKAGE_NAME + "_moveit2", srdf_file)
    robot_description_semantic = {"robot_description_semantic": robot_description_semantic_config}

    # Kinematics
    kinematics_yaml = load_yaml("ros2srrc_robots", CONFIGURATION["rob"] + "/config/kinematics.yaml")
    robot_description_kinematics = {"robot_description_kinematics": kinematics_yaml}

    # Joint limits (merge robot + gripper)
    YAML_ROB = load_yaml("ros2srrc_robots", CONFIGURATION["rob"] + "/config/joint_limits.yaml")["joint_limits"]
    YAML_EE = load_yaml("ros2srrc_endeffectors", CONFIGURATION["ee"] + "/config/joint_limits.yaml")["joint_limits"]
    joint_limits_yaml = {"joint_limits": YAML_ROB | YAML_EE}
    joint_limits = {'robot_description_planning': joint_limits_yaml}

    # Pilz planning pipeline
    pilz_planning_pipeline_config = {
        "move_group": {
            "planning_plugin": "pilz_industrial_motion_planner/CommandPlanner",
            "request_adapters": """ """,
            "start_state_max_bounds_error": 0.1,
        }
    }
    
    pilz_cartesian_limits_yaml = load_yaml("ros2srrc_robots", CONFIGURATION["rob"] + "/config/pilz_cartesian_limits.yaml")
    pilz_cartesian_limits = {"robot_description_planning": pilz_cartesian_limits_yaml}

    # Trajectory execution
    trajectory_execution = {
        "moveit_manage_controllers": True,
        "trajectory_execution.allowed_execution_duration_scaling": 1.2,
        "trajectory_execution.allowed_goal_duration_margin": 0.5,
        "trajectory_execution.allowed_start_tolerance": 0.01,
    }

    # MoveIt controllers (merge robot + gripper)
    YAML_ROB_CTR = load_yaml("ros2srrc_robots", CONFIGURATION["rob"] + "/config/controller_moveit2.yaml")
    YAML_EE_CTR = load_yaml("ros2srrc_endeffectors", CONFIGURATION["ee"] + "/config/controller_moveit2.yaml")
    for x in YAML_ROB_CTR["controller_names"]:
        YAML_EE_CTR["controller_names"].append(x)
    moveit_simple_controllers_yaml = YAML_ROB_CTR | YAML_EE_CTR
    moveit_controllers = {
        "moveit_simple_controller_manager": moveit_simple_controllers_yaml,
        "moveit_controller_manager": "moveit_simple_controller_manager/MoveItSimpleControllerManager",
    }

    # Planning scene monitor
    planning_scene_monitor_parameters = {
        "publish_planning_scene": True,
        "publish_geometry_updates": True,
        "publish_state_updates": True,
        "publish_transforms_updates": True,
    }

    # Move group capabilities
    move_group_capabilities = {
        "capabilities": "move_group/ExecuteTaskSolutionCapability"
    }

    # === MOVE GROUP NODE === #
    run_move_group_node = Node(
        package="moveit_ros_move_group",
        executable="move_group",
        output="screen",
        parameters=[
            robot_description,
            robot_description_semantic,
            kinematics_yaml,
            pilz_planning_pipeline_config,
            joint_limits,
            pilz_cartesian_limits,
            trajectory_execution,
            moveit_controllers,
            planning_scene_monitor_parameters,
            move_group_capabilities,
            {"use_sim_time": True},
        ]
    )

    # === ROS2SRRC EXECUTION INTERFACES === #
    
    # CRITICAL FIX: Set EE_PARAM correctly to robotiq_2f85 (not "none")
    print(f"[LAUNCH] Setting MoveInterface EE_PARAM to: {CONFIGURATION['ee']}")
    
    MoveInterface = Node(
        name="move",
        package="ros2srrc_execution",
        executable="move",
        output="screen",
        parameters=[
            robot_description,
            robot_description_semantic,
            kinematics_yaml,
            {"use_sim_time": True},
            {"ROB_PARAM": CONFIGURATION["rob"]},
            {"EE_PARAM": CONFIGURATION["ee"]},  # CRITICAL FIX
            {"ENV_PARAM": "gazebo"}
        ],
    )

    RobMoveInterface = Node(
        name="robmove",
        package="ros2srrc_execution",
        executable="robmove",
        output="screen",
        parameters=[
            robot_description,
            robot_description_semantic,
            kinematics_yaml,
            {"use_sim_time": True},
            {"ROB_PARAM": CONFIGURATION["rob"]}
        ],
    )
    
    RobPoseInterface = Node(
        name="robpose",
        package="ros2srrc_execution",
        executable="robpose",
        output="screen",
        parameters=[
            robot_description,
            robot_description_semantic,
            kinematics_yaml,
            {"use_sim_time": True},
            {"ROB_PARAM": CONFIGURATION["rob"]}
        ],
    )

    # === RVIZ2 === #
    rviz_config = os.path.join(PKG_PATH_MOVEIT, "config", "rviz_config.rviz")
    rviz_node = Node(
        package="rviz2",
        executable="rviz2",
        name="rviz2",
        output="log",
        arguments=["-d", rviz_config],
        parameters=[
            robot_description,
            robot_description_semantic,
            robot_description_kinematics,
            pilz_planning_pipeline_config,
            joint_limits,
            {"use_sim_time": True},
        ]
    )

    # === BUILD LAUNCH DESCRIPTION === #
    
    # Add basic nodes
    LD.add_action(gazebo)
    LD.add_action(node_robot_state_publisher)
    LD.add_action(static_tf)
    LD.add_action(spawn_entity)

    # Spawn controllers in sequence
    LD.add_action(RegisterEventHandler(
        OnProcessExit(
            target_action=spawn_entity,
            on_exit=[joint_state_broadcaster_spawner]
        )
    ))

    LD.add_action(RegisterEventHandler(
        OnProcessExit(
            target_action=spawn_entity,
            on_exit=[joint_trajectory_controller_spawner]
        )
    ))

    # CRITICAL FIX: Spawn gripper controllers after joint trajectory controller
    for spawner in gripper_controller_spawners:
        LD.add_action(RegisterEventHandler(
            OnProcessExit(
                target_action=joint_trajectory_controller_spawner,
                on_exit=[spawner]
            )
        ))

    # Launch MoveIt and interfaces after controllers are ready
    LD.add_action(RegisterEventHandler(
        OnProcessExit(
            target_action=joint_trajectory_controller_spawner,
            on_exit=[
                TimerAction(
                    period=3.0,
                    actions=[
                        run_move_group_node,
                        rviz_node,
                    ]
                ),
            ]
        )
    ))

    LD.add_action(RegisterEventHandler(
        OnProcessExit(
            target_action=joint_trajectory_controller_spawner,
            on_exit=[
                TimerAction(
                    period=5.0,
                    actions=[
                        MoveInterface,
                        RobMoveInterface,
                        RobPoseInterface,
                    ]
                ),
            ]
        )
    ))

    return LD

