"""
This module provides protocol and packet definitions for communicating with
newer Robotis Dynamixel servos that implement version 2 of the Dynamixel
protocol. In addition to the basic protocol, it also abstracts common sets of
transactions (such as writing new values to control table registers) into simple
servo class methods, so the application does not require knowledge or use of the
underlying protocol directly.
"""

# .py files
from .RobotisDynamixel2Device import *
from .RobotisDynamixel2Protocol import *
from .RobotisDynamixel2ParserGenerator import *
from .RobotisDynamixel2Packet import *
from .RobotisDynamixel2Servo import *
from .RobotisDynamixel2ControlTable import *
