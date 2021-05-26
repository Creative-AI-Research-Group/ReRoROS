"""
Motor class intialises the serve-client then manages all movement comms
direct to the Hitatchi
Methods are:
cmd() = sends a movement instruction
set() = sets parameters such as vel speed
wheel_left/_right() = addresses an individual wheel
checksum() = calculates the end checksum
write_cmd() = sends command to server

"""

from time import sleep
from comms import Comms

class Motor(Comms):
    def __init__(self):
        super().__init__()

        # define all start-up code sequences (inherited from Comms class)
        # b"\xFA\xFB\x03\x00\x00\x00", b"\xFA\xFB\x03\x01\x00\x01", b"\xFA\xFB\x03\x02\x00\x02"
        init_string = [self.HEADER1, self.HEADER2, self.SHORTCOUNT, self.SYNC0, 0, 0], \
                      [self.HEADER1, self.HEADER2, self.SHORTCOUNT, self.SYNC1, 0, 1], \
                      [self.HEADER1, self.HEADER2, self.SHORTCOUNT, self.SYNC2, 0, 2]

        # 2. Initialise sequence
        # sets up server connection on pg37
        # and send motors ON cmd
        # 1. #' Open ArRobot Connection #code 40, +, 1 (IOconfig request = once)
        # 2. #code 18, + (request config SIP
        # 3. #code 50, + (set baud rate to setting 2 )  #pulse
        # opening_codes = b"\xFA\xFB\x06\x01\x3B\x01\x00\x02\x3B\xFA\xFB\x06\x28\x3B\x02\x00\x2a\x3B",
        #                      b"\xFA\xFB\x06\x12\x3B\x01\x00\x13\x3B",
        #                      b"\xFA\xFB\x06\x32\x3B\x02\x00\x34\x3B\xFA\xFB\x03\x00\x00\x00"
        opening_codes = [self.HEADER1, self.HEADER2, self.BYTECOUNT, self.OPEN, self.POSITIVE, 1, 0, 2, 59,
                         self.HEADER1, self.HEADER2, self.BYTECOUNT, self.IOREQUEST, self.POSITIVE, 1, 0, 41, 59,
                         self.HEADER1, self.HEADER2, self.BYTECOUNT, self.ENCODER, self.POSITIVE, 0, 0, 19, 59], \
                        [self.HEADER1, self.HEADER2, self.BYTECOUNT, self.CONFIG, self.POSITIVE, 1, 0, 19, 59], \
                        [self.HEADER1, self.HEADER2, self.BYTECOUNT, self.HOSTBAUD, self.POSITIVE, 2, 0, 52, 59,
                         self.HEADER1, self.HEADER2, self.SHORTCOUNT, self.SYNC0, 0, 0]

        # 3. initialises all the motor params
        # fa fb 06 25 3b 02 00 27 3b = init gripper IO stop
        # A: #code 62, +, 1 (????not in manual … pulse off? No further pulses)
        # #code 4 = Enable robot's motors
        #
        # B: #code 06, +, && (set max vel to 500mm/sec)
        # #code 05, +, 2c 01 (set trans accelerator to 300mm/s/s)
        # #code 05, -, 2c 01 (set trans decelerations to 300mm/s/s
        # #code 11, +, 0 (translate vel to mm/sec fwd
        # #code 10, +, 64 (set rotate vel to 64mm/s
        # #code 23, + 64 (rotational accel to 100
        # #code 23, -, 64 (ditto anti-clockwise
        # motor_codes = b"\xFA\xFB\x06\x3E\x3B\x01\x00\x3F\x3B\xFA\xFB\x06\x04\x3B\x01\x00\x05\x3B",
        # b"\xFA\xFB\x06\x06\x3B\xF4\x01\xFA\x3C\xFA\xFB\x06\x05\x3B\x2C\x01\x31\x3C
        # \xFA\xFB\x06\x05\x1B\x2C\x01\x31\x1C\xFA\xFB\x06\x0B\x3B\x00\x00\x0B\x3B
        # \xFA\xFB\x06\x0A\x3B\x64\x00\x6E\x3B\
        # xFA\xFB\x06\x17\x3B\x64\x00\x7B\x3B\
        # xFA\xFB\x06\x17\x1B\x64\x00\x7B\x1B"
        motor_codes = [self.HEADER1, self.HEADER2, self.BYTECOUNT, self.GRIPPERIOREQUEST, self.POSITIVE, 0, 0, 37, 59, # new gripper insert
                       self.HEADER1, self.HEADER2, self.BYTECOUNT, 62, self.POSITIVE, 1, 0, 63, 59, # dont know code 62
                       self.HEADER1, self.HEADER2, self.BYTECOUNT, self.ENABLE, self.POSITIVE, 1, 0, 5, 59], \
                      [self.HEADER1, self.HEADER2, self.BYTECOUNT, self.SETV, self.POSITIVE, 244, 1, 250, 60,
                       self.HEADER1, self.HEADER2, self.BYTECOUNT, self.SETA, self.POSITIVE, 44, 1, 49, 60,
                       self.HEADER1, self.HEADER2, self.BYTECOUNT, self.SETA, self.NEGATIVE, 44, 1, 49, 28,
                       self.HEADER1, self.HEADER2, self.BYTECOUNT, self.VEL, self.POSITIVE, 0, 0, 11, 59,
                       self.HEADER1, self.HEADER2, self.BYTECOUNT, self.SETRV, self.POSITIVE, 100, 0, 110, 59,
                       self.HEADER1, self.HEADER2, self.BYTECOUNT, self.SETRA, self.POSITIVE, 100, 0, 123, 59,
                       self.HEADER1, self.HEADER2, self.BYTECOUNT, self.SETRA, self.NEGATIVE, 100, 0, 123, 27]

        # start up sequence
        print('1.....Sending three start-up codes SYNC0, SYNC1 and SYNC2')
        # send the 3 init codes to initialise connection
        for i, inits in enumerate(init_string):
            msg_match = False

            # send the data
            print(f'sending SYNC{i}: {inits} to robot')
            self.write(inits)

            # check if returning message is same as send
            while msg_match == False and i < 2: # the last message return the id of the robot
                # read server and check if a match
                msg_match = self.sipps_match(inits)
                sleep(0.1)  # wait for a bit

        print('2.....Sending open server-client connection and initialising conditions')
        for codes in opening_codes:
            msg_match = False
            self.write(codes)

            # check if returning message is same as send
            while msg_match == False:
                msg_match = self.sipps_match(codes)
                sleep(0.1)  # wait for a bit

        print('3.......Sending motor setup and params')
        for motors in motor_codes:
            msg_match = False
            self.write(motors)

            # check if returning message is same as send
            while msg_match == False:
                msg_match = self.sipps_match(motors)
                sleep(0.1)  # wait for a bit

        # send a pulse heartbeat to maintain conns
        self.pulse()

        for i in range (5):
            print(f'REROBOT READY ... {5 - i}\n\n\t\t')
            sleep(0.5)

    def sipps_match(self, send_msg):
        rtn_msg = self.read()  # read server info packets as incoming messages
        print('listening')
        decode = list(rtn_msg)
        if send_msg == decode:
            print(f'return message is  ... {rtn_msg}')
            return True

    # builds and sends a movement instruction
    # 1st creates checksum from bytes after byte-count
    def cmd(self, cmd, value, wheel=None):
        command_array = [cmd] # adds command code
        if value > 0: # + or - integer to follow
            command_array.append(self.POSITIVE)
        else:
            command_array.append(self.NEGATIVE)
            value *= -1

        if wheel == 'right':
            command_array.append(0)  # 2 byte integer Least 1st
            command_array.append(value)  # 2 byte integer Least 1st = right
        else:
            command_array.append(value) # 2 byte integer Least 1st
            command_array.append(0) # 2 byte integer Least 1st

        # calculate checksum
        checksum = self.checksum(command_array)
        command_array += checksum # add it to end of arra

        # finally adds header x2 & bytecount (which is always 6) to the front
        command_array[:0] = [self.HEADER1, self.HEADER2, self.BYTECOUNT]
        self.write(command_array)

    def set(self):
        # sets parameters such as max vel speed
        # SETRV limit (cmd 10)= heading turn
        # SETV speed (cmd 6)= Move speed
        pass

    def stop(self):
        # self.send_cmd(b'\xFA\xFB\x03\x1D\x00\x1D')   # all stop command
        self.write(self.STOP_COMMAND)   # all stop command

    def checksum(self, code):
        # TODO will need to amend when large number come through
        #  e.g. set vel speed as these will use both bytes for the value
        ls_a = code[::2]
        ls_b = code[1::2]
        cs_a = sum(ls_a)
        cs_b = sum(ls_b)
        return [cs_a, cs_b]

    # Set independent wheel velocities;
    #  bits 0-7 for right wheel,
    #  bits 8-15 for left wheel; in 20mm/sec
    def left(self, speed):
        self.cmd(self.VEL2, speed, 'left')

    def right(self, speed):
        self.cmd(self.VEL2, speed, 'right')

    def terminate(self):
        print ('Closing down all connections')
        # close_down_code = b"\xFA\xFB\x03\x02\x00\x02"
        self.write(self.STOP_COMMAND)
        self.close_sequence(self.CLOSE_DOWN_CODE)
