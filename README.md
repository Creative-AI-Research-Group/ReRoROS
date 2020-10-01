# Recycled Robot Operating System v1.1.3
## Created by Craig Vear and Dmitriy Dubovitskiy

This is a basic operating system for a recycled robot based on the Pioneer series of robots e.g. Pioneer 3 and Peoplebot.

The original onboard computer from the Pioneer machines were replaced with Jetson Nano's. These were connected to the Hitachi driver processors using a serial connection via the Jetson's USB.

The operating system was wrote in Python as an expandable, easily modified system for basic motion and server reporting from the internal ARIA system.

## Problem
The Creative AI research group inherited a selection of old Pioneer robots as part of the Recycled Robot Orchestra project. The original Linux onboard computer and Pioneer operating system (P2OS) was not capable of supporting with the machine learning and AI programming at the heart of the Recycled Robot Orchestra.

## Solution
We replaced the original onboard computer with a Jetson Nano, and built a bespoke OS that communicates with the robot's client/server architecture using the basic commands required by the Recycled Robot Orchestra. 

The OS is built on 4 layers of interpretation and translation from human-focused GUI to raw Hex communications. These layers are:
- basic_motion.py = simple GUI with basic functions and server information packets (SIPS) reporting
- rerobot.py = this class is a handler and interfaces between the GUI and the motor clasess.
It translates all the basic commands into motor-class based code.
    Commands are:
    move - forward backward
    rvel - revolve
    head - goto compass bearing
    stop - stop
    left - move left wheel only
    right - move right wheel only
- motor.py = Motor() class intialises the serve-client then manages all movement comms
direct to the Hitatchi
    Methods are:
    cmd() = sends a movement instruction
    set() = sets parameters such as vel speed
    wheel_left/_right() = addresses an individual wheel
    checksum() = calculates the end checksum
    write_cmd() = sends command to server
    read() = reads SIP streams 
- comms.py = this class handles all comms with Hitatchi controller.
It also parses the Server Information Packages from the robot
and assigns relevent info to a variable.
    variables are:
    L VEL
    R VEL
    THPOS
    Battery
    
