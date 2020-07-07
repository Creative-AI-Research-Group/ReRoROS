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

class Comms():
    L_VEL = 0
    R_VEL = 0
    THPOS = 0
    BATTERY = 0
    COMPASS = 0

    def __init__(self):
        print(f'initialise connection to host\nopens up the serial port as an object called "ser"{id}')

        self.ser = serial.Serial(port='/dev/ttyUSB0',
            baudrate=9600,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.EIGHTBITS,
            timeout=1
            )
        self.ser.isOpen()

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

    # def sip_request(self):
    #     # todo not responding to SIP
    #     # self.write([250, 251, 6, 40, 59, 1, 0, 41, 59]) # request 1 SIP request
    #     sip = self.ser.read(255)
    #     print(f'READING = {sip}')
    #     self.flush()
    #     return sip

    def decode(self, msg):
        global L_VEL, R_VEL, THPOS, BATTERY
        decode_array = list(msg)
        for i, bytes in enumerate(decode_array):
            if bytes[i] == 250 and bytes[i+1] == 251:
                L_VEL = decode_array[i+9]
                R_VEL = decode_array[i+10]
                THPOS = decode_array[i+8]
                BATTERY = decode_array[i+11]

    def close_sequence(self, terminate_code):
        """closes down server
        robot
        and serial port"""
        terminate_code = bytearray(terminate_code)
        self.ser.write(terminate_code)
        print ('Robot closing down')
        self.ser.close()
        print("All closed - see ya!!")

    def pulse(self):
        self.ser.write(b"\xFA\xFB\x03\x00\x00\x00")  # writes a pulse
