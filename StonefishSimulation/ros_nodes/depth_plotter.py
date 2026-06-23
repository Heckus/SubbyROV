#!/usr/bin/env python3
"""
depth_plotter.py
----------------
Live plot of ROV depth derived from the pressure sensor.

depth_m = pressure_pa / (water_density * gravity)

Run alongside Stonefish; optionally alongside station_keeping_node to watch
the controller converge on a target depth.
"""

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import FluidPressure
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from collections import deque

WATER_DENSITY = 1031.0   # kg/m^3  (matches ocean_environment.scn)
GRAVITY       = 9.81     # m/s^2
BUFFER_LEN    = 500      # ~10 s at 50 Hz


class DepthPlotter(Node):
    def __init__(self):
        super().__init__('depth_plotter')
        self.subscription = self.create_subscription(
            FluidPressure,
            '/qut_rov/pressure',
            self.pressure_callback,
            10)

        self.depth    = deque(maxlen=BUFFER_LEN)
        self.pressure = deque(maxlen=BUFFER_LEN)

    def pressure_callback(self, msg):
        p_pa  = msg.fluid_pressure
        depth = p_pa / (WATER_DENSITY * GRAVITY)
        self.pressure.append(p_pa)
        self.depth.append(depth)


def main():
    rclpy.init()
    node = DepthPlotter()

    fig, ax = plt.subplots(figsize=(10, 5))

    def update(frame):
        rclpy.spin_once(node, timeout_sec=0.01)
        ax.clear()
        ax.set_ylabel('Depth (m)')
        ax.set_xlabel('Sample')
        ax.set_title('ROV depth from pressure sensor')
        ax.grid(True)
        ax.invert_yaxis()  # depth increases downward
        if len(node.depth) > 0:
            ax.plot(list(node.depth), color='tab:blue', label='Depth (m)')
            ax.axhline(node.depth[-1], color='tab:gray', linestyle=':',
                       linewidth=0.8, alpha=0.6)
            ax.text(0.01, 0.95, f'current: {node.depth[-1]:.3f} m',
                    transform=ax.transAxes, va='top',
                    family='monospace', fontsize=10)
            ax.legend(loc='upper right')

    ani = animation.FuncAnimation(fig, update, interval=50)
    plt.show()

    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
