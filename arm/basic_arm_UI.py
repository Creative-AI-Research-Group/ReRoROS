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
        # debug logging
        self.logging = True

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
        # arm control blob
        self.img = tk.PhotoImage(file="data/200px-Light_Blue_Circle.svg.png")

        # create canvas
        self.canvas = tk.Canvas(self, width=self.canvas_width, height=self.canvas_height)
        self.canvas.grid(row=0, column=6, rowspan=5, columnspan=3)
        self.cimg = self.canvas.create_image(300, 450, image=self.img)

        # binding events to tkinter
        # listen for keyboard commands
        self.gui.bind('<KeyPress>', self.key_press)
        self.gui.bind('<KeyRelease>', self.key_release)

        # listen for left mouse button (to engage draw)
        self.gui.bind('<B1-Motion>', self.paint)

        # # listen for keyboard commands
        # self.gui.bind('<space>', self.space_press_on)

        # self.gui.bind('<space-release>', self.space_press_off)

        # Build buttons and SIPS reporting (telemetry feedback)
        self.create_widgets()
        self.create_sips()

        # Start the updating cycle
        self.ui_updater()

    def create_widgets(self):
        """create the interactive buttons"""
        btn_quit = tk.Button(master=self, text="1:ready", command=self.waiting_pos, bg="red")
        btn_quit.grid(row=0, column=0, sticky="nsew")

        btn_up = tk.Button(master=self, text="2.open\nclaw", command=self.open_claw, bg="green")
        btn_up.grid(row=0, column=1, sticky="nsew")

        btn_draw = tk.Button(master=self, text="3. close\nclaw", command=self.close_claw, bg="red")
        btn_draw.grid(row=0, column=2, sticky="nsew")

        btn_up = tk.Button(master=self, text="w:fwd", command=self.draw_arm_fwd, bg="green")
        btn_up.grid(row=1, column=1, sticky="nsew")

        btn_down = tk.Button(master=self, text="a:left", command=self.draw_arm_left, bg="green")
        btn_down.grid(row=2, column=0, sticky="nsew")

        btn_left = tk.Button(master=self, text="s:DRAW", command=self.draw_ready_pos_draw, bg="green")
        btn_left.grid(row=2, column=1, sticky="nsew")

        btn_draw = tk.Button(master=self, text="d:right", command=self.draw_arm_right, bg="red")
        btn_draw.grid(row=2, column=2, sticky="nsew")

        # btn_right = tk.Button(master=self, text="z:draw\nmode", command=self.draw_mode, bg="green")
        # btn_right.grid(row=3, column=0, sticky="nsew")

        btn_right = tk.Button(master=self, text="x:back", command=self.draw_arm_bkwd, bg="green")
        btn_right.grid(row=3, column=1, sticky="nsew")

        # btn_quit = tk.Button(master=self, text="c:arm\nmode", command=self.arm_mode, bg="red")
        # btn_quit.grid(row=3, column=2, sticky="nsew")

        btn_quit = tk.Button(master=self, text="Esc:quit", command=self.terminate, bg="red")
        btn_quit.grid(row=4, column=0, sticky="nsew")

        btn_right = tk.Button(master=self, text="r:reset", command=self.reset, bg="green")
        btn_right.grid(row=4, column=1, sticky="nsew")

        btn_draw = tk.Button(master=self, text="h:home", command=self.arm_home, bg="red")
        btn_draw.grid(row=4, column=2, sticky="nsew")

    def create_sips(self):
        """joint_dict_pos = {'myLSS1': 0, 'myLSS2': 0, 'myLSS3': 0, 'myLSS4': 0, 'myLSS5': 0}"""

        # display joint positions
        label_LSS1 = tk.Label(master=self, text=f"myLSS1 position = {self.arm.joint_dict['base']['pos']}")
        label_LSS1.grid(row=0, column=3)

        label_LSS2 = tk.Label(master=self, text=f"myLSS2 position = {self.arm.joint_dict['shoulder']['pos']}")
        label_LSS2.grid(row=1, column=3)

        label_LSS3 = tk.Label(master=self, text=f"myLSS3 position = {self.arm.joint_dict['elbow']['pos']}")
        label_LSS3.grid(row=2, column=3)

        label_LSS4 = tk.Label(master=self, text=f"myLSS4 position = {self.arm.joint_dict['wrist']['pos']}")
        label_LSS4.grid(row=3, column=3)

        label_LSS5 = tk.Label(master=self, text=f"myLSS5 position = {self.arm.joint_dict['gripper']['pos']}")
        label_LSS5.grid(row=4, column=3)

        # display joint current/load
        label_LSS1 = tk.Label(master=self, text=f"current = {self.arm.joint_dict['base']['load']}")
        label_LSS1.grid(row=0, column=4)

        label_LSS2 = tk.Label(master=self, text=f"current = {self.arm.joint_dict['shoulder']['load']}")
        label_LSS2.grid(row=1, column=4)

        label_LSS3 = tk.Label(master=self, text=f"current = {self.arm.joint_dict['elbow']['load']}")
        label_LSS3.grid(row=2, column=4)

        label_LSS4 = tk.Label(master=self, text=f"current = {self.arm.joint_dict['wrist']['load']}")
        label_LSS4.grid(row=3, column=4)

        label_LSS5 = tk.Label(master=self, text=f"current = {self.arm.joint_dict['gripper']['load']}")
        label_LSS5.grid(row=4, column=4)

        # display joint speed
        label_LSS1 = tk.Label(master=self, text=f"speed = {self.arm.joint_dict['base']['speed']}")
        label_LSS1.grid(row=0, column=5)

        label_LSS2 = tk.Label(master=self, text=f"speed = {self.arm.joint_dict['shoulder']['speed']}")
        label_LSS2.grid(row=1, column=5)

        label_LSS3 = tk.Label(master=self, text=f"speed = {self.arm.joint_dict['elbow']['speed']}")
        label_LSS3.grid(row=2, column=5)

        label_LSS4 = tk.Label(master=self, text=f"speed = {self.arm.joint_dict['wrist']['speed']}")
        label_LSS4.grid(row=3, column=5)

        label_LSS5 = tk.Label(master=self, text=f"speed = {self.arm.joint_dict['gripper']['speed']}")
        label_LSS5.grid(row=4, column=5)

    def ui_updater(self):
        # read incoming SIPS from LSS and parse to dict
        self.arm.get_telemetry()

        # refresh SIPS windows
        self.create_sips()

        # "... and start all over again"
        self.after(self.UPDATE_RATE, self.ui_updater)

    def key_release(self, event):
        key_released = event.keysym
        if key_released == 'Shift_L':
            self.arm.pen_drawing_status = False
            self.arm.led_blue()

    def key_press(self, event):
        key_pressed = event.keysym
        key_pressed.lower()
        if self.logging:
            print(f'{key_pressed} pressed')
        if key_pressed == '1':
            self.waiting_pos()
        if key_pressed == '2':
            self.open_claw()
        if key_pressed == '3':
            self.close_claw()
        if key_pressed == 'w':
            self.draw_arm_fwd()
        if key_pressed == 'a':
            self.draw_arm_left()
        if key_pressed == 's':
            self.draw_ready_pos_draw()
        if key_pressed == 'd':
            self.draw_arm_right()
        if key_pressed == 'h':
            self.arm_home()
        if key_pressed == 'x':
            self.draw_arm_bkwd()
        # if key_pressed == 'c':
        #     self.arm_mode()
        if key_pressed == 'Escape':
            self.terminate()
        if key_pressed == 'r':
            self.reset()
        if key_pressed == 'Shift_L':
            self.arm.pen_drawing_status = True
            self.arm.led_red()

    def paint(self, event):
        x1, y1 = (event.x - 1), (event.y - 1)
        x2, y2 = (event.x + 1), (event.y + 1)

        # draw control blob
        self.canvas.coords(self.cimg, event.x, event.y)

        # draw tracers
        self.canvas.create_oval(x1, y1, x2, y2, fill="Black")

        if self.logging:
            print(f'mouse 1 x={event.x}, y={event.y}')

        if self.arm.draw_mode_status:
            # move arm using blue dot if selected
            self.arm.executeMove([event.x, event.y])

    def shift_press_on(self, event):
        print('hello shift', event)
        self.pen_offset = False
        if self.arm.draw_mode_status:
            self.arm.led_red()

    def shift_press_off(self, event):
        print('hello shift' ,event)
        self.pen_offset = True
        if self.arm.draw_mode_status:
            self.arm.led_blue()

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
        # LED's ready for arm
        self.arm.led_green()

        # take arm out of draw mode
        self.arm.draw_mode_status = False
        self.arm.first_draw_move = True
        self.arm.pen_drawing_status = False

        # go and wait
        self.arm.home()

    def pen_lift(self):
        self.arm.move_joint_relative_speed(4, -5, 20)

    def pen_down(self):
        self.arm.move_joint_relative_speed(4, 5, 20)

    def waiting_pos(self):
        # LED's ready for arm
        self.arm.led_green()

        # wait in draw mode
        self.arm.draw_mode_status = True
        self.arm.first_draw_move = True
        self.arm.pen_drawing_status = False

        # go and wait
        self.arm.wait_ready()

    def draw_ready_pos_draw(self):
        # LED's ready fpr drawing
        self.arm.led_blue()

        # get arm into draw mode
        self.arm.draw_mode_status = True
        self.arm.first_draw_move = True
        self.arm.pen_drawing_status = False

        # put blue dot in centre of screen (draw ready pos)
        self.canvas.coords(self.cimg, 300, 450)

        # goto position
        self.arm.draw_ready()



    def open_claw(self):
        self.arm.move_joint_relative_speed(5, -140, 20)

    def close_claw(self):
        self.arm.move_joint_relative_speed(5, 140, 20)

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
