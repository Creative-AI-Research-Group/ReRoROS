# -*- coding: utf-8 -*-

"""
JETSON terminal commands:
workon robot
list ports
FIX PERMISSIONS - sudo chmod 666 /dev/ttyUSB0
cd python
cd ReRoRos_v1
python3 basic_motion_UI.py
"""

from time import sleep
from rerobot import Robot
import tkinter as tk

class GUI(tk.Frame):
    """ GUI & main """

    # defining global vars
    UPDATE_RATE = 100 # millisecs
    SIPS_LOGGING = False

    def __init__(self):
        # Create robot move object and Comms inheritance
        self.robot = Robot()

        # Build GUI
        print('building GUI')
        self.gui = tk.Tk()
        self.gui.title("Robot Control")
        self.gui.geometry("700x500")
        self.gui.configure(background='light slate gray')

        # Initialize the Frame
        tk.Frame.__init__(self, self.gui)
        self.grid()
        self.rowconfigure([0, 1, 2, 3, 4, 5], minsize=100, weight=1)
        self.columnconfigure([0, 1, 2, 3, 4, 5, 6], minsize=75, weight=1)

        # Build buttons and SIPPS reporting
        self.create_widgets()
        if self.SIPS_LOGGING:
            self.create_sips()

        # Start the updating cycle
        self.updater()

    def on_press(self, event):
        # self.log("button was pressed")
        print(event)
        speed = self.speed_fdr.get()
        if event == "fwd":
            self.robot.forward()
        elif event == "bkwd":
            self.robot.backward()
        elif event == "right":
            self.robot.right()
        elif event == "left":
            self.robot.left()

    def on_release(self):
        # self.log("button was released")
        self.robot.stop()

    def create_widgets(self):
        """create the interactive buttons"""
        btn_step_forward = tk.Button(master=self, text="step\nforward", command=self.robot.step_forward, bg="green")
        btn_step_forward.grid(row=1, column=3, sticky="nsew")

        btn_step_backward = tk.Button(master=self, text="step\nbackward", command=self.robot.step_backward, bg="green")
        btn_step_backward.grid(row=3, column=3, sticky="nsew")

        btn_step_rvel_left = tk.Button(master=self, text="step\nleft", command=self.robot.step_left, bg="green")
        btn_step_rvel_left.grid(row=2, column=2, sticky="nsew")

        btn_stop = tk.Button(master=self, text="STOP", command=self.robot.stop, bg="red")
        btn_stop.grid(row=2, column=3, sticky="nsew")

        btn_step_rvel_right = tk.Button(master=self, text="step\nright", command=self.robot.step_right, bg="green")
        btn_step_rvel_right.grid(row=2, column=4, sticky="nsew")

        btn_quit = tk.Button(master=self, text="QUIT", command=self.terminate, bg="red")
        btn_quit.grid(row=4, column=5, sticky="nsew")

        # added continuous movement buttons
        # self.speed_fdr = tk.Scale(self.gui, from_=0, to=50)
        # self.speed_fdr.set(10)
        # self.speed_fdr.grid(row=0, column=0, rowspan=5, columnspan=1, sticky="nsew")
        #
        # btn_forward = tk.Button(master=self, text="forward", command=self.robot.step_forward, bg="green")
        # btn_forward.grid(row=0, column=3, sticky="nsew")
        # btn_forward.bind("<ButtonPress>", self.on_press("fwd"))
        # btn_forward.bind("<ButtonRelease>", self.on_release())
        #
        # btn_backward = tk.Button(master=self, text="backward", command=self.robot.step_backward, bg="green")
        # btn_backward.grid(row=4, column=3, sticky="nsew")
        # btn_backward.bind("<ButtonPress>", self.on_press("bkwd"))
        # btn_backward.bind("<ButtonRelease>", self.on_release())
        #
        # btn_rvel_left = tk.Button(master=self, text="left", command=self.robot.step_left, bg="green")
        # btn_rvel_left.grid(row=2, column=1, sticky="nsew")
        # btn_rvel_left.bind("<ButtonPress>", self.on_press("left"))
        # btn_rvel_left.bind("<ButtonRelease>", self.on_release())
        #
        # btn_rvel_right = tk.Button(master=self, text="right", command=self.robot.step_right, bg="green")
        # btn_rvel_right.grid(row=2, column=5, sticky="nsew")
        # btn_rvel_right.bind("<ButtonPress>", self.on_press("right"))
        # btn_rvel_right.bind("<ButtonRelease>", self.on_release())

        # gripper control
        btn_gpr_up = tk.Button(master=self, text="gripper\nup", command=self.robot.gripper_up, bg="blue")
        btn_gpr_up.grid(row=1, column=4, sticky="nsew")

        btn_pad_open = tk.Button(master=self, text="paddle\nopen", command=self.robot.paddle_open, bg="yellow")
        btn_pad_open.grid(row=4, column=2, sticky="nsew")

        btn_pad_close = tk.Button(master=self, text="paddle\nclose", command=self.robot.paddle_close, bg="yellow")
        btn_pad_close.grid(row=5, column=2, sticky="nsew")

        btn_gpr_down = tk.Button(master=self, text="gripper\ndown", command=self.robot.gripper_down, bg="blue")
        btn_gpr_down.grid(row=5, column=1, sticky="nsew")


    def create_sips(self):
        label_battery = tk.Label(master=self, text=f"Battery Level = {self.robot.motor.sips_dict.value['BATTERY']}")
        label_battery.grid(row=0, column=6)

        label_compass = tk.Label(master=self, text=f"Bumpers = {self.robot.motor.sips_dict.value['BUMPERS']}")
        label_compass.grid(row=1, column=6)

        label_heading = tk.Label(master=self, text=f"Actual Heading = {self.robot.motor.sips_dict.value['THPOS']}")
        label_heading.grid(row=2, column=6)

        label_left_wheel = tk.Label(master=self, text=f"Left Wheel Vel = {self.robot.motor.sips_dict.value['L_VEL']}")
        label_left_wheel.grid(row=3, column=6)

        label_right_wheel = tk.Label(master=self, text=f"Right Wheel Vel = {self.robot.motor.sips_dict.value['R_VEL']}")
        label_right_wheel.grid(row=4, column=6)

    def updater(self):
        if self.SIPS_LOGGING:
            # send SIP request
            self.robot.motor.send_sip_request()

            # read incoming SIPS from client robot
            self.robot.motor.parse_sip()

            # refresh SIPS windows
            self.create_sips()

        # send a heartbeat pulse
        self.robot.motor.pulse()

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
    window.mainloop()
