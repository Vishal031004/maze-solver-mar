# ROS2 Maze Solver Using Pledge Algorithm  
### Mobile and Autonomous Robots Mini Project

An autonomous maze-solving robot built using **ROS 2 Humble**, **Gazebo**, and **OpenCV**.  
The robot navigates through a maze using the **Pledge Algorithm**, detects hazards using camera vision, and raises **voice alerts** in real time.

---

# Project Features

 Autonomous maze navigation  
 Pledge Algorithm for loop handling  
 LiDAR-based obstacle sensing  
 Camera-based red hazard detection  
 Voice warning alert using `espeak`  
 Emergency stop control  
 Gazebo simulation environment  

---

# Demo Summary

The robot is placed inside a maze and must autonomously escape.  
While navigating:

- It uses **LiDAR** to detect walls and corridors  
- It follows the **Pledge Algorithm** to avoid getting trapped in loops  
- It uses an onboard **camera** to detect red hazard objects  
- If hazard is detected, it shows:

```text
HAZARD DETECTED!
```

and plays an audio warning.

---

# Repository Structure

```text
maze-solver-mar/
│── maze_solver_description/      # Robot model (URDF/Xacro)
│── maze_solver_nav/              # ROS2 Python nodes
│   ├── pledge_solver.py          # Maze solving logic
│   ├── vision_alert.py           # Camera hazard detection
│   ├── e_stop.py                 # Emergency stop
│── maze_solver_simulation/       # Gazebo world + launch files
│── README.md
```

---

# System Requirements

Recommended Environment:

- Ubuntu 22.04
- ROS 2 Humble
- Python 3.10+
- Gazebo Fortress / Gazebo compatible with ROS2 Humble
- OpenCV
- colcon build tools

---

# Installation Guide

## 1. Install ROS2 Humble

Official guide:

https://docs.ros.org/en/humble/Installation/Ubuntu-Install-Debians.html

---

## 2. Create Workspace

```bash
mkdir -p ~/ros2_ws/src
cd ~/ros2_ws/src
```

---

## 3. Clone Repository

```bash
git clone https://github.com/Vishal031004/maze-solver-mar.git
```

---

## 4. Build Project

```bash
cd ~/ros2_ws
source /opt/ros/humble/setup.bash
colcon build --symlink-install
```

---

## 5. Source Workspace

```bash
source ~/ros2_ws/install/setup.bash
```

---

# Required Python Packages

If needed:

```bash
pip install opencv-python numpy
sudo apt install ros-humble-cv-bridge espeak -y
```

---

# How to Run the Project

Open **4 separate terminals**.

---

# Terminal 1 — Launch Gazebo Maze World

```bash
cd ~/ros2_ws
source /opt/ros/humble/setup.bash
source install/setup.bash

ros2 launch maze_solver_simulation spawn_maze.launch.py
```

This launches:

- Gazebo
- Maze environment
- Robot model

---

# Terminal 2 — Emergency Stop Node

```bash
cd ~/ros2_ws
source /opt/ros/humble/setup.bash
source install/setup.bash

ros2 run maze_solver_nav e_stop
```

### Controls

- Press **SPACEBAR** to toggle Emergency Stop

---

# Terminal 3 — Vision Alert Node

```bash
cd ~/ros2_ws
source /opt/ros/humble/setup.bash
source install/setup.bash

ros2 run maze_solver_nav vision_alert
```

This opens the **Robot Camera Feed** window.

If a red object enters view:

```text
HAZARD DETECTED!
```

Voice warning is played.

---

# Terminal 4 — Maze Solver Node

```bash
cd ~/ros2_ws
source /opt/ros/humble/setup.bash
source install/setup.bash

ros2 run maze_solver_nav pledge_solver
```

Robot starts autonomous maze navigation.

---

# How to Test Hazard Detection

Inside Gazebo:

1. Locate the red box (`victim_box`) placed in the maze  
2. Let the robot move until camera sees the red box

Expected result:

- Camera feed displays alert text  
- Voice warning plays  
- Robot continues navigation

---

# How the Pledge Algorithm Works

The robot avoids loops using cumulative turn counting:

1. Move in preferred direction  
2. If blocked, follow wall  
3. Count left/right turns  
4. Exit wall-following when heading is restored  
5. Continue toward maze exit

This prevents infinite looping inside spiral or cyclic mazes.

---

# Important ROS Nodes

| Node | Purpose |
|------|---------|
| `pledge_solver` | Controls maze navigation |
| `vision_alert` | Camera hazard detection |
| `e_stop` | Emergency stop control |

---

# Troubleshooting

## Package Not Found

```bash
source ~/ros2_ws/install/setup.bash
```

---

## Robot Not Moving

Ensure:

```bash
ros2 run maze_solver_nav pledge_solver
```

is running.

---

## Camera Window Not Opening

Ensure:

```bash
ros2 run maze_solver_nav vision_alert
```

is running.

---

## Gazebo Glitch / Duplicate Robot

Close everything and run:

```bash
pkill -f ros2
pkill -f gz
pkill -f gazebo
```

Then relaunch.

---

# Rebuild After Changes

```bash
cd ~/ros2_ws
colcon build --symlink-install
source install/setup.bash
```

---

# Future Enhancements

- Dynamic obstacle avoidance  
- SLAM mapping  
- Path planning using A* / Dijkstra  
- Victim localization  
- Fire / smoke detection  
- Multi-robot rescue coordination  

---

# Authors

- Vishal P  
- Yashas J  
- Vrishank NA  
- Sagar R Bhat

---

# Conclusion

This project demonstrates an intelligent autonomous robot capable of:

- Navigating a maze
- Detecting hazards visually
- Giving real-time alerts
- Operating modularly using ROS 2 nodes

It provides a strong base for real-world rescue robotics and autonomous navigation systems.

---

# GitHub Repository

https://github.com/Vishal031004/maze-solver-mar
