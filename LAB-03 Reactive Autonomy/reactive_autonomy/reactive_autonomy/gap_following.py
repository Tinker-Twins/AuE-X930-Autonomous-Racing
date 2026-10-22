#!/usr/bin/env python3

################################################################################

# Copyright (c) 2026, Tinker Twins, AutoDRIVE Ecosystem
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:

# 1. Redistributions of source code must retain the above copyright notice, this
#    list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

################################################################################

# ROS 2 module imports
import rclpy # ROS 2 client library (rcl) for Python (built on rcl C API)
from rclpy.node import Node # Node class for Python nodes
from sensor_msgs.msg import LaserScan # LaserScan (LIDAR range measurements) message class
from ackermann_msgs.msg import AckermannDriveStamped # Actuation (speed and steering commands) message class
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy # Quality of Service (tune communication between nodes)

# Python module imports
import numpy as np # Numerical computations

################################################################################

MAX_SPEED_MPS = 6.0 # DBW speed limit for the drive motor (m/s)
SAFE_SPEED_MPS = 1.5 # Safe speed limit for the vehicle (m/s)
MAX_STEER_RAD = 0.5236 # Maximum steering angle (rad)
LIDAR_SCAN_SIZE = 1440 # Number of samples in the LIDAR scan
LIDAR_ANG_RES = 0.25 # LIDAR angular resolution (degrees)
LIDAR_ANG_MIN = -180.0 # LIDAR angle of the first sample (degrees)

################################################################################

