#
#   arm.py
#   class for Lynxmotion LSS robot arm
#   (c) Craig Vear
#   cvear@dmu.ac.uk
#   24/03/2021
#
"""This class is a handler and interfaces between the GUI and the LSS clasess supplied by Lynxmotion.
It translates all the basic commands for drawing arm into LSS-class based code.
"""

# Import required libraries
import random
import platform
import numpy as np
from math import atan2, sqrt, cos, sin, acos, pi, copysign
import time

# Import LSS library
import lss
import lss_const as lssc

class Arm:
    def __init__(self):
        print('init serial comms to LynxMotion board')
        print('Init robot arm')

        # Open constants
        if platform.system() == 'Windows':
            CST_LSS_Port = "COM3"
        elif platform.system() == 'Linux':
            CST_LSS_Port = "/dev/ttyUSB0"
        else:
            CST_LSS_Port = "/dev/cu.usbserial-AG4UPOC0" # Mac

        CST_LSS_Baud = lssc.LSS_DefaultBaud
        self.CST_ANGLE_MIN = -90
        self.CST_ANGLE_MAX = 90

        # Create and open a serial port
        lss.initBus(CST_LSS_Port, CST_LSS_Baud)
        print('port opened')

        # Set standard positions - ABSOLUTES
        self.sleep_position_abs = [0, -900, 900, 0, 0]  # absolute arm position for hold
        self.wait_ready_abs = [0, -900, 400, 600, 0]  # waits
        self.draw_position_abs = [0, -90, 60, 840, 0]

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

        # Set stiffness (-4 : 4 = floppy joints which means less jitter at stop)
        self.allMotors.setAngularHoldingStiffness(0)

        # set max speed
        self.allMotors.setMaxSpeed(40)
        self.base.setMaxSpeed(40)

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

        # toggle checking arrived and issue management
        self.checking = False

        # draw mode vars
        # safe use of drawing canvas
        self.draw_mode_status = False

        # is this the 1st move?
        self.first_draw_move = True

        # is Shift down? (drawing not moving arm)
        self.pen_drawing_status = False

        # pen height from end of gripper
        self.pen_height = 3  # inch

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
    # gets into waiting position
    def wait_ready(self):
        # allow spamming of positions to joint OFF
        self.shoulder.setMotionControlEnabled(1)
        self.elbow.setMotionControlEnabled(1)

        for i, joint in enumerate(self.lss_list):
            joint.moveSpeed(self.wait_ready_abs[i], 30)

    # gets into drawing position
    def draw_ready(self):
        # allow spamming of positions to joint OFF
        self.shoulder.setMotionControlEnabled(1)
        self.elbow.setMotionControlEnabled(1)

        for i, joint in enumerate(self.lss_list):
            joint.moveSpeed(self.draw_position_abs[i], 30)

    # opens claw for pen
    def open_claw(self):
        self.move_arm_relative_speed(self.open_pen_rel, 50)

    # closes claw for pen
    def close_claw(self):
        self.move_arm_relative_speed(self.hold_pen_rel, 50)

    # returns arm to home/ sleep position
    def home(self):
        # allow spamming of positions to joint OFF
        self.shoulder.setMotionControlEnabled(1)
        self.elbow.setMotionControlEnabled(1)

        for i, joint in enumerate(self.lss_list):
            joint.moveSpeed(self.sleep_position_abs[i], 50)

    # returns arm to home/ sleep position and holds
    def home_hold(self):
        for i, joint in enumerate(self.lss_list):
            joint.moveSpeed(self.sleep_position_abs[i], 50)
        self.hold()

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
    # todo look at arm_motion solution for 'arrived'
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

