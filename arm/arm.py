#
#   tangle.py
#   cover / illustration for PbR handbook
#   (c) Fabrizio Augusto Poltronieri
#   fabrizio.poltronieri@dmu.ac.uk
#   22/03/2021
#

# Import required libraries
import time
import random
from pygame import mouse

# Import LSS library
import lss
import lss_const as lssc


class Arm:
    print('init serial comms to LynxMotion board')

    # Open constants
    CST_LSS_Port = "/dev/cu.usbserial-AG4UPOC05"
    CST_LSS_Baud = lssc.LSS_DefaultBaud

    # Create and open a serial port
    lss.initBus(CST_LSS_Port, CST_LSS_Baud)
    print('port opened')

    # Set standard positions - ABSOLUTES
    sleep_position_abs = [180, -900, 900, 0, 0]  # absolute arm position for hold
    draw_ready_abs = [183, -309, 230, 432, 0]  # waits

    # Set standard positions - RELATIVE
    open_pen_rel = [0, 0, 0, 0, -140]  # opens claw to recieve pen
    hold_pen_rel = [180, -900, 900, 0, 0]  # closes claw for pen



    def __init__(self):
        print ('Init robot arm')
        # define safety params
        self.my_max_speed = 1

        # Create LSS objects
        self.myLSS1 = lss.LSS(1)
        self.myLSS2 = lss.LSS(2)
        self.myLSS3 = lss.LSS(3)
        self.myLSS4 = lss.LSS(4)
        self.myLSS5 = lss.LSS(5)

        # Set safety params
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

        # Instance params
        self.waiting = False

    def waiting_dance(self):
        while self.waiting:
            # get random vars
            rnd_joint = random.randrange(5) + 1
            rnd_delta = random.randrange(10)
            rnd_speed = random.randrange(20) + 10

            # move joint in dance
            moving_joint = self.lss_list[rnd_joint]
            moving_joint.moveRelative(rnd_delta, rnd_speed)

            # while not is_in_posiiton:


    def drawing(self):
        pass

    def draw(self):
        for i, joint in enumerate(self.lss_list):
            joint.moveSpeed(self.draw_ready_abs[i], 100)

    def home(self):
        for i, joint in enumerate(self.lss_list):
            joint.moveSpeed(self.sleep_position_abs[i], 100)

    def get_positions(self):
        # Get the values from LSS
        print("\r\nQuerying LSS...")

        for joint in self.lss_list:
            pos = joint.getPosition()
            max_s = joint.getMaxSpeed()
            max_s_rpm = joint.getMaxSpeedRPM()
            print(f"Position  {joint} (1/10 deg) = ", str(pos))
            print(f'max speed = {max_s}; max speed RPMM = {max_s_rpm}')

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

    def mouse_position(self):
        pos = pygame.mouse.get_pos()

    def move_parse(self):
        pass

    def reset_arm(self):
        self.myLSS1.reset()
        self.myLSS2.reset()
        self.myLSS3.reset()
        self.myLSS4.reset()
        self.myLSS5.reset()

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