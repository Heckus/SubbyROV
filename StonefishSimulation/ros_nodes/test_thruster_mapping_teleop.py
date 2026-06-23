#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from std_msgs.msg import Float64MultiArray
import sys, termios, tty

PWM = 500.0

# Thruster order in your XML:
# [TL, TR, BL, BR]

class Teleop(Node):
    def __init__(self):
        super().__init__('teleop')
        self.pub = self.create_publisher(Float64MultiArray, '/qut_rov/setpoint/pwm', 10)

    def get_key(self):
        fd = sys.stdin.fileno()
        old = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            return sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old)

    def publish_thrust(self, thrust):
        msg = Float64MultiArray()
        msg.data = [float(v) for v in thrust]
        self.pub.publish(msg)
        print(f"Published: {msg.data}", flush=True)

    def run(self):
        print("""
Single thruster test mode

Thruster order:
  [TL, TR, BL, BR]

Keys:
  1 = TL forward
  2 = TR forward
  3 = BL forward
  4 = BR forward

  q = TL reverse
  w = TR reverse
  e = BL reverse
  r = BR reverse

  space = stop all
  x = exit
""")

        while True:
            key = self.get_key()

            thrust = [0.0, 0.0, 0.0, 0.0]

            if key == '1':
                print("TL forward", flush=True)
                thrust = [PWM, 0.0, 0.0, 0.0]

            elif key == '2':
                print("TR forward", flush=True)
                thrust = [0.0, PWM, 0.0, 0.0]

            elif key == '3':
                print("BL forward", flush=True)
                thrust = [0.0, 0.0, PWM, 0.0]

            elif key == '4':
                print("BR forward", flush=True)
                thrust = [0.0, 0.0, 0.0, PWM]

            elif key == 'q':
                print("TL reverse", flush=True)
                thrust = [-PWM, 0.0, 0.0, 0.0]

            elif key == 'w':
                print("TR reverse", flush=True)
                thrust = [0.0, -PWM, 0.0, 0.0]

            elif key == 'e':
                print("BL reverse", flush=True)
                thrust = [0.0, 0.0, -PWM, 0.0]

            elif key == 'r':
                print("BR reverse", flush=True)
                thrust = [0.0, 0.0, 0.0, -PWM]

            elif key == ' ':
                print("STOP", flush=True)
                thrust = [0.0, 0.0, 0.0, 0.0]

            elif key == 'x':
                print("Exit + stop", flush=True)
                self.publish_thrust([0.0, 0.0, 0.0, 0.0])
                break

            else:
                continue

            self.publish_thrust(thrust)


def main():
    rclpy.init()
    node = Teleop()
    try:
        node.run()
    finally:
        node.publish_thrust([0.0, 0.0, 0.0, 0.0])
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()

