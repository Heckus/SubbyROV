"""
PID controller with anti-windup, derivative-on-measurement,
and optional angle-wrapping for heading control.
"""

import math


class PIDController:
    """
    A PID controller suitable for AUV attitude control.

    Features:
    - Derivative on measurement (avoids derivative kick on setpoint change)
    - Integral anti-windup via clamping
    - Angle-wrapping mode for yaw (handles ±180° boundary)
    - Output clamping to thruster limits
    """

    def __init__(
        self,
        kp: float,
        ki: float,
        kd: float,
        output_min: float = -1.0,
        output_max: float = 1.0,
        integral_limit: float = 0.3,
        wrap_angle: bool = False,
    ):
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.output_min = output_min
        self.output_max = output_max
        self.integral_limit = integral_limit
        self.wrap_angle = wrap_angle

        self._integral = 0.0
        self._prev_measurement = None  # for derivative-on-measurement

    def reset(self):
        self._integral = 0.0
        self._prev_measurement = None

    @staticmethod
    def _wrap_to_pi(angle: float) -> float:
        """Wrap angle to [-180, 180] degrees."""
        return (angle + 180.0) % 360.0 - 180.0

    def compute(
        self,
        setpoint: float,
        measurement: float,
        dt: float,
        measurement_rate: float = None,
    ) -> float:
        """
        Compute PID output.

        Args:
            setpoint:         Desired value (degrees for attitude DOFs).
            measurement:      Current sensor value.
            dt:               Time step in seconds.
            measurement_rate: If provided (e.g. gyro), used directly as the
                              derivative term — avoids numerical differentiation
                              noise. Sign: positive rate = increasing measurement.

        Returns:
            Clamped control output in [output_min, output_max].
        """
        if dt <= 0.0:
            return 0.0

        # --- Error ---
        error = setpoint - measurement
        if self.wrap_angle:
            error = self._wrap_to_pi(error)

        # --- Proportional ---
        p_term = self.kp * error

        # --- Integral with anti-windup ---
        self._integral += error * dt
        self._integral = max(
            -self.integral_limit,
            min(self.integral_limit, self._integral)
        )
        i_term = self.ki * self._integral

        # --- Derivative (on measurement to avoid kick) ---
        if measurement_rate is not None:
            # Use gyro directly — note sign: d(error)/dt = -d(measurement)/dt
            d_term = -self.kd * measurement_rate
        elif self._prev_measurement is not None:
            d_measurement = measurement - self._prev_measurement
            if self.wrap_angle:
                d_measurement = self._wrap_to_pi(d_measurement)
            d_term = -self.kd * (d_measurement / dt)
        else:
            d_term = 0.0

        self._prev_measurement = measurement

        # --- Sum and clamp ---
        output = p_term + i_term + d_term
        return max(self.output_min, min(self.output_max, output))