# Mapping & Localization

**Authors:** [Chinmay Samak](https://www.linkedin.com/in/samakchinmay) and [Tanmay Samak](https://www.linkedin.com/in/samaktanmay)

The `mapping_localization` ROS 2 package provides reference implementations for mapping (SLAM), localization, and map-based navigation, which are directly (mapping and localization) or remotely (navigation) relevant to autonomous racing application:

- **Mapping** builds an occupancy-grid map of the environment with Simultaneous Localization and Mapping (SLAM) process; using Graph-SLAM, GMapping, or Cartographer algorithmic variants.
- **Localization** estimates the vehicle pose on a known occupancy-grid map of the environment using Adaptive Monte Carlo Localization (AMCL) algorithm (an adaptive variant of particle filter that dynamically adjusts the total number of particles on the fly using KLD-sampling to save computational overload).
- **Navigation** uses Nav2 with either Dynamic Window Approach (DWA) or Timed Elastic Band (TEB) variant configuration to plan and follow a trajectory with real-time feedback of the estimated vehicle pose on a known occupancy-grid map of the environment.

> [!NOTE]
> - `/scan` contains an array of 360° range measurements spanning -180° to 180° at 0.25° resolution, represented as a 1440-bin array of float32 distances in meters. The `ranges` index 0 points straight behind the vehicle, and the subsequent elements progress counter-clockwise. Only the 270 deg window (|angle| <= 135°) carries returns; no-return = `inf`. The rear sector (between 135° and 225°) is blind; returns `inf`.
> - `/drive` expects `speed` and `steering_angle` commands for the vehicle to be normalized `[-1.0, 1.0]`. The actuation limits of the vehicle for `speed` and `steering_angle` are ±6 m/s (safety cap) and ±0.5236 rad (30°). For `speed`, positive command corresponds to forward vehicle motion, while negative command corresponds to reverse vehicle motion. For `steering_angle`, positive command corresponds to left-hand turn, while negative command corresponds to right-hand turn.

## Package description

```text
mapping_localization/
├── config/
│   └── odometry_ekf.yaml
│   └── slam_graph.yaml
│   └── slam_gmapping.yaml
│   └── slam_cartographer.lua
│   └── localization_amcl.yaml
│   └── navigation_dwa.yaml
│   └── navigation_teb.yaml
├── launch/
│   └── slam_graph.launch.py
│   └── slam_gmapping.launch.py
│   └── slam_cartographer.launch.py
│   └── localization_amcl.launch.py
│   └── navigation_dwa.launch.py
│   └── navigation_teb.launch.py
├── mapping_localization/
│   └── __init__.py
│   └── teleop_keyboard.py
├── maps/
│   └── map.pgm
│   └── map.png
│   └── map.yaml
├── resource/
│   └── mapping_localization
├── rviz/
│   └── mapping.rviz
│   └── localization.rviz
│   └── navigation.rviz
├── package.xml
├── setup.cfg
└── setup.py
```

- `config/odometry_ekf.yaml` — configures odometry algorithm.
- `config/{slam_graph.yaml, slam_gmapping.yaml, slam_cartographer.lua}` — configure the three mapping (SLAM) algorithm variants.
- `config/localization_amcl.yaml` — configures localization algorithm.
- `config/{navigation_dwa.yaml, navigation_teb.yaml}` — configure navigation algorithm variants.
- `launch/{slam_graph.launch.py, slam_gmapping.launch.py, slam_cartographer.launch.py}` — start the respective mapping (SLAM) stacks.
- `launch/localization_amcl.launch.py` — starts the localization stack (AMCL) on the supplied map.
- `launch/{navigation_dwa.launch.py, navigation_teb.launch.py}` — start the Nav2 stack with the respective configurations.
- `mapping_localization/__init__.py` — marks the Python module directory as the `mapping_localization` package.
- `mapping_localization/teleop_keyboard.py` — implements the `teleop_keyboard` interface as a ROS 2 node.
- `maps/map.pgm` — is the image reference of the occupancy-grid map.
- `maps/map.png` — is a PNG-equivalent of `map.pgm` for convenient cross-platform visualization.
- `maps/map.yaml` — is the configuration withholding metadata of the occupancy-grid map.
- `resource/mapping_localization` — ament resource marker used to register the package in the ROS 2 package index.
- `rviz/{mapping.rviz, localization.rviz, and navigation.rviz}` — configurations for interactive visualization of the algorithm behavior and debugging.
- `test/test_copyright.py` — checks package files for required copyright notices.
- `test/test_flake8.py` — checks Python code style with Flake8.
- `test/test_pep257.py` — checks Python docstring conventions with PEP 257.
- `package.xml` — declares package metadata, maintainers, license, and dependencies.
- `setup.cfg` — configures where ROS 2 installs the Python executables.
- `setup.py` — defines the Python package, installed data files, metadata, and console entry points.

> [!TIP]
> - `mapping_localization` is an `ament_python` package with multiple launch configurations for mapping, localization, and navigation. Execute only one launch file at a time to avoid a race condition.
> - The package was created with:
>   ```bash
>   ros2 pkg create --build-type ament_python mapping_localization --dependencies rclpy std_msgs geometry_msgs sensor_msgs nav_msgs ackermann_msgs
>   ```

## Setup and usage

### Simulator (digital twin)

1. From this lab directory, create a workspace and copy the package into its `src` directory:
    ```bash
    mkdir -p aueX930_ws/src
    cp -a mapping_localization aueX930_ws/src/
    ```
    Update any algorithm parameters within the respective `yaml` or `lua` file in the `config` directory.

2. Run the [`autodrive_neoracer_api`](https://hub.docker.com/r/autodriveecosystem/autodrive_neoracer_api) container with the workspace mounted:
   - `AMD64` Architecture:
       ```bash
        docker run --name autodrive_neoracer_api --rm -it --network=host --ipc=host -v /tmp/.X11-unix:/tmp/.X11-unix:rw -v "$PWD/aueX930_ws":/root/aueX930_ws --env DISPLAY --privileged --gpus all autodriveecosystem/autodrive_neoracer_api:2026-fall-amd64
       ```
   - `ARM64` Architecture:
       ```bash
        docker run --name autodrive_neoracer_api --rm -it --network=host --ipc=host -v "$PWD/aueX930_ws":/root/aueX930_ws --privileged autodriveecosystem/autodrive_neoracer_api:2026-fall-arm64
       ```

3. In the container, build and source the workspace:
    ```bash
    cd ~/aueX930_ws
    colcon build --symlink-install --packages-select mapping_localization
    source install/setup.bash
    ```

4. Run the [`autodrive_neoracer_sim`](https://hub.docker.com/r/autodriveecosystem/autodrive_neoracer_sim) container in a separate host terminal:
    ```bash
    docker run --name autodrive_neoracer_sim --rm -it --network=host --ipc=host -v /tmp/.X11-unix:/tmp/.X11-unix:rw --env DISPLAY --privileged --gpus all autodriveecosystem/autodrive_neoracer_sim:2026-fall-practice
    ```
    Alternatively, you can choose to use the standalone executable of the AutoDRIVE Simulator for [Linux](https://github.com/AutoDRIVE-Ecosystem/Clemson-University-AuE-X930-Tech-Stack/releases/download/2026-fall/autodrive_simulator_practice_linux.zip) | [Windows](https://github.com/AutoDRIVE-Ecosystem/Clemson-University-AuE-X930-Tech-Stack/releases/download/2026-fall/autodrive_simulator_practice_windows.zip) | [macOS](https://github.com/AutoDRIVE-Ecosystem/Clemson-University-AuE-X930-Tech-Stack/releases/download/2026-fall/autodrive_simulator_practice_macos.zip) depending on your requirement.

5. Teleoperate and bring the NeoRacer digital twin to a desired initial pose. Use the `Driving Mode Button` in the ` Menu Panel` on the left-hand side to toggle the driving mode of the vehicle between `Manual` and `Autonomous` (default is `Autonomous`). The selected driving mode is displayed beside this button. The vehicle will listen to the `/drive` topic while in `Autonomous` mode.

6. Launch the mapping (SLAM) algorithm:
    - Graph SLAM:
      ```bash
      ros2 launch mapping_localization slam_graph.launch.py
      ```
    - GMapping:
      ```bash
      ros2 launch mapping_localization slam_gmapping.launch.py
      ```
    - Cartographer:
      ```bash
      ros2 launch mapping_localization slam_cartographer.launch.py
      ```
    Stop the node with `Ctrl`+`C` before starting another node to avoid a race condition.

    While the node is running, you can teleoperate the vehicle using `teleop_keyboard`:
    ```bash
    ros2 run mapping_localization teleop_keyboard
    ```

    > [!NOTE]
    > Move the vehicle through the environment and inspect the map in RViz. Save the resulting map using the ROS 2 map-saving workflow before using it for localization.

7. Launch the localization algorithm:
    ```bash
    ros2 launch mapping_localization localization_amcl.launch.py
    ```
    Stop the node with `Ctrl`+`C` before starting another node to avoid a race condition.

    While the node is running, you can teleoperate the vehicle using `teleop_keyboard`:
    ```bash
    ros2 run mapping_localization teleop_keyboard
    ```
    
    > [!NOTE]
    > - Use RViz to provide an initial pose and inspect the estimated pose against the map.
    > - The supplied localization stack uses the package's `maps/map.yaml`; update the map used by the launch configuration when using a different map.

8. Launch the autonomous navigation algorithm:
    - Dynamic Window Approach (DWA):
      ```bash
      ros2 launch mapping_localization navigation_dwa.launch.py
      ```
    - Timed Elastic Band (TEB) Approach:
      ```bash
      ros2 launch mapping_localization navigation_teb.launch.py
      ```
    Stop the node with `Ctrl`+`C` before starting another node to avoid a race condition.

    > [!NOTE]
    > Set an initial pose and navigation goal in RViz, and monitor the planned paths and vehicle motion.

### Testbed (physical twin)

1. From this lab directory, create a workspace and copy the package into its `src` directory:
    ```bash
    mkdir -p aueX930_ws/src
    cp -a mapping_localization aueX930_ws/src/
    ```
    Update any algorithm parameters within the respective `yaml` or `lua` file in the `config` directory.

2. Build and source the workspace:
    ```bash
    cd ~/aueX930_ws
    colcon build --symlink-install --packages-select mapping_localization
    source install/setup.bash
    ```

3. Place the NeoRacer physical twin on the ground and make sure the area is secure for any experimentation. Flip the toggle switch (second from left) on the RC transmitter to the bottom position for the vehicle to listen to the `/drive` topic (i.e., operate in `Autonomous` mode). The toggle switch can be flipped to the top position during an autonomous run for manual override to avoid any collisions or accidents.

4. Launch the mapping (SLAM) algorithm:
    - Graph SLAM:
      ```bash
      ros2 launch mapping_localization slam_graph.launch.py
      ```
    - GMapping:
      ```bash
      ros2 launch mapping_localization slam_gmapping.launch.py
      ```
    - Cartographer:
      ```bash
      ros2 launch mapping_localization slam_cartographer.launch.py
      ```
    Stop the node with `Ctrl`+`C` before starting another node to avoid a race condition.

    While the node is running, you can teleoperate the vehicle using `teleop_keyboard`:
    ```bash
    ros2 run mapping_localization teleop_keyboard
    ```

    > [!NOTE]
    > Move the vehicle through the environment and inspect the map in RViz. Save the resulting map using the ROS 2 map-saving workflow before using it for localization.

5. Launch the localization algorithm:
    ```bash
    ros2 launch mapping_localization localization_amcl.launch.py
    ```
    Stop the node with `Ctrl`+`C` before starting another node to avoid a race condition.

    While the node is running, you can teleoperate the vehicle using `teleop_keyboard`:
    ```bash
    ros2 run mapping_localization teleop_keyboard
    ```
    
    > [!NOTE]
    > - Use RViz to provide an initial pose and inspect the estimated pose against the map.
    > - The supplied localization stack uses the package's `maps/map.yaml`; update the map used by the launch configuration when using a different map.

6. Launch the autonomous navigation algorithm:
    - Dynamic Window Approach (DWA):
      ```bash
      ros2 launch mapping_localization navigation_dwa.launch.py
      ```
    - Timed Elastic Band (TEB) Approach:
      ```bash
      ros2 launch mapping_localization navigation_teb.launch.py
      ```
    Stop the node with `Ctrl`+`C` before starting another node to avoid a race condition.

    > [!NOTE]
    > Set an initial pose and navigation goal in RViz, and monitor the planned paths and vehicle motion.
