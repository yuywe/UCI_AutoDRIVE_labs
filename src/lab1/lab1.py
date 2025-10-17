#!/usr/bin/env python

# Import libraries
import socketio
import eventlet
from flask import Flask
import autodrive
from typing import Any, Optional, Tuple
import numpy as np
from dataclasses import dataclass

################################################################################


@dataclass
class PID:
    kp: float = 0.0
    ki: float = 0.0
    kd: float = 0.0
    setpoint: float = 0.0
    out_limits: Tuple[Optional[float], Optional[float]] = (-1.0, 1.0)
    integral: float = 0.0
    previous_error: Optional[float] = None

    def reset(self) -> None:
        self.integral = 0.0
        self.previous_error = None

    def update(self, measurement: float, dt: Optional[float]) -> float:
        error: float = self.setpoint - measurement
        if dt and dt > 0.0:
            self.integral += error * dt
        derivative: float = (
            (error - self.previous_error) / dt
            if dt and dt > 0.0 and self.previous_error is not None
            else 0.0
        )
        u: float = self.kp * error + self.ki * self.integral + self.kd * derivative
        low, high = self.out_limits
        if low is not None and u < low:
            u = low
        if high is not None and u > high:
            u = high
        self.previous_error = error
        return u


def get_range(
    lidar_range_array: np.ndarray[Any] | None,
    angle: float,
    min_angle: float = -3.0 * np.pi / 4.0,
    max_angle: float = 3.0 * np.pi / 4.0,
):
    angle_increment = (max_angle - min_angle) / lidar_range_array.size
    index = round((angle - min_angle) / angle_increment)
    if lidar_range_array is not None and index < lidar_range_array.size:
        return lidar_range_array[index]
    else:
        return 0.0


def get_distance_from_wall(lidar_range_array: np.ndarray[Any] | None):
    if lidar_range_array is None:
        return None

    theta_rad = np.deg2rad(45.0)
    a = get_range(lidar_range_array, -theta_rad)
    b = get_range(lidar_range_array, -np.pi / 2.0)
    if not np.isfinite(a) or not np.isfinite(b) or a <= 0.05 or b <= 0.05:
        return None

    alpha = np.arctan((a * np.cos(theta_rad) - b) / (a * np.sin(theta_rad)))
    distance = b * np.cos(alpha)
    return distance + 0.5 * np.sin(alpha)
    


# Initialize vehicle(s)
f1tenth_1 = autodrive.F1TENTH()
f1tenth_1.id = "V1"
steering_pid = PID(kp=0.8, kd=0.1, ki=0, setpoint=0.5)

# Initialize the server
sio = socketio.Server()

# Flask (web) app
app = Flask(__name__)  # '__main__'


# Registering "connect" event handler for the server
@sio.on("connect")
def connect(sid, environ):
    print("Connected!")


# Registering "Bridge" event handler for the server
@sio.on("Bridge")
def bridge(sid, data):
    if data:
        # Vehicle data
        f1tenth_1.parse_data(data)

        distance = get_distance_from_wall(f1tenth_1.lidar_range_array)
        if distance is None:
            distance = steering_pid.setpoint
        steering = steering_pid.update(distance, 1/f1tenth_1.lidar_scan_rate)
        # Vehicle control
        f1tenth_1.throttle_command = 0.4  # [-1, 1]
        f1tenth_1.steering_command = float(steering)

        ########################################################################

        json_msg = f1tenth_1.generate_commands()

        try:
            sio.emit("Bridge", data=json_msg)
        except Exception as exception_instance:
            print(exception_instance)


################################################################################

if __name__ == "__main__":
    app = socketio.Middleware(
        sio, app
    )  # Wrap flask application with socketio's middleware
    eventlet.wsgi.server(
        eventlet.listen(("", 4567)), app
    )  # Deploy as an eventlet WSGI server