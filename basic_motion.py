# -*- coding: utf-8 -*-

"""
JETSON terminal commands:
workon robot
list ports
FIX PERMISSIONS - sudo chmod 666 /dev/ttyUSB0
cd python
cd ReRoRos_v1
python3 basic_motion.py
"""

from time import sleep
from rerobot import Robot
from comms import Comms
import tkinter as tk
import atexit

class GUI(tk.Frame):
    """ GUI & main """

    # defining global vars
    UPDATE_RATE = 10

    def __init__(self):
        # Create robot move object
        self.robot = Robot()

        # Create robot comms object for SIPS
        self.comms = Comms()

        # Build GUI
        print('building GUI')
        self.gui = tk.Tk()
        self.gui.title("Robot Control")
        self.gui.geometry("700x500")

        # Initialize the Frame
        tk.Frame.__init__(self, self.gui)
        self.grid()
        self.rowconfigure([0, 1, 2, 3, 4], minsize=100, weight=1)
        self.columnconfigure([0, 1, 2, 3, 4], minsize=75, weight=1)

        # Build buttons and SIPPS reporting
        self.create_widgets()
        self.create_sips()

        # Start the updating cycle
        self.updater()

    def create_widgets(self):
        """create the interactive buttons"""
        btn_forward = tk.Button(master=self, text="forward", command=self.robot.step_forward, bg="green")
        btn_forward.grid(row=0, column=1, sticky="nsew")

        btn_backward = tk.Button(master=self, text="backward", command=self.robot.step_backward, bg="green")
        btn_backward.grid(row=2, column=1, sticky="nsew")

        btn_rvel_left = tk.Button(master=self, text="left", command=self.robot.step_left, bg="green")
        btn_rvel_left.grid(row=1, column=0, sticky="nsew")

        btn_stop = tk.Button(master=self, text="STOP", command=self.robot.stop, bg="red")
        btn_stop.grid(row=1, column=1, sticky="nsew")

        btn_rvel_right = tk.Button(master=self, text="right", command=self.robot.step_right, bg="green")
        btn_rvel_right.grid(row=1, column=2, sticky="nsew")

        btn_quit = tk.Button(master=self, text="QUIT", command=self.terminate, bg="red")
        btn_quit.grid(row=2, column=2, sticky="nsew")

    def create_sips(self):
        label_battery = tk.Label(master=self, text=f"Battery Level = {self.comms.BATTERY}")
        label_battery.grid(row=0, column=4)

        label_compass = tk.Label(master=self, text=f"Spare = 0")
        label_compass.grid(row=1, column=4)

        label_heading = tk.Label(master=self, text=f"Actual Heading = {self.comms.THPOS}")
        label_heading.grid(row=2, column=4)

        label_left_wheel = tk.Label(master=self, text=f"Left Wheel Vel = {self.comms.L_VEL}")
        label_left_wheel.grid(row=3, column=4)

        label_right_wheel = tk.Label(master=self, text=f"Right Wheel Vel = {self.comms.R_VEL}")
        label_right_wheel.grid(row=4, column=4)

    def updater(self):
        # read incoming SIPS from client robot
        self.comms.sip_read()

        # refresh SIPS windows
        self.create_sips()

        # send a heartbeat pulse
        self.comms.pulse()

        # "... and start all over again"
        self.after(self.UPDATE_RATE, self.updater)

    def terminate(self):
        print ('terminator!!!')
        self.gui.destroy()
        sleep(1)
        self.robot.terminate()
        print ("That's all folks!")
        exit()


if __name__ == "__main__":
    window = GUI()
