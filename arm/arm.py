#
#   arm.py
#   class for Lynxmotion LSS robot arm
#   (c) Craig Vear
#   cvear@dmu.ac.uk
#   24/03/2021
#
"""This class is a handler and interfaces between the GUI and the LSS clasess supplied by Lynxmotio.
It translates all the basic commands for drawing arm into LSS-class based code.
"""
# Import required libraries
import time
import random
from pygame import mouse

# Import LSS library
import lss
import lss_const as lssc


class Arm:
    def __init__(self):
        print('init serial comms to LynxMotion board')
        print('Init robot arm')

        # Open constants
        self.CST_LSS_Port = "/dev/cu.usbserial-AG4UPOC05" # Mac platform
        # self.CST_LSS_Port = "/dev/ttyUSB0" # For Linux/Unix platforms
        # self.CST_LSS_Port = "COM230"  # For windows platforms
        self.CST_LSS_Baud = lssc.LSS_DefaultBaud

        # Create and open a serial port
        lss.initBus(self.CST_LSS_Port, self.CST_LSS_Baud)
        print('port opened')

        # Set standard positions - ABSOLUTES
        self.sleep_position_abs = [180, -900, 900, 0, 0]  # absolute arm position for hold
        self.draw_ready_abs = [183, -309, 230, 432, 0]  # waits

        # Set standard positions - RELATIVE
        self.open_pen_rel = [0, 0, 0, 0, -140]  # opens claw to receive pen
        self.hold_pen_rel = [0, 0, 0, 0, 0]  # closes claw for pen


        # define safety params
        self.my_max_speed = 100

        # Create LSS objects
        self.myLSS1 = lss.LSS(1)
        self.myLSS2 = lss.LSS(2)
        self.myLSS3 = lss.LSS(3)
        self.myLSS4 = lss.LSS(4)
        self.myLSS5 = lss.LSS(5)

        # Set safety params (it seems these are ignored by arm OS when using moveSpeed
        self.myLSS1.setMaxSpeed(self.my_max_speed, lssc.LSS_SetConfig)
        self.myLSS2.setMaxSpeed(self.my_max_speed, lssc.LSS_SetConfig)
        self.myLSS3.setMaxSpeed(self.my_max_speed, lssc.LSS_SetConfig)
        self.myLSS4.setMaxSpeed(self.my_max_speed, lssc.LSS_SetConfig)
        self.myLSS5.setMaxSpeed(self.my_max_speed, lssc.LSS_SetConfig)

        # define joint list
        self.lss_list = [self.myLSS1,
                         self.myLSS2,
                         self.myLSS3,
                         self.myLSS4,
                         self.myLSS5]

        self.lss_list_str = ['myLSS1',
                         'myLSS2',
                         'myLSS3',
                         'myLSS4',
                         'myLSS5']

        # define joint dict for current position
        self.joint_dict_pos = {'myLSS1': 0,
                               'myLSS2': 0,
                               'myLSS3': 0,
                               'myLSS4': 0,
                               'myLSS5': 0
                               }

        # define joint dict for next pos
        self.joint_dict_next_pos = {'myLSS1': 0,
                               'myLSS2': 0,
                               'myLSS3': 0,
                               'myLSS4': 0,
                               'myLSS5': 0
                               }

        # Instance params
        self.waiting = False

        # logging
        self.sips_logging = False

    #### lss shared commands ####
    # resets all joints
    def reset_arm(self):
        for joint in self.lss_list:
            joint.reset()

    # all joints limp - safety mode
    def limp_arm(self):
        for joint in self.lss_list:
            joint.limp()

    # locks motors at current pos
    def hold(self):
        for i, joint in enumerate(self.lss_list):
            joint.hold()

    # move arm to abolsute pos or predefined pos
    def move_arm(self, pos):
        for i, joint in enumerate(self.lss_list):
            joint.move(pos)

    # move joint to absolute position
    def move_joint(self, joint, pos):
        joint = self.lss_list[joint]
        joint.move(pos)

    # move arm to relative pos with delta
    def move_arm_relative(self, delta):
        for i, joint in enumerate(self.lss_list):
            joint.moveRelative(delta)

    # move joint to relative pos with delta
    def move_joint_relative(self, joint, delta):
        joint = self.lss_list[joint]
        joint.moveRelative(delta)

    # moves arm to absolute positions or preset, optional speed
    def move_arm_speed(self, pos, speed=None):
        for i, joint in enumerate(self.lss_list):
            joint.moveSpeed(pos[i], speed)

    # moves a joint to absolute position, optional speed
    def move_joint_speed(self, joint, pos, speed=None):
        joint = self.lss_list[joint]
        joint.moveSpeed(pos, speed)

    # moves arm relative to delta, optional speed
    def move_arm_relative_speed(self, delta, speed=None):
        for i, joint in enumerate(self.lss_list):
            joint.moveRelativeSpeed(delta, speed)

    # moves joint relative to delta, optional speed
    def move_joint_relative_speed(self, joint, delta, speed=None):
        joint = self.lss_list[joint]
        joint.moveRelativeSpeed(delta, speed)

    #### drawing specific commands ####
    # gets into drawing position
    def draw_ready(self):
        for i, joint in enumerate(self.lss_list):
            joint.moveSpeed(self.draw_ready_abs[i], 50)

    # opens claw for pen
    def open_claw(self):
        self.move_arm_relative_speed(self.open_pen_rel, 50)

    # closes claw for pen
    def close_claw(self):
        self.move_arm_relative_speed(self.hold_pen_rel, 50)

    # returns arm to home/ sleep position
    def home(self):
        for i, joint in enumerate(self.lss_list):
            joint.move(self.sleep_position_abs[i])

    # returns arm to home/ sleep position and holds
    def home_hold(self):
        for i, joint in enumerate(self.lss_list):
            joint.move(self.sleep_position_abs[i])
        self.hold()

    def drawing(self):
        pass

    # animation functions while waiting
    def waiting_dance(self):
        while self.waiting:
            # get random vars
            rnd_joint = random.randrange(5) + 1
            rnd_delta = random.randrange(10)
            rnd_speed = random.randrange(20) + 10

            # move joint in dance
            moving_joint = self.lss_list[rnd_joint]
            moving_joint.moveRelativeSpeed(rnd_delta, rnd_speed)

            # while not is_in_posiiton:

    def tracking_human_pencil_while_waiting(self):
        pass

    #### telemetry ####
    # reads the sips from LSS and get current position
    def get_positions(self):
        # Get the values from LSS
        if self.sips_logging:
            print("\r\nQuerying LSS...")

        for i, joint in enumerate(self.lss_list):
            pos = joint.getPosition()
            max_s = joint.getMaxSpeed()
            max_s_rpm = joint.getMaxSpeedRPM()
            if self.sips_logging:
                print(f"Position  {joint} (1/10 deg) = ", str(pos))
                print(f'max speed = {max_s}; max speed RPMM = {max_s_rpm}')

            joint_dict = self.lss_list_str[i]
            self.joint_dict_pos[joint_dict] = pos

    # calcs where nest position of arm should be
    def is_in_position(self, position):
        pos_list = []
        pos_count = 0
        for joint in self.lss_list:
            pos_list.append(joint.getPosition())

        for i, pos in enumerate(position):
           if pos == pos_list[i]:
               pos_count += 1

        if pos_count == 5:
            return True
        else:
            return False


    # Terminate objects
    def terminate(self):
        # reset servos first
        self.reset_arm()

        # Destroy objects
        del self.myLSS1
        del self.myLSS2
        del self.myLSS3
        del self.myLSS4
        del self.myLSS5

        # Destroy the bus
        lss.closeBus()

if __name__ == "__main__":
    bot_arm = Arm()
    bot_arm.draw()
    time.sleep(5)
    bot_arm.home()
    time.sleep(5)
    bot_arm.terminate()