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

        # setup vars and consts
        # lifts draw head off page until ready to draw (mouse button)_
        self.draw_offset = -10
        # debug logging
        self.logging = True
        # detect if mouse is in frame
        self.ui_mouse_enter = False
        # canvas dims
        self.canvas_width = 750
        self.canvas_height = 900

        # Build GUI
        print('building arm GUI')
        self.gui = tk.Tk()
        self.gui.title("Arm Control")
        self.gui.geometry("1300x900")
        self.gui.configure(background='light slate gray')

        # Initialize the Frame
        tk.Frame.__init__(self, self.gui)
        self.grid()
        self.rowconfigure([0, 1, 2, 3, 4], minsize=100, weight=1)
        self.columnconfigure([0, 1, 2, 3, 4, 5, 6, 7, 8], minsize=75, weight=1)

        # create a canvas for drawing
        # create canvas
        self.canvas = tk.Canvas(self, width=self.canvas_width, height=self.canvas_height)
        self.canvas.grid(row=0, column=6, rowspan=5, columnspan=3)


        # binding events to tkinter
        # listen for keyboard commands
        self.gui.bind('<Key>', self.key_press)

        # # listen for mouse in frame
        # self.gui.bind('<Enter>', self.mouse_state)
        #
        # # listen for mouse control
        # self.gui.bind('<Motion>', self.move_arm_mouse)

        # listen for left mouse button (to engage draw)
        self.gui.bind('<B1-Motion>', self.paint)

        # Build buttons and SIPS reporting (telemetry feedback)
        self.create_widgets()
        self.create_sips()

        # Start the updating cycle
        self.ui_updater()

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

        # display joint positions
        label_LSS1 = tk.Label(master=self, text=f"myLSS1 position = {self.arm.joint_dict['myLSS1']['pos']}")
        label_LSS1.grid(row=0, column=3)

        label_LSS2 = tk.Label(master=self, text=f"myLSS2 position = {self.arm.joint_dict['myLSS2']['pos']}")
        label_LSS2.grid(row=1, column=3)

        label_LSS3 = tk.Label(master=self, text=f"myLSS3 position = {self.arm.joint_dict['myLSS3']['pos']}")
        label_LSS3.grid(row=2, column=3)

        label_LSS4 = tk.Label(master=self, text=f"myLSS4 position = {self.arm.joint_dict['myLSS4']['pos']}")
        label_LSS4.grid(row=3, column=3)

        label_LSS5 = tk.Label(master=self, text=f"myLSS5 position = {self.arm.joint_dict['myLSS5']['pos']}")
        label_LSS5.grid(row=4, column=3)

        # display joint current/load
        label_LSS1 = tk.Label(master=self, text=f"current = {self.arm.joint_dict['myLSS1']['load']}")
        label_LSS1.grid(row=0, column=4)

        label_LSS2 = tk.Label(master=self, text=f"current = {self.arm.joint_dict['myLSS2']['load']}")
        label_LSS2.grid(row=1, column=4)

        label_LSS3 = tk.Label(master=self, text=f"current = {self.arm.joint_dict['myLSS3']['load']}")
        label_LSS3.grid(row=2, column=4)

        label_LSS4 = tk.Label(master=self, text=f"current = {self.arm.joint_dict['myLSS4']['load']}")
        label_LSS4.grid(row=3, column=4)

        label_LSS5 = tk.Label(master=self, text=f"current = {self.arm.joint_dict['myLSS5']['load']}")
        label_LSS5.grid(row=4, column=4)

        # display joint speed
        label_LSS1 = tk.Label(master=self, text=f"speed = {self.arm.joint_dict['myLSS1']['speed']}")
        label_LSS1.grid(row=0, column=5)

        label_LSS2 = tk.Label(master=self, text=f"speed = {self.arm.joint_dict['myLSS2']['speed']}")
        label_LSS2.grid(row=1, column=5)

        label_LSS3 = tk.Label(master=self, text=f"speed = {self.arm.joint_dict['myLSS3']['speed']}")
        label_LSS3.grid(row=2, column=5)

        label_LSS4 = tk.Label(master=self, text=f"speed = {self.arm.joint_dict['myLSS4']['speed']}")
        label_LSS4.grid(row=3, column=5)

        label_LSS5 = tk.Label(master=self, text=f"speed = {self.arm.joint_dict['myLSS5']['speed']}")
        label_LSS5.grid(row=4, column=5)

    def ui_updater(self):
        # read incoming SIPS from LSS and parse to dict
        self.arm.get_telemetry()

        # refresh SIPS windows
        self.create_sips()

        # "... and start all over again"
        self.after(self.UPDATE_RATE, self.ui_updater)

    def key_press(self, event):
        key_pressed = event.keysym
        if self.logging:
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

    def paint(self, event):
        x1, y1 = (event.x - 1), (event.y - 1)
        x2, y2 = (event.x + 1), (event.y + 1)
        self.canvas.create_oval(x1, y1, x2, y2, fill="Black")
        self.move_arm_mouse(event.x, event.y)

    def mouse_state(self, event):
        print('############################ ', event.focus)
        if event.focus:
            self.ui_mouse_enter = True
        else:
            self.ui_mouse_enter = False

    def move_arm_mouse(self, x, y):
        if self.logging:
            print(f'mouse 1 x={x}, y={y}')

        # FLIP TO MAKE IT PORTRAIT & get trig list
        move_list = self.calc_arm_pos_trig(y, x)

        # move arm
        self.draw(move_list)

    def calc_arm_pos_trig(self, x, y):
        """x,y (top left = 0, 0) is opposite right corner of A4 page
        lss1_x_min = 290 - 63
        lss1_x_max = -73 - -420
        lss2 = 590 - -470
        lss3 = -740 - -520
        lss4 = 1000 - 870

        NewValue = (((OldValue - OldMin) * (NewMax - NewMin)) / (OldMax - OldMin)) + NewMin
        """
        lss2 = ((((y - 0) * (-470 - 590)) / (1400 - 0)) + 590) + self.draw_offset
        lss3 = (((y - 0) * (-510 - -740)) / (1400 - 0)) + -740
        lss4 = (((y - 0) * (870 - 1000)) / (1400 - 0)) + 1000

        lss1_x_min = (((y - 0) * (63 - 290)) / (1400 - 0)) + 1000
        lss1_x_max = (((y - 0) * (-420 - -73)) / (1400 - 0)) + 1000

        lss1 = (((x - 0) * (lss1_x_max - lss1_x_min)) / (1400 - 0)) + 1000
        if self.logging:
            print(f'lss1 pos = {lss1}, '
                  f'lss2 pos = {lss2}, '
                  f'lss3 pos = {lss3}, '
                  f'lss4 pos = {lss4}')

        move_list = [0, int(lss2), int(lss3), int(lss4), 0]
        return move_list

    def draw_button_on(self, event):
        while event:
            self.draw_offset = 0 # put draw head on page
        else:
            self.draw_offset = -10 # lifts draw head of page

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

    def draw(self, pos_list):
        self.arm.move_arm_speed(pos_list, 20)

    def reset(self):
        self.arm.reset_arm()


    def terminate(self):
        self.arm_home()
        print('terminator!!!')
        self.gui.destroy()
        sleep(1)
        self.arm.terminate()
        print("That's all folks!")
        exit()


if __name__ == "__main__":
    window = ArmGUI()
    window.mainloop()
