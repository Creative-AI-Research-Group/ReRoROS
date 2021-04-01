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
import platform

# Import LSS library
import lss
import lss_const as lssc
from arm_control import IK_move


class Arm:
    def __init__(self):
        print('init serial comms to LynxMotion board')
        print('Init robot arm')

        # Open constants
        if platform.system() == 'Windows':
            port = "COM3"
        elif platform.system() == 'Linux':
            port = "/dev/ttyUSB0"
        else:
            self.CST_LSS_Port = "/dev/cu.usbserial-AG4UPOC0" # Mac

        self.CST_LSS_Baud = lssc.LSS_DefaultBaud
        self.CST_ANGLE_MIN = -90
        self.CST_ANGLE_MAX = 90

        # Create and open a serial port
        lss.initBus(self.CST_LSS_Port, self.CST_LSS_Baud)
        print('port opened')

        # Set standard positions - ABSOLUTES
        self.sleep_position_abs = [0, -900, 900, 0, 0]  # absolute arm position for hold
        self.draw_ready_abs = [0, -350, 450, 0, 0]  # waits
        self.draw_in_position = [0, -20, 100, 700, 0]

        # Set standard positions - RELATIVE
        self.open_pen_rel = [0, 0, 0, 0, -140]  # opens claw to receive pen
        self.hold_pen_rel = [0, 0, 0, 0, 0]  # closes claw for pen

        # Create LSS objects
        self.base = lss.LSS(1)
        self.shoulder = lss.LSS(2)
        self.elbow = lss.LSS(3)
        self.wrist = lss.LSS(4)
        self.gripper = lss.LSS(5)
        self.allMotors = lss.LSS(254)

        # Instantiate an IK object for complex arm moves
        self.IK = IK_move(self.base, self.shoulder, self.elbow, self.wrist, self.gripper, self.allMotors)

        # Set safety params (it seems these are ignored by arm OS when using moveSpeed
        self.allMotors.setAngularHoldingStiffness(0)
        self.allMotors.setMaxSpeed(100)
        self.base.setMaxSpeed(60)
        self.shoulder.setMotionControlEnabled(0)
        self.elbow.setMotionControlEnabled(0)

        # define joint list
        self.lss_list = [self.base,
                         self.shoulder,
                         self.elbow,
                         self.wrist,
                         self.gripper]

        self.lss_list_str = ['base',
                         'shoulder',
                         'elbow',
                         'wrist',
                         'gripper']

        # define joint dict for current position
        self.joint_dict = {'base': {'pos': 0, 'speed': 0, 'load': 0},
                               'shoulder': {'pos': 0, 'speed': 0, 'load': 0},
                               'elbow': {'pos': 0, 'speed': 0, 'load': 0},
                               'wrist': {'pos': 0, 'speed': 0, 'load': 0},
                               'gripper': {'pos': 0, 'speed': 0, 'load': 0}
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

    # move arm to absolute pos or predefined pos
    def move_arm(self, pos):
        for i, joint in enumerate(self.lss_list):
            joint.move(pos[i])

    # move joint to absolute position
    def move_joint(self, joint, pos):
        joint = self.lss_list[joint-1]
        joint.move(pos)

    # move arm to relative pos with delta
    def move_arm_relative(self, delta):
        for i, joint in enumerate(self.lss_list):
            joint.moveRelative(delta[i])

    # move joint to relative pos with delta
    def move_joint_relative(self, joint, delta):
        joint = self.lss_list[joint-1]
        joint.moveRelative(delta)

    # moves arm to absolute positions or preset, optional speed
    def move_arm_speed(self, pos, speed=None):
        for i, joint in enumerate(self.lss_list):
            joint.moveSpeed(pos[i], speed)

    # moves a joint to absolute position, optional speed
    def move_joint_speed(self, joint, pos, speed=None):
        joint = self.lss_list[joint-1]
        joint.moveSpeed(pos, speed)

    # moves arm relative to delta, optional speed
    def move_arm_relative_speed(self, delta, speed=None):
        for i, joint in enumerate(self.lss_list):
            joint.moveRelativeSpeed(delta[i], speed)

    # moves joint relative to delta, optional speed
    def move_joint_relative_speed(self, joint, delta, speed=None):
        joint = self.lss_list[joint-1]
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
            joint.moveSpeed(self.sleep_position_abs[i], 50)

    # returns arm to home/ sleep position and holds
    def home_hold(self):
        for i, joint in enumerate(self.lss_list):
            joint.moveSpeed(self.sleep_position_abs[i], 50)
        self.hold()

    def draw(self):
        for i, joint in enumerate(self.lss_list):
            joint.moveSpeed(self.draw_in_position[i], 20)


    # animation functions while waiting
    # todo
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

    # todo
    def tracking_human_pencil_while_waiting(self):
        pass

    #### telemetry ####
    # reads the sips from LSS and get current position
    def get_telemetry(self):
        # Get the values from LSS
        if self.sips_logging:
            print("\r\nQuerying LSS...")

        for i, joint in enumerate(self.lss_list):
            pos = joint.getPosition()
            load = joint.getCurrent()
            speed = joint.getSpeed()
            if self.sips_logging:
                print(f"Position  {joint} (1/10 deg) = ", str(pos))
                print(f'speed = {speed}; load/current = {load}')

            joint_dict = self.lss_list_str[i]
            self.joint_dict[joint_dict]['pos'] = pos
            self.joint_dict[joint_dict]['speed'] = speed
            self.joint_dict[joint_dict]['load'] = load

    # calcs where next position of arm should be
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
        del self.base
        del self.shoulder
        del self.elbow
        del self.wrist
        del self.gripper

        # Destroy the bus
        lss.closeBus()

if __name__ == "__main__":
    bot_arm = Arm()
    bot_arm.draw_ready()
    time.sleep(5)
    bot_arm.home()
    time.sleep(5)
    bot_arm.terminate()