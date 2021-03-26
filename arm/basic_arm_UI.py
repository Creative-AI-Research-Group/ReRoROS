# from pynput.mouse import Listener
# from pynput import Key
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

        # binding events to tkinter
        # listen for keyboard commands
        self.gui.bind('<Key>', self.key_press)

        # listen for mouse control
        self.gui.bind('<B1-Motion>', self.draw_arm_mouse)
        self.gui.bind('<B2-Motion>', self.move_arm_mouse)

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

        btn_up = tk.Button(master=self, text="2.open\nclaw", command=self.open_claw, bg="green")
        btn_up.grid(row=0, column=1, sticky="nsew")

        btn_draw = tk.Button(master=self, text="3. close\nclaw", command=self.close_claw, bg="red")
        btn_draw.grid(row=0, column=2, sticky="nsew")

        btn_up = tk.Button(master=self, text="w:fwd", command=self.draw_arm_fwd, bg="green")
        btn_up.grid(row=1, column=1, sticky="nsew")

        btn_down = tk.Button(master=self, text="a:left", command=self.draw_arm_left, bg="green")
        btn_down.grid(row=2, column=0, sticky="nsew")

        btn_left = tk.Button(master=self, text="s:DRAW", command=self.arm_draw, bg="green")
        btn_left.grid(row=2, column=1, sticky="nsew")

        btn_draw = tk.Button(master=self, text="d:right", command=self.draw_arm_right, bg="red")
        btn_draw.grid(row=2, column=2, sticky="nsew")

        btn_right = tk.Button(master=self, text="z:pen\nlift", command=self.pen_lift, bg="green")
        btn_right.grid(row=3, column=0, sticky="nsew")

        btn_right = tk.Button(master=self, text="x:back", command=self.draw_arm_bkwd, bg="green")
        btn_right.grid(row=3, column=1, sticky="nsew")

        btn_quit = tk.Button(master=self, text="c:pen\ndown", command=self.pen_down, bg="red")
        btn_quit.grid(row=3, column=2, sticky="nsew")

        btn_quit = tk.Button(master=self, text="Esc:quit", command=self.terminate, bg="red")
        btn_quit.grid(row=4, column=0, sticky="nsew")

        btn_right = tk.Button(master=self, text="r:reset", command=self.reset, bg="green")
        btn_right.grid(row=4, column=1, sticky="nsew")

        btn_draw = tk.Button(master=self, text="h:home", command=self.arm_home, bg="red")
        btn_draw.grid(row=4, column=2, sticky="nsew")

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
        # self.mouse_position()

        # move arm using mouse pos
        # parse arme movement here self.arm.draw(mouse_pos)


        # "... and start all over again"
        self.after(self.UPDATE_RATE, self.updater)

    def key_press(self, event):
        key_pressed = event.keysym
        print('{0} pressed'.format(event.keysym))
        if key_pressed == '1':
            self.draw_ready()
        if key_pressed == '2':
            self.open_claw()
        if key_pressed == '3':
            self.close_claw()
        if key_pressed == 'w':
            self.draw_arm_fwd()
        if key_pressed == 'a':
            self.draw_arm_left()
        if key_pressed == 's':
            self.arm_draw()
        if key_pressed == 'd':
            self.draw_arm_right()
        if key_pressed == 'z':
            self.pen_lift()
        if key_pressed == 'x':
            self.draw_arm_bkwd()
        if key_pressed == 'c':
            self.pen_down()
        if key_pressed == 'Escape':
            self.terminate()
        if key_pressed == 'r':
            self.reset()
        if key_pressed == 'h':
            self.arm_home()

    def move_arm_mouse(self, event):
        print(f'mouse 1 x={event.x}, y={event.y}')

    def draw_arm_mouse(self, event):
        print(f'mouse 2 x={event.x}, y={event.y}')

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
        self.arm.move_joint_relative_speed(5, -140, 20)

    def close_claw(self):
        self.arm.move_joint_relative_speed(5, 140, 20)

    def arm_draw(self):
        self.arm.draw()

    def reset(self):
        self.arm.reset_arm()

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