#########
#
# The following code is adapted from
# https://github.com/Robotics-Technology/Chess-Robot/blob/master/ArmControl.py
# sincere thanks to Geraldine BC for allowing me to use her original code
#
#########

    # checks if results are in range
    def checkConstraints(self, value, min, max):
        if (value < min):
            value = min
        if (value > max):
            value = max
        return value

    # calc rescale due to page size
    def scale_xy(self, raw_xy):
        """x,y (top left = 0, 0) is opposite right corner of A4 page
                lss1_x_min = 290 - 63
                lss1_x_max = -73 - -420
                lss2 = 590 - -470
                lss3 = -740 - -520
                lss4 = 1000 - 870

                NewValue = (((OldValue - OldMin) * (NewMax - NewMin)) / (OldMax - OldMin)) + NewMin
                        x = params["baseradius"] + params["cbFrame"] + params["sqSize"] * sqNumber - params["sqSize"]*1/2
                        y = params["sqSize"] * sqletter - copysign(params["sqSize"]*1/2,sqletter)
                        {"baseradius": 1.77, "cbFrame": 0.62, "sqSize": 1.09, "cbHeight": 0.79, "pieceHeight": 1.97}
        """

        # params from canvas
        x_old_min = 0
        x_old_max = 750
        y_old_min = 0
        y_old_max = 900

        # old calc in inches
        baseradius = 1.77 # radius of LSS base to beginning of chess board
        cbframe = 1 # outer frame of chess board
        sqsize = 1.5 # cb square

        # calc new range based on sqNumber -4 : +4; sqLetter 8 : 1
        x_new_min = baseradius + cbframe + sqsize * -4
        x_new_max = baseradius + cbframe * 4

        y_new_min = sqsize * 8
        y_new_max = sqsize * 1

        # scaling using cb params vs 2D plot from canvas
        # SWAP X & Y round to map on A4
        y = (((raw_xy[0] - x_old_min) * (x_new_max - x_new_min)) / (x_old_max - x_old_min)) + x_new_min
        x = (((raw_xy[1] - y_old_min) * (y_new_max - y_new_min)) / (y_old_max - y_old_min)) + y_new_min

        print('move = ', x, y)
        return [x, y]

    # calcs degrees for IK for each joint
    # Desired positions in x, y, z, gripper aperture
    def LSS_IK(self, targetXYZG):
        # UK centimeters
        # d1 = 10.49  # Bottom to shoulder
        # d2 = 14.25  # Shoulder to elbow
        # d3 = 16.23  # Elbow to wrist
        # d4 = 11.48  # Wrist to end of gripper

        # original US inches
        d1 = 4.13  # Bottom to shoulder
        d2 = 5.61  # Shoulder to elbow
        d3 = 6.39  # Elbow to wrist
        d4 = 4.52  # Wrist to end of gripper

        x0 = targetXYZG[0]
        y0 = targetXYZG[1]
        z0 = targetXYZG[2]
        g0 = targetXYZG[3]

        # Base angle (degrees)
        q1 = atan2(y0, x0) * 180 / pi

        # Radius from the axis of rotation of the base in xy plane
        xyr = sqrt(x0 ** 2 + y0 ** 2)
        print('xyr = ', xyr)

        # Pitch angle for gripper head (was 80)
        q0 = 90

        # Gripper components in xz plane
        lx = d4 * cos(q0 * pi / 180)
        lz = d4 * sin(q0 * pi / 180)

        # Wrist coordinates in xz plane
        x1 = xyr - lx
        z1 = z0 + lz - d1

        # Distance between the shoulder axis and the wrist axis
        h = sqrt(x1 ** 2 + z1 ** 2)
        print('h = ', h)

        a1 = atan2(z1, x1)
        print('a1 = ', a1)

        a2 = acos((d2 ** 2 - d3 ** 2 + h ** 2) / (2 * d2 * h))

        # Shoulder angle (degrees)
        q2 = (a1 + a2) * 180 / pi

        # Elbow angle (degrees)
        a3 = acos((d2 ** 2 + d3 ** 2 - h ** 2) / (2 * d2 * d3))
        q3 = 180 - a3 * 180 / pi

        # Wrist angle (degrees) (add 5 deg because of the wrist-gripper offset)
        q4 = q0 - (q3 - q2) + 6

        #  Add 15 deg because of the shoulder-elbow axis offset
        q2 = q2 + 16

        # Return values Base, Shoulder, Elbow, Wrist, Gripper
        angles_BSEWG = [q1, 90 - q2, q3 - 90, q4, g0]

        # Check constraints
        for i in range(0, 5):
            angles_BSEWG[i] = self.checkConstraints(angles_BSEWG[i], self.CST_ANGLE_MIN, self.CST_ANGLE_MAX)

        return (np.dot(10, angles_BSEWG).astype(int))


    def LSSA_moveMotors(self, angles_BSEWG):
        # If the servos detect a current higher or equal than the value (mA)
        # before reaching the requested positions they will halt and hold
        # self.wrist.moveCH(angles_BSEWG[3], 1000)
        # self.shoulder.moveCH(angles_BSEWG[1], 1600)
        # self.elbow.moveCH(angles_BSEWG[2], 1600)
        # self.base.moveCH(angles_BSEWG[0], 1000)
        # self.gripper.moveCH(angles_BSEWG[4], 500)

        # If the servos detect a current higher or equal than the value (mA)
        # before reaching the requested positions they will halt and hold
        # changed to moveSpeed to control Zen of interaction
        self.wrist.moveSpeed(angles_BSEWG[3], 10)
        self.shoulder.moveSpeed(angles_BSEWG[1], 10)
        self.elbow.moveSpeed(angles_BSEWG[2], 10)
        self.base.moveSpeed(angles_BSEWG[0], 10)
        self.gripper.moveSpeed(angles_BSEWG[4], 10)

        arrived = False
        issue = 0
        i = 0

        # optional checking and issue management
        if self.checking:

            # Check if they reached the requested position
            while arrived == False and issue == 0:
                bStat = self.base.getStatus()
                sStat = self.shoulder.getStatus()
                eStat = self.elbow.getStatus()
                wStat = self.wrist.getStatus()
                gStat = self.gripper.getStatus()

                # If a status is None print message if it continues to be None return issue 1
                if (bStat is None or sStat is None or eStat is None or wStat is None or gStat is None):
                    print("- Unknown status")
                    i = i + 1
                    if (i >= 5):
                        print("- Issue detected")
                        issue = 1
                # If the statuses aren't None check their values
                else:
                    # If a servo is Outside limits, Stuck, Blocked or in Safe Mode before it reaches the requested position reset the servos and return issue 1
                    if (int(bStat) > 6 or int(sStat) > 6 or int(eStat) > 6 or int(wStat) > 6 or int(gStat) > 6):
                        print("- Issue detected")
                        issue = 1
                    # If all the servos are holding positions check if they have arrived
                    elif (int(bStat) == 6 and int(sStat) == 6 and int(eStat) == 6 and int(wStat) == 6 and int(gStat) == 6):
                        bPos = self.base.getPosition()
                        sPos = self.shoulder.getPosition()
                        ePos = self.elbow.getPosition()
                        wPos = self.wrist.getPosition()
                        # If any position is None
                        if (bPos is None or sPos is None or ePos is None or wPos is None):
                            print("- Unknown position")

                        # If they are holding in a different position than the requested one return issue 2
                        elif (abs(int(bPos) - angles_BSEWG[0]) > 20 or abs(int(sPos) - angles_BSEWG[1]) > 50 or abs(
                                int(ePos) - angles_BSEWG[2]) > 50 or abs(int(wPos) - angles_BSEWG[3]) > 20):
                            sStat = self.shoulder.getStatus()
                            eStat = self.elbow.getStatus()

                            # Re-check shoulder and elbow status and positions
                            if (int(sStat) == 6 and int(eStat) == 6):
                                sPos = self.shoulder.getPosition()
                                ePos = self.elbow.getPosition()
                                if (sPos is None or ePos is None):
                                    print("- Unknown position")
                                elif (abs(int(sPos) - angles_BSEWG[1]) > 40 or abs(int(ePos) - angles_BSEWG[2]) > 40):
                                    print("- Obstacle detected")
                                    issue = 2
                        else:
                            print("- Arrived\n")
                            arrived = True

            return arrived

        else:
            return True, 0

    def led_blue(self):
        # change LED state to draw ready
        self.allMotors.setColorLED(lssc.LSS_LED_Cyan)

    def led_red(self):
        # change LED state to pen activated
        self.allMotors.setColorLED(lssc.LSS_LED_Red)

    def led_green(self):
        # change LED state to arm move
        self.allMotors.setColorLED(lssc.LSS_LED_Green)

    def executeMove(self, raw_xy):

        # allow spamming of positions to joint (drawing only)
        self.shoulder.setMotionControlEnabled(0)
        self.elbow.setMotionControlEnabled(0)

        move = self.scale_xy(raw_xy)

        # set z for draw state (pen down or up)
        if self.pen_drawing_status:
            z = self.pen_height
        else:
            z = self.pen_height + 1 # inch

        # move arm to ...
        x, y = move[0], move[1]

        # Calculate position and FPC (steps between positions)

        # 1st draw from draw ready position
        if self.first_draw_move:
            x0, y0 = 0, 0
            self.first_draw_move = False

            distance = sqrt(((x0 - x) ** 2) + ((y0 - y) ** 2))
            fpc = int(distance) + 15
            self.shoulder.setFilterPositionCount(fpc)
            self.elbow.setFilterPositionCount(fpc)

        else:
            # Normal moves
            self.shoulder.setFilterPositionCount(15)
            self.elbow.setFilterPositionCount(15)

        #calc angles and move joints
        angles_BSEWG = self.LSS_IK([x, y, z, 0])

        arrived = self.LSSA_moveMotors(angles_BSEWG)
        # self.askPermision(angles_BSEWG2, arrived2, issue2, homography, cap, selectedCam)

if __name__ == "__main__":
    bot_arm = Arm()
    bot_arm.draw_ready()
    time.sleep(5)
    bot_arm.home()
    time.sleep(5)
    bot_arm.terminate()