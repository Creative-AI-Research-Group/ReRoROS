# import pynput
from arm import Arm
from time import sleep
import tkinter as tk


class ArmGUI(tk.Frame):
    """ arm GUI & main """

    # defining global vars
    UPDATE_RATE = 100 # millisecs

    def __init__(self):
        # Create robot arm object
        self.arm = Arm()

        # Build GUI
        print('building arm GUI')
        self.gui = tk.Tk()
        self.gui.title("Arm Control")
        self.gui.geometry("700x500")
        self.gui.configure(background='light slate gray')

        # Initialize the Frame
        tk.Frame.__init__(self, self.gui)
        self.grid()
        self.rowconfigure([0, 1, 2, 3, 4], minsize=100, weight=1)
        self.columnconfigure([0, 1, 2, 3, 4], minsize=75, weight=1)

        # Build buttons and SIPS reporting (telemetry feedback)
        self.create_widgets()
        self.create_sips()

        # Start the updating cycle
        self.updater()

    def create_widgets(self):
        """create the interactive buttons"""
        btn_quit = tk.Button(master=self, text="1:ready", command=self.draw_ready, bg="red")
        btn_quit.grid(row=0, column=0, sticky="nsew")

        btn_up = tk.Button(master=self, text="2.open\njaw", command=self.open_claw, bg="green")
        btn_up.grid(row=0, column=1, sticky="nsew")

        btn_draw = tk.Button(master=self, text="3. close\njaw", command=self.close_claw, bg="red")
        btn_draw.grid(row=0, column=2, sticky="nsew")

        btn_quit = tk.Button(master=self, text="Q:QUIT", command=self.terminate, bg="red")
        btn_quit.grid(row=1, column=0, sticky="nsew")

        btn_up = tk.Button(master=self, text="W:fwd", command=self.draw_arm_fwd, bg="green")
        btn_up.grid(row=1, column=1, sticky="nsew")

        btn_draw = tk.Button(master=self, text="E:home", command=self.arm_home, bg="red")
        btn_draw.grid(row=1, column=2, sticky="nsew")

        btn_down = tk.Button(master=self, text="A:left", command=self.draw_arm_left, bg="green")
        btn_down.grid(row=2, column=0, sticky="nsew")

        btn_left = tk.Button(master=self, text="S:DRAW", command=self.arm_draw, bg="green")
        btn_left.grid(row=2, column=1, sticky="nsew")

        btn_draw = tk.Button(master=self, text="D:right", command=self.draw_arm_right, bg="red")
        btn_draw.grid(row=2, column=2, sticky="nsew")

        btn_right = tk.Button(master=self, text="Z:pen\nlift", command=self.pen_lift, bg="green")
        btn_right.grid(row=3, column=0, sticky="nsew")

        btn_right = tk.Button(master=self, text="X:back", command=self.draw_arm_bkwd, bg="green")
        btn_right.grid(row=3, column=1, sticky="nsew")

        btn_quit = tk.Button(master=self, text="C:pen\ndown", command=self.pen_down, bg="red")
        btn_quit.grid(row=3, column=2, sticky="nsew")

    def create_sips(self):
        """joint_dict_pos = {'myLSS1': 0, 'myLSS2': 0, 'myLSS3': 0, 'myLSS4': 0, 'myLSS5': 0}"""

        label_LSS1 = tk.Label(master=self, text=f"myLSS1 position = {self.arm.joint_dict_pos['myLSS1']}")
        label_LSS1.grid(row=0, column=4)

        label_LSS2 = tk.Label(master=self, text=f"myLSS2 position = {self.arm.joint_dict_pos['myLSS2']}")
        label_LSS2.grid(row=1, column=4)

        label_LSS3 = tk.Label(master=self, text=f"myLSS3 position = {self.arm.joint_dict_pos['myLSS3']}")
        label_LSS3.grid(row=2, column=4)

        label_LSS4 = tk.Label(master=self, text=f"myLSS4 position = {self.arm.joint_dict_pos['myLSS4']}")
        label_LSS4.grid(row=3, column=4)

        label_LSS5 = tk.Label(master=self, text=f"myLSS5 position = {self.arm.joint_dict_pos['myLSS5']}")
        label_LSS5.grid(row=4, column=4)

    def updater(self):
        # read incoming SIPS from LSS and parse to dict
        self.arm.get_positions()

        # refresh SIPS windows
        self.create_sips()

        # look for mouse position
        # mouse_pos = self.mouse_position()

        # move arm using mouse pos
        # parse arme movement here self.arm.draw(mouse_pos)

        # watch for keyboard commands
        # self.

        # "... and start all over again"
        self.after(self.UPDATE_RATE, self.updater)

    # move arm fwd by 0.5 degree relative
    def draw_arm_fwd(self):
        self.arm.move_joint_relative_speed(3, -5, 20)

    def draw_arm_bkwd(self):
        self.arm.move_joint_relative_speed(3, 5, 20)

    def draw_arm_right(self):
        self.arm.move_joint_relative_speed(1, 5, 20)

    def draw_arm_left(self):
        self.arm.move_joint_relative_speed(1, -5, 20)

    def arm_home(self):
        self.arm.home()

    def pen_lift(self):
        self.arm.move_joint_relative_speed(4, -5, 20)

    def pen_down(self):
        self.arm.move_joint_relative_speed(4, 5, 20)

    def draw_ready(self):
        self.arm.draw_ready()

    def open_claw(self):
        self.arm.open_claw()

    def close_claw(self):
        self.arm.close_claw()

    def arm_draw(self):
        self.arm.draw_ready()

    def keyboard_watcher(self):
        pass

    def mouse_position(self):
        # pos = pynput.mouse.get_pos()
        # return pos
        pass

    def terminate(self):
        print('terminator!!!')
        self.gui.destroy()
        sleep(1)
        self.arm.terminate()
        print("That's all folks!")
        exit()


if __name__ == "__main__":
    window = ArmGUI()
    window.mainloop()
