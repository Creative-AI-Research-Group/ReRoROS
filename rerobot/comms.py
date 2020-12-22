"""this class handles all comms with Hitatchi controller.
It also parses the Server Information Packages from the robot
and assigns relevent info to a variable.
variables are:
L VEL
R VEL
THPOS
Battery
"""

import serial
import atexit

class Comms:
    # define all major bytes
    HEADER1 = 250
    HEADER2 = 251
    BYTECOUNT = 6  # this may change but so far all basic commands are 6 bytes long
    SHORTCOUNT = 3
    POSITIVE = 59
    NEGATIVE = 27

    # define commands
    SYNC0 = 0
    SYNC1 = 1
    SYNC2 = 2

    PULSE = 0
    OPEN = 1
    CLOSE = 2
    ENABLE = 4
    SETA = 5
    SETV = 6
    MOVE = 8
    ROTATE = 9
    SETRV = 10
    VEL = 11
    CONFIG = 18
    SETRA = 23
    SONAR = 28 # 1=enable, 0=disable all the sonar
    STOP = 29
    VEL2 = 32
    GRIPPER = 33
    IOREQUEST = 40 # Request one (1), a continuous stream (>1), or stop (0) IO SIPs
    HOSTBAUD = 50

    # complex codes
    close_down_code = [HEADER1, HEADER2, SHORTCOUNT, SYNC2, 0, 2]

    # sipp reporting
    L_VEL = 0
    R_VEL = 0
    THPOS = 0
    BATTERY = 0

    def __init__(self):
        print(f'initialise connection to host\n'
              f'opens up the serial port as an object called "ser"{id}')

        self.ser = serial.Serial(port='/dev/ttyUSB0',
            baudrate=9600,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.EIGHTBITS,
            timeout=1
            )
        self.ser.isOpen()

    # header (2 bytes = \xFA\xFB),
    #      byte count (1 byte),
    #      command_num (1 byte 0-255),
    #      arg_type (\x3B, \x1B or \x2B),
    #      arg (n bytes - always 2-byte or string conatinig lgth prefix),
    #      checksum (2 bytes))
    def write(self, msg):
        msg_hx = bytearray(msg)
        print(f'sending hex message: {msg_hx} to {self.ser.port}')
        self.ser.write(msg_hx)

    def flush(self):
        self.ser.flushInput()

    def read(self):
        incoming = self.ser.read(255)
        print (f'READING = {incoming}')
        self.flush()
        return incoming

    def sip_read(self):
        read_data = self.read()
        print(f'return message is {read_data}')
        # self.comms.flush()

        # parse sips
        decode_array = list(read_data)
        for i, bytes in enumerate(decode_array):
            if bytes[i] == self.HEADER1 and bytes[i+1] == self.HEADER2:

                # assign relevant bytes to robots vars
                length_string = list(decode_array[i + 2][0])
                self.TYPE = decode_array[i + 3] #  s = 2 when motors stopped or 3 when robot moving
                self.XPOS = decode_array[i + 4: i + 5]
                self.YPOS = decode_array[i + 6: i + 6]
                self.THPOS = decode_array[i + 8: i + 9]
                self.L_VEL = decode_array[i + 10: i + 11]
                self.R_VEL = decode_array[i + 12: i + 13]
                self.BATTERY = decode_array[i + 14]
                self.BUMPERS = decode_array[i + 15: i + 16]
                self.CONTROL = decode_array[i + 17: i + 18]
                self.FLAGS = decode_array[i + 19: i + 20]
                self.COMPASS = decode_array[i + 21]

                self.GRIP_STATE = decode_array[length_string - 10]
                self.ANPORT = decode_array[length_string - 9]
                self.ANALOG = decode_array[length_string - 8]
                self.DIGIN = decode_array[length_string - 7]
                self.DIGOUT = decode_array[length_string - 6]
                self.BATTERYX10 = decode_array[length_string - 5: length]

    # closes down server robot
    # and serial port
    def close_sequence(self, terminate_code):
        terminate_code = bytearray(terminate_code)
        self.ser.write(terminate_code)
        print ('Robot closing down')
        self.ser.close()
        print("All closed - see ya!!")

    def pulse(self):
        # writes a pulse (as raw Hex for now)
        # self.ser.write(b"\xFA\xFB\x03\x00\x00\x00")
        self.ser.write([self.HEADER1, self.HEADER2, self.SHORTCOUNT, self.SYNC0, 0, 0])
