# Mapping & Localization

**Authors:** [Chinmay Samak](https://www.linkedin.com/in/samakchinmay) and [Tanmay Samak](https://www.linkedin.com/in/samaktanmay)

```bash
cd ~/aueX930_ws
colcon build --symlink-install --packages-select mapping_localization
source install/setup.bash
```

## Mapping (SLAM)

```bash
ros2 launch mapping_localization slam_graph.launch.py
ros2 launch mapping_localization slam_gmapping.launch.py
ros2 launch mapping_localization slam_cartographer.launch.py
```

## Localization

```bash
ros2 launch mapping_localization localization_amcl.launch.py
```

## Navigation

```bash
ros2 launch mapping_localization nav_teb.launch.py
ros2 launch mapping_localization nav_dwa.launch.py
```