class Gap_Following(Node):
    def __init__(self):
        # Node infrastructure
        super().__init__('gap_following') # Create a node with name 'gap_following'
        qos_profile = QoSProfile( # Quality of Service profile
            reliability=ReliabilityPolicy.RELIABLE, # Reliable (not best effort) communication
            history=HistoryPolicy.KEEP_LAST, # Keep/store only up to last N samples
            depth=10 # Queue size/depth of 10 (only honored if the “history” policy was set to “keep last”)
        )

        # Node information
        info = '\nFind gaps and target the farthest reachable point to navigate the racetrack without collisions.\n'
        self.get_logger().info(info)

        # Node parameters
        self.declare_parameter('control_rate', 10.0) # Control loop execution rate (Hz)
        self.declare_parameter('speed_setpoint', 0.5) # Desired vehicle speed (m/s)
        self.declare_parameter('steer_smoothness', 0.8) # Smoothing factor for steering angle [0.0, 1.0]
        self.declare_parameter('min_scan_angle', -90.0) # Minimum scan angle for gap detection (degrees)
        self.declare_parameter('max_scan_angle', 90.0) # Maximum scan angle for gap detection (degrees)
        self.declare_parameter('vehicle_width', 0.25) # Width of vehicle footprint (m)
        self.declare_parameter('safety_margin', 0.10) # Safety margin around the vehicle (m)
        self.declare_parameter('disparity_threshold', 0.5) # Threshold for identifying a disparity (m)
        self.declare_parameter('perception_verbose', True) # Verbose perception output (boolean)
        self.declare_parameter('control_verbose', True) # Verbose control output (boolean)
        self.control_rate = self.get_parameter('control_rate').value
        self.speed_setpoint = self.get_parameter('speed_setpoint').value
        self.steer_smoothness = self.get_parameter('steer_smoothness').value
        self.min_scan_angle = self.get_parameter('min_scan_angle').value
        self.max_scan_angle = self.get_parameter('max_scan_angle').value
        self.vehicle_width = self.get_parameter('vehicle_width').value
        self.safety_margin = self.get_parameter('safety_margin').value
        self.disparity_threshold = self.get_parameter('disparity_threshold').value
        self.perception_verbose = self.get_parameter('perception_verbose').value
        self.control_verbose = self.get_parameter('control_verbose').value

        # Publishers and subscribers
        self.vehicle_scan_sub = self.create_subscription(LaserScan, '/scan', self.perception_callback, qos_profile) # Subscriber which will subscribe to LaserScan message on the topic '/scan' adhering to 'qos_profile' QoS profile
        self.vehicle_scan_sub # Prevent unused variable warning
        self.vehicle_ctrl_pub = self.create_publisher(AckermannDriveStamped, '/drive', qos_profile) # Publisher which will publish AckermannDriveStamped message to the topic '/drive' adhering to 'qos_profile' QoS profile
        timer_period = 1/self.control_rate # Node execution time period (seconds)
        self.create_timer(timer_period, self.parameter_callback) # Define timer to execute 'parameter_callback()' every 'timer_period' seconds
        self.create_timer(timer_period, self.control_callback) # Define timer to execute 'control_callback()' every 'timer_period' seconds

        # Member variables
        self.scan = np.full(LIDAR_SCAN_SIZE, np.inf) # Initialize variable to capture the laserscan
        self.filtered_scan = np.full(LIDAR_SCAN_SIZE, 0.0) # Initialize variable to store the filtered laserscan
        self.filtered_angles = np.full(LIDAR_SCAN_SIZE, 0.0) # Initialize variable to store the filtered angles
        self.ctrl_msg = AckermannDriveStamped() # Vehicle control commands
        self.steer_setpoint = 0.0
        self.steer_previous = 0.0

    def parameter_callback(self):
        names = (
            'control_rate',
            'speed_setpoint',
            'steer_smoothness',
            'min_scan_angle',
            'max_scan_angle',
            'vehicle_width',
            'safety_margin',
            'disparity_threshold',
            'perception_verbose',
            'control_verbose'
        )
        for parameter in self.get_parameters(names):
            setattr(self, parameter.name, parameter.value)

    def perception_callback(self, msg):
        self.scan = np.array(msg.ranges) # Capture the laserscan
        # Filter the laserscan samples to keep only those within the specified angular range
        scan_angles = LIDAR_ANG_MIN + np.arange(len(self.scan)) * LIDAR_ANG_RES # Compute angle of each laserscan sample (degrees)
        filtered_indices = np.where((scan_angles >= self.min_scan_angle) & (scan_angles <= self.max_scan_angle))[0] # Compute indices for filtering
        self.filtered_scan = self.scan[filtered_indices] # Filter the laserscan samples
        self.filtered_angles = scan_angles[filtered_indices] # Keep angles corresponding to the filtered samples
        if self.perception_verbose:
            self.get_logger().info('Original scan size: {:d} | Filtered scan size: {:d}'.format(len(self.scan), len(self.filtered_scan)))

    def control_callback(self):
        for index in range(len(self.filtered_scan) - 1):
            disparity = self.filtered_scan[index] - self.filtered_scan[index + 1] # Compute disparity between adjacent samples
            if abs(disparity) > self.disparity_threshold:
                closer_index = index if disparity < 0 else index + 1 # Find the closer point
                farther_index = index + 1 if disparity < 0 else index # Find the farther point
                # Extend the disparity to account for half vehicle width with a safety margin on either side
                extension = int(np.ceil(np.arctan2(self.vehicle_width/2 + self.safety_margin,
                                                   self.filtered_scan[closer_index]) / np.radians(LIDAR_ANG_RES)))
                # If the left sample is farther, extend the disparity toward the left (increasing indices in CCW direction)
                if farther_index > closer_index:
                    indices = range(farther_index, min(len(self.filtered_scan), farther_index + extension + 1))
                # If the right sample is farther, extend the disparity toward the right (decreasing indices in CW direction)
                else:
                    indices = range(max(0, farther_index - extension), farther_index + 1)
                # Mask the disparity-extended gap to the closer range measurement
                for sample_index in indices:
                    self.filtered_scan[sample_index] = min(self.filtered_scan[sample_index], self.filtered_scan[closer_index])

        # Find farthest reachable point in disparity-extended gap and compute the steering setpoint to target that point
        target_index = np.argmax(self.filtered_scan) # Find farthest reachable sample
        target_angle = self.filtered_angles[target_index] # Compute target angle
        self.steer_setpoint = self.steer_smoothness * self.steer_previous + (1 - self.steer_smoothness) * target_angle # Steering setpoint (degrees)
        self.steer_previous = self.steer_setpoint # Update previous steering setpoint for smoothing

        # Longitudinal control
        if self.speed_setpoint > SAFE_SPEED_MPS:
            self.speed_setpoint = SAFE_SPEED_MPS # Limit the speed setpoint to the safe speed
            if self.control_verbose:
                self.get_logger().warn('Speed setpoint limited to {} m/s'.format(self.speed_setpoint))
        self.ctrl_msg.drive.speed = self.speed_setpoint/MAX_SPEED_MPS # Set linear velocity (normalized)
        # Lateral control
        self.ctrl_msg.drive.steering_angle = max(-1.0, min(1.0, np.radians(self.steer_setpoint)/MAX_STEER_RAD)) # Set steering angle (normalized)
        self.vehicle_ctrl_pub.publish(self.ctrl_msg) # Publish vehicle control message
        if self.control_verbose:
            self.get_logger().info('Speed: {:.3f} m/s | Steer: {:.3f} rad | Target: {:.3f} deg'.format(self.ctrl_msg.drive.speed*MAX_SPEED_MPS,
                                                                                   self.ctrl_msg.drive.steering_angle*MAX_STEER_RAD,
                                                                                   target_angle))

################################################################################

def main(args=None):
    rclpy.init(args=args) # Start ROS 2 communications
    node = Gap_Following() # Create node
    rclpy.spin(node) # Execute node
    node.destroy_node() # Destroy node explicitly (optional - otherwise it will be done automatically when garbage collector destroys the node object)
    rclpy.shutdown() # Shutdown ROS 2 communications

################################################################################

if __name__ == "__main__":
    main()
