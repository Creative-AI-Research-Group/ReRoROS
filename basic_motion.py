# -*- coding: utf-8 -*-

"""
workon robot
list ports
FIX PERMISSIONS - sudo chmod 666 /dev/ttyUSB0
cd python
cd ReRoRos_v1
python basic_motion.py
"""

from time import sleep
from threading import Thread
from rerobot.rerobot import Robot
from rerobot.comms import Comms
import tkinter as tk
import rerobot.config as config

class GUI(tk.Frame):
    """ GUI & main """

    def __init__(self, gui_window):
        # 1. instantiates a comms link to SIPS and ReRobot
        print('1. setting up comms to the robot')
        self.sips_comms = Comms()
        input("Is the robot ready?")  # temp fix until flag sorted

        self.robot = Robot()
        input("Is the robot ready?")  # temp fix until flag sorted

        """ Initialize the Frame"""
        tk.Frame.__init__(self, gui_window)
        self.grid()
        self.rowconfigure([0, 1, 2, 3, 4], minsize=100, weight=1)
        self.columnconfigure([0, 1, 2, 3, 4], minsize=75, weight=1)

        self.create_widgets()
        self.create_sips()
        self.updater()

    def create_widgets(self):
        """create the interactive buttons"""
        btn_forward = tk.Button(master=self, text="forward", command=l_bot.step_forward, bg="green")
        btn_forward.grid(row=0, column=1, sticky="nsew")

        btn_backward = tk.Button(master=self, text="backward", command=l_bot.step_backward, bg="green")
        btn_backward.grid(row=2, column=1, sticky="nsew")

        btn_rvel_left = tk.Button(master=self, text="left", command=l_bot.step_left, bg="green")
        btn_rvel_left.grid(row=1, column=0, sticky="nsew")

        btn_stop = tk.Button(master=self, text="STOP", command=l_bot.stop, bg="red")
        btn_stop.grid(row=1, column=1, sticky="nsew")

        btn_rvel_right = tk.Button(master=self, text="right", command=l_bot.step_right, bg="green")
        btn_rvel_right.grid(row=1, column=2, sticky="nsew")

        btn_quit = tk.Button(master=self, text="QUIT", command=self.terminate, bg="red")
        btn_quit.grid(row=2, column=2, sticky="nsew")

    def create_sips(self):

        label_battery = tk.Label(master=self, text=f"Battery Level = {config.BATTERY}")
        label_battery.grid(row=0, column=4)

        label_compass = tk.Label(master=self, text=f"Spare = 0")
        label_compass.grid(row=1, column=4)

        label_heading = tk.Label(master=self, text=f"Actual Heading = {config.THPOS}")
        label_heading.grid(row=2, column=4)

        label_left_wheel = tk.Label(master=self, text=f"Left Wheel Vel = {config.L_VEL}")
        label_left_wheel.grid(row=3, column=4)

        label_right_wheel = tk.Label(master=self, text=f"Right Wheel Vel = {config.R_VEL}")
        label_right_wheel.grid(row=4, column=4)

    def update_sip(self):
        #print('updating SIP')
        sip = sips_comms.read()
        sips_comms.decode(sip)

    def updater(self):
        self.update_sip()
        l_bot.pulse()
        self.after(UPDATE_RATE, self.updater)

    def terminate(self):
        global running
        print ('terminator!!!')
        # self.destroy()
        # exit()
        running = False

# local movement controls
    def stop(self):
        robot.stop()

    def step_forward(self):
        robot.move(10)
        sleep(0.5)
        robot.stop()

    def step_backward(self):
        robot.move(-10)
        sleep(0.5)
        robot.stop()

    def step_left(self):
        robot.rvel(20)
        sleep(0.5)
        robot.stop()

    def step_right(self):
        robot.rvel(-20)
        sleep(0.5)
        robot.stop()

    def pulse(self):
        global slow_loop
        if slow_loop < 10:
            slow_loop += 1
        else:
            sips_comms.pulse()  # send pulse code every cycle
            print('sending pulse code')
            slow_loop = 0



