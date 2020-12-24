"""This class is a handler and interfaces between the GUI and the motor clasess.
It translates all the basic commands into motor-class based code.
"""

from motor import Motor
from time import sleep

class Robot():

    def __init__(self):
        self.motor = Motor()

    # ReRoBot specific commands (selection)
    def nudge(self, dist=10.0):
        """Translate (+) forward or (-) back mm distance at SETV speed"""
        self.motor.cmd(self.motor.MOVE, value=dist)

    def move(self, speed=10.0):
        """Move forward (+) or reverse (-) at millimeters per second"""
        self.motor.cmd(self.motor.VEL, value=speed)

    def rvel(self, speed=10.0):
        """Rotate robot at (+) counter- or (–) clockwise; degrees/sec (SETRV limit)."""
        self.motor.cmd(self.motor.RVEL, value=speed)

    def head(self, degree=0.0):
        """Turn at SETRV speed to absolute heading; ±degrees (+ = ccw )"""
        self.motor.cmd(self.motor.HEAD, value=degree)

    def rotate(self, degrees=10.0):
        """Rotate (+) counter- or (-) clockwise degrees/sec."""
        self.motor.cmd(self.motor.ROTATE, value=degrees)

    def terminate(self):
        self.motor.terminate()

    # useful UI commands
    def step_forward(self):
        self.nudge(10)
        sleep(0.5)
        self.stop()

    def step_backward(self):
        self.nudge(-10)
        sleep(0.5)
        self.stop()

    def step_left(self):
        self.rvel(20)
        sleep(0.5)
        self.stop()

    def step_right(self):
        self.rvel(-20)
        sleep(0.5)
        self.stop()

    # Jetbot shared commands
    def set_motors(self, left_speed, right_speed):
        self.motor.left(left_speed)
        self.motor.right(right_speed)

    def reset_motors(self):
        self.motor.left(1)
        self.motor.right(1)

    def forward(self, speed=10.0):
        self.move(speed)

    def backward(self, speed=10.0):
        self.move(-speed)

    def stop(self):
        self.motor.stop()

    def left(self, speed=1.0):
        self.motor.left = -speed
        self.motor.right = speed
        self.move()

    def right(self, speed=1.0):
        self.motor.left = speed
        self.motor.right = -speed
        self.move()


