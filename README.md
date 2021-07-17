# ros2tests
Basic tests with ros2, repo for when learning ROS2, and repo for running basic rostalker2 files during the intial prototyping stage.

# Rostalker2
Rostalker2 is a project to connect 3 different moving parts in an automated biology lab a master, Opentron-2 robot, and robotic arm, with added equipment later on. A goal of rostalker2 is to set up a network between these different robotics parts using ROS 2 Foxy and have them able to syncronize each other and be fault tolerant. Another goal is to allow a user to run whatever they want concurrently on multiple different machines this goal is called the monolithic model. Another goal is to be able to run biology experiments in a HPC manner, where the user just specifies tasks and their dependencies and the system will automatically schedule the experiment, this theoritcallly should increase performance and efficiency dubbed the workflow model. Currently rostalker2 only supports the monolithic model, future plans will begin to add in the workflow model.

# Rostalker2 Files
**arm_controller/**
		  **arm_controller/**
				    armManager.py (Manages the state of the arm)
				    armTransferHandler.py (Manages transfer service)
		  **launch/**
				    arm_bringup.launch.py (Launches the arm)

**arm_client/**
		  **arm_client/**
				    transfer_api.py (An api for other OT2s to use to transfer items)
				    publish_arm_state.py (api to publish its state to a manager)

**ot2_workcell_manager/**
		  **ot2_workcell_manager/**
				    master.py (Controls the state of the system)

**master_api/**
		  **master_api/**
				    register_api.py (registration to the master api)
				    retry_api.py (api to allow users to run a function in an isolated manner)
				    worker_info_api.py (api to allow workers to retrieve other worker info from the master)

**ot2_controller/**
		  **ot2_controller/**
				    protocol_manager.py (removes items from the queue in manager)

**ot2_client/**
		  **ot2_client/**
				    load_run_api.py (TODO)
				    publish_ot2_state_api.py (api to publish the state of the ot2 to manager)

**rostalker2/ (TODO: Deprecate)**
		  **rostalker2/**
				    ot2class.py (Contains the state of the OT2 class planned to split it up into 3 different files)

**workcell_interfaces/**
		  **srv/**
				    Destroy.srv
				    GetId.srv
				    GetNextTransfer.srv
				    GetNodeInfo.srv
				    GetNodeList.srv
				    LoadService.srv
				    LoadTransfer.srv
				    Register.srv
				    Run.srv
		  **msg/**
				    NodeEntry.msg
				    ArmStateUpdate.msg
				    CompletedTransfer.msg
				    OT2StateUpdate.msg

# Install
This is for ubuntu 20.04 running ROS2 foxy
1. cd (Must be in home directory)
2. source /opt/ros/foxy/setup.bash
3. git clone https://github.com/urd00m/ros2tests
4. cd ros2tests
5. colcon build
6. source install/setup.bash

# Launching
**Master**
1. source ~/ros2tests/install/setup.bash
2. ros2 run ot2_workcell_manager master

**Arm**
1. source ~/ros2tests/install/setup.bash
2. ros2 launch arm_controller arm_bringup.launch.py

**Opentron-2s**
1. source ~/ros2tests/install/setup.bash
2. ros2 run rostalker2 OT2 bob

**Opentron-2s**
1. source ~/ros2tests/install/setup.bash
2. ros2 run rostalker2 OT2 alex

This will cause nodes to be registered with master and start a transfer process as well as a OT-2 procedure. In the future this won't be able to run conncurentlly as use of a arm will block whatever called it.

# Diagrams for different components
TODO
