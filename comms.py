"""this class handles all comms with Hitatchi controller.
It also parses the Server Information Packages from the robot
and assigns relevent info to a variable.
"""

import serial
from time import sleep

class Comms:
    # Full codes and info:
    # https://www.manualslib.com/manual/130418/Pioneer-2-Peoplebot.html

    # define all major bytes
    HEADER1 = 250
    HEADER2 = 251
    BYTECOUNT = 6  # this may change but so far all basic commands are 6 bytes long
    SHORTCOUNT = 3
    POSITIVE = 59
    NEGATIVE = 27

    # Before Client Connection
    SYNC0 = 0
    SYNC1 = 1
    SYNC2 = 2

    # After Established Connection
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
    HEAD = 12
    DHEAD = 13
    CONFIG = 18
    ENCODER = 19
    RVEL = 21
    SETRA = 23
    SONAR = 28 # 1=enable, 0=disable all the sonar
    STOP = 29
    # Set independent wheel velocities; bits 0-7 for right
    # wheel, bits 8-15 for left wheel; in 20mm/sec
    # increments.
    VEL2 = 32
    GRIPPER = 33
    IOREQUEST = 40 # Request one (1), a continuous stream (>1), or stop (0) IO SIPs
    BUMP_STALL = 44
    HOSTBAUD = 50
    E_STOP = 55

    # complex codes
    CLOSE_DOWN_CODE = [HEADER1, HEADER2, SHORTCOUNT, SYNC2, 0, 2]
    HEARTBEAT = [HEADER1, HEADER2, SHORTCOUNT, SYNC0, 0, 0]
    STOP_COMMAND = [HEADER1, HEADER2, SHORTCOUNT, STOP, 00, 29]
    SIP_REQUEST = [HEADER1, HEADER2, BYTECOUNT, ENCODER, POSITIVE, 1, 20, 59]

    # UI reporting variables from SIPPS
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

    # writes to server
    def write(self, msg):
        msg_hx = bytearray(msg)
        print(f'sending hex message: {msg_hx} to {self.ser.port}')
        self.ser.write(msg_hx)

    # fluch buffer
    def flush(self):
        self.ser.flushInput()

    # read from server buffer
    def read(self):
        # Read incoming SIP
        incoming = self.ser.read(255)
        print (f'READING = {incoming}')
        self.flush()
        return incoming

    # parse SIPPS codes
    def sip_read(self):
        # Send ENCODE SIP request (might need IO SIP request!!)
        self.write(self.SIP_REQUEST)

        # Wait a tick
        sleep(0.01)

        # Read incoming SIP
        read_data = self.read()
        print(f'return message is {read_data}')

        # parse sips
        decode_array = list(read_data)
        for i, bytes in enumerate(decode_array):
            if bytes == self.HEADER1 and decode_array[i+1] == self.HEADER2:

                # assign relevant bytes to robots vars
                length_string = decode_array[i + 2]
                self.TYPE = decode_array[i + 3]
                self.XPOS = decode_array[i + 4: i + 5]
                self.YPOS = decode_array[i + 6: i + 7]
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
                self.BATTERYX10 = decode_array[length_string - 5: length_string - 4]

    # closes down server robot and serial port
    def close_sequence(self, terminate_code):
        terminate_code = bytearray(terminate_code)
        self.ser.write(terminate_code)
        print ('Robot closing down')
        self.ser.close()
        print("All closed - see ya!!")

    # Heartbeat pulse
    def pulse(self):
        # writes a pulse (as raw Hex for now)
        # self.ser.write(b"\xFA\xFB\x03\x00\x00\x00")
        self.ser.write(self.HEARTBEAT)
