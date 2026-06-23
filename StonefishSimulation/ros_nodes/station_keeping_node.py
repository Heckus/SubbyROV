#!/usr/bin/env python3
"""
station_keeping_node.py
-----------------------
Depth-only station keeping for the qut_rov in Stonefish / ROS 2.

Keyboard Controls:
    s + ENTER = toggle depth keeping ON/OFF

Sensor:
    /qut_rov/pressure
    (sensor_msgs/FluidPressure, gauge pressure in Pa)

Actuator:
    /qut_rov/setpoint/thrusters
    (std_msgs/Float64MultiArray [TL, TR, BL, BR])

Depth conversion:
    depth_m = pressure_pa / (water_density * gravity)

Control:
    error = target_depth - current_depth

    too deep     -> thrust UP
    too shallow  -> thrust DOWN

    heave_cmd = -PID(error)

Thruster mixing:
    TL = heave_cmd
    TR = heave_cmd
    BL = 0
    BR = 0
"""

import os
import sys
import threading
import select

sys.path.insert(0, os.path.dirname(__file__))

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import FluidPressure
from std_msgs.msg import Float64MultiArray

from pid_controller import PIDController


class DepthKeepingNode(Node):

    def __init__(self):
        super().__init__("station_keeping_node")

        self._declare_parameters()
        self._load_parameters()

        self._build_controller()
        self._build_publisher()
        self._build_subscriber()

        self._prev_stamp = None
        self._log_counter = 0

        # Start disabled for safety
        self._enabled = False

        # Keyboard listener thread
        self._keyboard_thread = threading.Thread(
            target=self._keyboard_listener,
            daemon=True
        )
        self._keyboard_thread.start()

        self.get_logger().info(
            "\n"
            "========================================\n"
            "  Depth Keeping READY\n"
            "========================================\n"
            f"  target_depth = {self._target_depth:.2f} m\n"
            f"  max_pwm      = +/- {self._max_pwm}\n"
            f"  water rho    = {self._rho} kg/m^3\n"
            f"  enabled      = {self._enabled}\n"
            "\n"
            "  Press 's' + ENTER to toggle controller\n"
            "========================================"
        )

    # ------------------------------------------------------------------
    # Parameters
    # ------------------------------------------------------------------

    def _declare_parameters(self):

        self.declare_parameter("enabled", False)

        self.declare_parameter("target_depth_m", 4.0)

        self.declare_parameter("max_pwm", 600.0)

        self.declare_parameter("water_density", 1031.0)

        self.declare_parameter("gravity", 9.81)

        # PID gains
        self.declare_parameter("depth.kp", 150.0)
        self.declare_parameter("depth.ki", 5.0)
        self.declare_parameter("depth.kd", 80.0)

        self.declare_parameter("depth.integral_limit", 400.0)

        # Topics
        self.declare_parameter(
            "pressure_topic",
            "/qut_rov/pressure"
        )

        self.declare_parameter(
            "thruster_topic",
            "/qut_rov/setpoint/thrusters"
        )

    def _load_parameters(self):

        self._enabled = self.get_parameter("enabled").value

        self._target_depth = self.get_parameter(
            "target_depth_m"
        ).value

        self._max_pwm = self.get_parameter(
            "max_pwm"
        ).value

        self._rho = self.get_parameter(
            "water_density"
        ).value

        self._g = self.get_parameter(
            "gravity"
        ).value

    # ------------------------------------------------------------------
    # Controller
    # ------------------------------------------------------------------

    def _build_controller(self):

        self._depth_pid = PIDController(
            kp=self.get_parameter("depth.kp").value,
            ki=self.get_parameter("depth.ki").value,
            kd=self.get_parameter("depth.kd").value,

            integral_limit=self.get_parameter(
                "depth.integral_limit"
            ).value,

            output_min=-self._max_pwm,
            output_max=self._max_pwm,

            wrap_angle=False,
        )

    # ------------------------------------------------------------------
    # ROS setup
    # ------------------------------------------------------------------

    def _build_publisher(self):

        topic = self.get_parameter(
            "thruster_topic"
        ).value

        self._pub_thrusters = self.create_publisher(
            Float64MultiArray,
            topic,
            10
        )

    def _build_subscriber(self):

        topic = self.get_parameter(
            "pressure_topic"
        ).value

        self._sub_pressure = self.create_subscription(
            FluidPressure,
            topic,
            self._pressure_callback,
            10
        )

    # ------------------------------------------------------------------
    # Keyboard control
    # ------------------------------------------------------------------

    def _keyboard_listener(self):
        """
        Keyboard controls:
            s = toggle depth keeping
        """

        while rclpy.ok():

            if select.select([sys.stdin], [], [], 0.1)[0]:

                key = sys.stdin.readline().strip().lower()

                if key == "s":

                    self.set_enabled(not self._enabled)

    # ------------------------------------------------------------------
    # Main control loop
    # ------------------------------------------------------------------

    def _pressure_callback(self, msg: FluidPressure):

        # Compute dt
        stamp = (
            msg.header.stamp.sec
            + msg.header.stamp.nanosec * 1e-9
        )

        if self._prev_stamp is None:
            self._prev_stamp = stamp
            return

        dt = stamp - self._prev_stamp
        self._prev_stamp = stamp

        # Reject invalid timing
        if dt <= 0.0 or dt > 1.0:
            return

        # Disabled -> zero thrust
        if not self._enabled:

            self._publish_pwm(
                0.0,
                0.0,
                0.0,
                0.0
            )

            return

        # --------------------------------------------------------------
        # Pressure -> depth
        # --------------------------------------------------------------

        pressure_pa = msg.fluid_pressure

        depth_m = pressure_pa / (self._rho * self._g)

        # --------------------------------------------------------------
        # PID
        # --------------------------------------------------------------

        pid_out = self._depth_pid.compute(
            setpoint=self._target_depth,
            measurement=depth_m,
            dt=dt,
        )

        # Positive PWM should thrust upward
        heave_cmd = -pid_out

        # --------------------------------------------------------------
        # Thruster mixing
        # --------------------------------------------------------------

        tl = heave_cmd
        tr = heave_cmd

        bl = 0.0
        br = 0.0

        # --------------------------------------------------------------
        # Publish
        # --------------------------------------------------------------

        self._publish_pwm(
            tl,
            tr,
            bl,
            br
        )

        # --------------------------------------------------------------
        # Logging (~1 Hz)
        # --------------------------------------------------------------

        self._log_counter += 1

        if self._log_counter % 50 == 0:

            err = self._target_depth - depth_m

            self.get_logger().info(
                f"depth {depth_m:5.2f} m | "
                f"target {self._target_depth:.2f} m | "
                f"err {err:+5.2f} m | "
                f"PWM {heave_cmd:+7.1f}"
            )

    # ------------------------------------------------------------------
    # Publish helper
    # ------------------------------------------------------------------

    def _publish_pwm(self, tl, tr, bl, br):

        msg = Float64MultiArray()

        msg.data = [
            float(tl),
            float(tr),
            float(bl),
            float(br)
        ]

        self._pub_thrusters.publish(msg)

    # ------------------------------------------------------------------
    # Runtime control
    # ------------------------------------------------------------------

    def set_target_depth_m(self, depth_m: float):

        self._target_depth = depth_m

        self._depth_pid.reset()

        self.get_logger().info(
            f"New target depth: {depth_m:.2f} m"
        )

    def set_enabled(self, enabled: bool):

        self._enabled = enabled

        if not enabled:

            self._depth_pid.reset()

            self._publish_pwm(
                0.0,
                0.0,
                0.0,
                0.0
            )

        self.get_logger().info(
            f"Depth keeping "
            f"{'ENABLED' if enabled else 'DISABLED'}"
        )


def main(args=None):

    rclpy.init(args=args)

    node = DepthKeepingNode()

    try:
        rclpy.spin(node)

    except KeyboardInterrupt:
        pass

    finally:

        node.set_enabled(False)

        node.destroy_node()

        rclpy.shutdown()


if __name__ == "__main__":
    main()