""" 
#######################################################
################      MAIN CODE        ################
#######################################################
"""

if __name__ == "__main__":


    # 2. initialise mission control & build GUI
    UPDATE_RATE = 100  # matches baud rate of Pioneer SIP sends e.g. every 100 ms
    slow_loop = UPDATE_RATE / 10  # slows down pulse to 1/10th UPDATE_RATE e.g. sending every second
    print('building GUI')
    gui = tk.Tk()
    gui.title("Robot Control")
    gui.geometry("700x500")
    gooey = GUI(gui)

    # 3. runs it until quit
    running = True
    while running:
        gui.update()

    # 4. close everything down
    robot.terminate()
    sleep(1)
    gui.destroy()
    print ("That's all folks!")
    # exit()




"""ALTERNATIVE COOKBOOK"""
#
# import Tkinter
# import time
# import threading
# import random
# import Queue
#
# class GuiPart:
#     def _ _init_ _(self, master, queue, endCommand):
#         self.queue = queue
#         # Set up the GUI
#         console = Tkinter.Button(master, text='Done', command=endCommand)
#         console.pack(  )
#         # Add more GUI stuff here depending on your specific needs
#
#     def processIncoming(self):
#         """Handle all messages currently in the queue, if any."""
#         while self.queue.qsize(  ):
#             try:
#                 msg = self.queue.get(0)
#                 # Check contents of message and do whatever is needed. As a
#                 # simple test, print it (in real life, you would
#                 # suitably update the GUI's display in a richer fashion).
#                 print msg
#             except Queue.Empty:
#                 # just on general principles, although we don't
#                 # expect this branch to be taken in this case
#                 pass
#
# class ThreadedClient:
#     """
#     Launch the main part of the GUI and the worker thread. periodicCall and
#     endApplication could reside in the GUI part, but putting them here
#     means that you have all the thread controls in a single place.
#     """
#     def _ _init_ _(self, master):
#         """
#         Start the GUI and the asynchronous threads. We are in the main
#         (original) thread of the application, which will later be used by
#         the GUI as well. We spawn a new thread for the worker (I/O).
#         """
#         self.master = master
#
#         # Create the queue
#         self.queue = Queue.Queue(  )
#
#         # Set up the GUI part
#         self.gui = GuiPart(master, self.queue, self.endApplication)
#
#         # Set up the thread to do asynchronous I/O
#         # More threads can also be created and used, if necessary
#         self.running = 1
#         self.thread1 = threading.Thread(target=self.workerThread1)
#         self.thread1.start(  )
#
#         # Start the periodic call in the GUI to check if the queue contains
#         # anything
#         self.periodicCall(  )
#
#     def periodicCall(self):
#         """
#         Check every 200 ms if there is something new in the queue.
#         """
#         self.gui.processIncoming(  )
#         if not self.running:
#             # This is the brutal stop of the system. You may want to do
#             # some cleanup before actually shutting it down.
#             import sys
#             sys.exit(1)
#         self.master.after(200, self.periodicCall)
#
#     def workerThread1(self):
#         """
#         This is where we handle the asynchronous I/O. For example, it may be
#         a 'select(  )'. One important thing to remember is that the thread has
#         to yield control pretty regularly, by select or otherwise.
#         """
#         while self.running:
#             # To simulate asynchronous I/O, we create a random number at
#             # random intervals. Replace the following two lines with the real
#             # thing.
#             time.sleep(rand.random(  ) * 1.5)
#             msg = rand.random(  )
#             self.queue.put(msg)
#
#     def endApplication(self):
#         self.running = 0
#
# rand = random.Random(  )
# root = Tkinter.Tk(  )
#
# client = ThreadedClient(root)
# root.mainloop(  )
