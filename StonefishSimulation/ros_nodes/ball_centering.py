#!/usr/bin/env python3
"""
ball_centering_node.py
----------------------
Detects a green ball in the camera feed and centres it in the frame
by controlling the ROV's yaw and pitch thrusters.

Keyboard Controls:
    c + ENTER = toggle centering ON/OFF

Sensor:
    /qut_rov/left/image_color

Actuator:
    /qut_rov/setpoint/thrusters
    (std_msgs/Float64MultiArray [TL, TR, BL, BR])

Control:
    x_error = ball_x - frame_centre_x  -> yaw correction  (left/right)
    y_error = ball_y - frame_centre_y  -> pitch correction (up/down)
"""

import os
import sys
import threading
import select
from collections import deque

import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import matplotlib.animation as animation

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from std_msgs.msg import Float64MultiArray
import numpy as np
import cv2

sys.path.insert(0, os.path.dirname(__file__))
from pid_controller import PIDController


class BallCenteringNode(Node):

    def __init__(self):
        super().__init__('ball_centering_node')

        # --- Parameters ---
        self.declare_parameter('max_pwm', 600.0)
        self.declare_parameter('image_topic', '/qut_rov/left/image_color')
        self.declare_parameter('thruster_topic', '/qut_rov/setpoint/thrusters')

        # HSV colour range for the green ball - tune if needed
        self.declare_parameter('hue_low',  40)
        self.declare_parameter('hue_high', 80)
        self.declare_parameter('sat_low',  80)
        self.declare_parameter('val_low',  80)

        # PID gains
        self.declare_parameter('yaw.kp',   2)
        self.declare_parameter('yaw.ki',   1)
        self.declare_parameter('yaw.kd',   0.5)

        self.declare_parameter('pitch.kp', 20)
        self.declare_parameter('pitch.ki', 15)
        self.declare_parameter('pitch.kd', 10)

        self._max_pwm = self.get_parameter('max_pwm').value

        # --- PID controllers ---
        self._yaw_pid = PIDController(
            kp=self.get_parameter('yaw.kp').value,
            ki=self.get_parameter('yaw.ki').value,
            kd=self.get_parameter('yaw.kd').value,
            output_min=-self._max_pwm,
            output_max=self._max_pwm,
            wrap_angle=False,
        )

        self._pitch_pid = PIDController(
            kp=self.get_parameter('pitch.kp').value,
            ki=self.get_parameter('pitch.ki').value,
            kd=self.get_parameter('pitch.kd').value,
            output_min=-self._max_pwm,
            output_max=self._max_pwm,
            wrap_angle=False,
        )

        # --- State ---
        self._enabled = True
        self._prev_stamp = None
        self._log_counter = 0
        self._latest_frame = None

        # --- Plot data ---
        self._y_err_hist = deque(maxlen=200)

        # --- Publisher ---
        self._pub = self.create_publisher(
            Float64MultiArray,
            self.get_parameter('thruster_topic').value,
            10
        )

        # --- Subscriber ---
        self.create_subscription(
            Image,
            self.get_parameter('image_topic').value,
            self._image_callback,
            10
        )

        # --- Keyboard thread ---
        threading.Thread(
            target=self._keyboard_listener,
            daemon=True
        ).start()

        self.get_logger().info(
            "\n"
            "========================================\n"
            "  Ball Centering READY\n"
            "========================================\n"
            "  Press 'c' + ENTER to toggle\n"
            "========================================"
        )

    # ------------------------------------------------------------------
    # Keyboard
    # ------------------------------------------------------------------

    def _keyboard_listener(self):
        while rclpy.ok():
            if select.select([sys.stdin], [], [], 0.1)[0]:
                key = sys.stdin.readline().strip().lower()
                if key == 'c':
                    self._enabled = not self._enabled
                    if not self._enabled:
                        self._yaw_pid.reset()
                        self._pitch_pid.reset()
                        self._publish_pwm(0.0, 0.0, 0.0, 0.0)
                    self.get_logger().info(
                        f"Ball centering "
                        f"{'ENABLED' if self._enabled else 'DISABLED'}"
                    )

    # ------------------------------------------------------------------
    # Image callback
    # ------------------------------------------------------------------

    def _image_callback(self, msg: Image):

        # Compute dt from header stamp
        stamp = msg.header.stamp.sec + msg.header.stamp.nanosec * 1e-9
        if self._prev_stamp is None:
            self._prev_stamp = stamp
            return
        dt = stamp - self._prev_stamp
        self._prev_stamp = stamp
        if dt <= 0.0 or dt > 1.0:
            return

        # Convert ROS image to numpy array manually (avoid cv_bridge numpy conflict)
        frame = np.frombuffer(msg.data, dtype=np.uint8).reshape(
            msg.height, msg.width, -1)

        # Keep as RGB for matplotlib display
        frame_rgb = frame.copy()

        # BGR copy for OpenCV processing only
        frame_bgr = frame[:, :, ::-1].copy()

        h, w = frame_bgr.shape[:2]
        cx = w // 2
        cy = h // 2

        # --- Detect green ball ---
        hsv = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2HSV)

        lower = np.array([
            self.get_parameter('hue_low').value,
            self.get_parameter('sat_low').value,
            self.get_parameter('val_low').value,
        ])
        upper = np.array([
            self.get_parameter('hue_high').value,
            255,
            255,
        ])

        mask = cv2.inRange(hsv, lower, upper)
        mask = cv2.erode(mask,  None, iterations=2)
        mask = cv2.dilate(mask, None, iterations=2)

        contours, _ = cv2.findContours(
            mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Draw crosshair on RGB frame
        cv2.drawMarker(frame_rgb, (cx, cy), (255, 255, 255),
                       cv2.MARKER_CROSS, 20, 2)

        if not contours:
            self._latest_frame = frame_rgb
            self._publish_pwm(0.0, 0.0, 0.0, 0.0)
            return

        # Largest contour = ball
        c = max(contours, key=cv2.contourArea)
        ((bx, by), radius) = cv2.minEnclosingCircle(c)

        # Ignore tiny detections
        if radius < 5:
            self._latest_frame = frame_rgb
            self._publish_pwm(0.0, 0.0, 0.0, 0.0)
            return

        # --- Pixel error from centre ---
        x_err = bx - cx   # positive = ball is right of centre
        y_err = by - cy   # positive = ball is below centre

        # --- Record for plot ---
        self._y_err_hist.append(y_err)

        # --- Draw bounding box and info on RGB frame ---
        x_box, y_box, w_box, h_box = cv2.boundingRect(c)

        cv2.rectangle(frame_rgb,
                      (x_box, y_box),
                      (x_box + w_box, y_box + h_box),
                      (0, 255, 0), 2)

        cv2.circle(frame_rgb, (int(bx), int(by)), int(radius),
                   (0, 255, 0), 2)

        cv2.circle(frame_rgb, (int(bx), int(by)), 4,
                   (255, 0, 0), -1)

        cv2.putText(frame_rgb,
                    f"x={int(bx)} y={int(by)}",
                    (x_box, y_box - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

        cv2.putText(frame_rgb,
                    f"err x={int(x_err):+d} y={int(y_err):+d}",
                    (x_box, y_box - 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)

        self._latest_frame = frame_rgb

        if not self._enabled:
            self._publish_pwm(0.0, 0.0, 0.0, 0.0)
            return

        # --- PID ---
        yaw_cmd   = self._yaw_pid.compute(
            setpoint=0.0, measurement=x_err, dt=dt)
        pitch_cmd = self._pitch_pid.compute(
            setpoint=0.0, measurement=y_err, dt=dt)

        # --- Thruster mixing ---
        BUOYANCY_OFFSET = 185.0
        if -BUOYANCY_OFFSET < pitch_cmd < 0:
            tl =  -BUOYANCY_OFFSET
            tr =  -BUOYANCY_OFFSET
        else:
            tl =  pitch_cmd
            tr =  pitch_cmd


        if x_err > 0:
            bl =  yaw_cmd
            br = 0
        else:  
            bl = 0 
            br =  yaw_cmd          

        self._log_counter += 1
        if self._log_counter % 15 == 0:
            self.get_logger().info(
                f"Ball at ({bx:.0f}, {by:.0f}) | "
                f"err x={x_err:+.0f} y={y_err:+.0f} px | "
                f"r={radius:.0f}px | "
                f"enabled={self._enabled}"
            )
            if self._enabled:
                self.get_logger().info(
                    f"PWM -> TL={tl:+.1f} TR={tr:+.1f} BL={bl:+.1f} BR={br:+.1f}"
                )

        self._publish_pwm(tl, tr, bl, br)

    # ------------------------------------------------------------------
    # Publish
    # ------------------------------------------------------------------

    def _publish_pwm(self, tl, tr, bl, br):
        def clamp(v):
            return max(-self._max_pwm, min(self._max_pwm, v))
        msg = Float64MultiArray()
        msg.data = [clamp(tl), clamp(tr), clamp(bl), clamp(br)]
        self._pub.publish(msg)

    def destroy_node(self):
        super().destroy_node()


def main(args=None):
    rclpy.init(args=args)
    node = BallCenteringNode()

    # Spin ROS in background thread
    ros_thread = threading.Thread(target=rclpy.spin, args=(node,), daemon=True)
    ros_thread.start()

    # Run matplotlib in main thread
    fig, (ax_img, ax_err) = plt.subplots(1, 2, figsize=(12, 4))
    fig.suptitle('Ball Centering Monitor')

    def update(frame):
        ax_err.clear()
        ax_err.plot(list(node._y_err_hist), color='tab:red',
                    label='Y error (px)')
        ax_err.axhline(0, color='black', linewidth=0.8, linestyle='--')
        ax_err.set_ylim(-250, 250)   # fixed scale matching half frame height
        ax_err.set_ylabel('Y error (px)')
        ax_err.set_title('Ball Y Error (+ = ball below centre)')
        ax_err.legend(loc='upper right')
        ax_err.grid(True)

        if node._latest_frame is not None:
            ax_img.clear()
            ax_img.imshow(node._latest_frame)
            ax_img.set_title('Ball Detection')
            ax_img.axis('off')

    ani = animation.FuncAnimation(fig, update, interval=100)
    plt.tight_layout()

    try:
        plt.show()
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()