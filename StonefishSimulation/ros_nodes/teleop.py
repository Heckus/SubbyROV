#!/usr/bin/env python3
import sys
import select
import termios
import tty

import rclpy
from rclpy.node import Node
from std_msgs.msg import Float64MultiArray


class Teleop(Node):
    def __init__(self):
        super().__init__('teleop')
        self.pub = self.create_publisher(Float64MultiArray, '/qut_rov/setpoint/thrusters', 10)
        self.timer = self.create_timer(0.05, self.timer_callback)  # 20 Hz

        self.thruster_cmd =600.0  # 100% throttle
        self.thrust = [0.0, 0.0, 0.0, 0.0]

        self.old_terminal_settings = termios.tcgetattr(sys.stdin)
        tty.setcbreak(sys.stdin.fileno())

        print("Controls (TOGGLE MODE):")
        print("  w = forward")
        print("  s = backward")
        print("  a = left")
        print("  d = right")
        print("  q = up")
        print("  e = down")
        print("  space = stop")
        print("  x = exit")
        print("")
        print("Press once to change command.")

    def read_key_nonblocking(self):
        if select.select([sys.stdin], [], [], 0.0)[0]:
            return sys.stdin.read(1)
        return None

    def timer_callback(self):
        key = self.read_key_nonblocking()

        if key is not None:
            if key == 'w':
                self.thrust = [0.0, 0.0, self.thruster_cmd, self.thruster_cmd]
                print("Forward", flush=True)

            elif key == 's':
                self.thrust = [0.0, 0.0, -self.thruster_cmd, -self.thruster_cmd]
                print("Backward", flush=True)

            elif key == 'a':
                self.thrust = [0.0, 0.0, 0.5*self.thruster_cmd, self.thruster_cmd]
                print("Left", flush=True)

            elif key == 'd':
                self.thrust = [0.0, 0.0, self.thruster_cmd, 0.5*self.thruster_cmd]
                print("Right", flush=True)


            elif key == 'q':
                self.thrust = [self.thruster_cmd, self.thruster_cmd, 0.0, 0.0]
                print("Up", flush=True)

            elif key == 'e':
                self.thrust = [-self.thruster_cmd, -self.thruster_cmd, 0.0, 0.0]
                print("Down", flush=True)

            elif key == ' ':
                self.thrust = [0.0, 0.0, 0.0, 0.0]
                print("Stop", flush=True)

            elif key == 'x':
                print("Exit", flush=True)
                self.thrust = [0.0, 0.0, 0.0, 0.0]
                self.publish_thrust()
                self.cleanup()
                rclpy.shutdown()
                return

        # Always keep publishing current command
        self.publish_thrust()

    def publish_thrust(self):
        msg = Float64MultiArray()
        msg.data = self.thrust
        self.pub.publish(msg)

    def cleanup(self):
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, self.old_terminal_settings)


def main():
    rclpy.init()
    node = Teleop()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.thrust = [0.0, 0.0, 0.0, 0.0]
        node.publish_thrust()
        node.cleanup()
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()